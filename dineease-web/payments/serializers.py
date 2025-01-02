from rest_framework import serializers
from .models import Order, OrderItem, Payment, Refund, Tax
from core.models import Menu, AddonOption, Restaurant, Promo
from core.serializers import MenuMiniSerializer, UserSerializer, PromoMiniSerializer, RestaurantMiniSerializer, VerificationCodeSerializer
from decimal import Decimal

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'refund_amount', 'refund_date', 'refund_reason', 'refund_status']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = MenuMiniSerializer()

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'price', 'subtotal']

class PaymentSerializer(serializers.ModelSerializer):
    refunds = RefundSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'card_brand',
            'card_last4',
            'payment_method',
            'payment_status',
            'transaction_id',
            'amount_paid',
            'payment_date',
            'payment_gateway',
            'refunds',
        ]
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True)
    restaurant_details = RestaurantMiniSerializer(source='restaurant', read_only=True)
    customer = UserSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    promos = PromoMiniSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'order_type',
            'restaurant_details',
            'items',
            'promos',  # Include attached promos
            'order_total',
            'discount',  # Read-only, dynamically calculated
            'tax_rate',  # Read-only, dynamically calculated
            'tax_amount',  # Read-only, dynamically calculated
            'service_fee',  # Read-only, dynamically calculated
            'service_fee_tax',  # Read-only, dynamically calculated
            'total',  # Read-only, dynamically calculated
            'status',
            'order_time',
            'payment',
        ]
        read_only_fields = [
            'order_total',
            'discount',
            'tax_rate',
            'tax_amount',
            'service_fee',
            'service_fee_tax',
            'total',
        ]

    def get_verification_code(self, obj):
        """
        Retrieve the `code` from the related `VerificationCode` object.
        """
        if obj.verification_code:
            return obj.verification_code.code
        return None


class OrderPreviewSerializer(serializers.Serializer):
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    restaurant_id = serializers.IntegerField()
    promo_codes = serializers.ListField(
        child=serializers.CharField(), required=False, default=[]
    )
    promo_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=[]
    )
    stripe_fee_rate = serializers.DecimalField(
        max_digits=5, decimal_places=4, required=False, default=Decimal("0.029")
    )
    stripe_fixed_fee = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False, default=Decimal("0.30")
    )

    def validate(self, data):
        try:
            data['restaurant'] = Restaurant.objects.get(id=data['restaurant_id'])
        except Restaurant.DoesNotExist:
            raise serializers.ValidationError("Invalid restaurant ID")

        # Validate promos by code or ID (if provided)
        promos = Promo.objects.none()
        if data.get('promo_codes'):
            promos = Promo.objects.filter(code__in=data['promo_codes'], status='active')
        elif data.get('promo_ids'):
            promos = Promo.objects.filter(id__in=data['promo_ids'], status='active')

        data['promos'] = promos  # Allow empty promos
        return data

    def calculate_totals(self):
        """Calculate discounts, tax, service fee, Stripe fees, and final total."""
        order_total = self.validated_data['order_total']
        restaurant = self.validated_data['restaurant']
        promos = self.validated_data['promos']
        stripe_fee_rate = self.validated_data['stripe_fee_rate']
        stripe_fixed_fee = self.validated_data['stripe_fixed_fee']

        tax = Tax.objects.filter(province=restaurant.province, is_active=True).first()
        tax_rate = Decimal(tax.rate) if tax else Decimal(0)

        # Apply promos
        discount = Decimal(0)
        discounted_total = Decimal(order_total)
        for promo in promos:
            if promo.discount_type == 'percentage':
                discount_amount = discounted_total * (Decimal(promo.discount) / Decimal(100))
            elif promo.discount_type == 'fixed':
                discount_amount = Decimal(promo.discount)
            discount_amount = min(discount_amount, discounted_total)
            discounted_total -= discount_amount
            discount += discount_amount

        # Calculate tax and service fees
        tax_amount = discounted_total * (tax_rate / Decimal(100))
        service_fee = Decimal(tax.get_service_fee(discounted_total)) if tax else Decimal(0)
        service_fee_tax = service_fee * (tax_rate / Decimal(100))

        # Calculate total paid by customer
        total = discounted_total + tax_amount + service_fee + service_fee_tax

        # Payment to restaurant before Stripe fee
        restaurant_payment_before_fee = discounted_total - service_fee

        # Calculate Stripe fees (paid by the restaurant)
        stripe_fee = (restaurant_payment_before_fee * stripe_fee_rate) + stripe_fixed_fee

        # Final restaurant payment after Stripe fee
        restaurant_payment = restaurant_payment_before_fee - stripe_fee

        # Platform revenue (total - restaurant payment - service fees)
        platform_revenue = total - restaurant_payment_before_fee - stripe_fee

        return {
            "order_total": round(order_total, 2),
            "discount": round(discount, 2),
            "tax_rate": round(tax_rate, 2),
            "tax_amount": round(tax_amount, 2),
            "service_fee": round(service_fee, 2),
            "service_fee_tax": round(service_fee_tax, 2),
            "stripe_fee": round(stripe_fee, 2),
            "total": round(total, 2),
            "restaurant_payment_before_fee": round(restaurant_payment_before_fee, 2),
            "restaurant_payment": round(restaurant_payment, 2),
            "platform_revenue": round(platform_revenue, 2),
        }