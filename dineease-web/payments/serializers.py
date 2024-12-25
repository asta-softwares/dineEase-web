from rest_framework import serializers
from .models import Order, OrderItem, Payment, Refund, Tax
from core.models import Menu, AddonOption, Restaurant, Promo
from core.serializers import MenuMiniSerializer, UserSerializer, PromoMiniSerializer
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
    restaurant = serializers.StringRelatedField()
    customer = UserSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    promos = PromoMiniSerializer(many=True, read_only=True)  # Use PromoSerializer for detailed info

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'restaurant',
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


class OrderPreviewSerializer(serializers.Serializer):
    order_total = serializers.DecimalField(max_digits=10, decimal_places=2)
    restaurant_id = serializers.IntegerField()
    promo_codes = serializers.ListField(
        child=serializers.CharField(), required=False, default=[]
    )
    promo_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=[]
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
        """Calculate discounts, tax, service fee, and final total."""
        order_total = self.validated_data['order_total']
        restaurant = self.validated_data['restaurant']
        promos = self.validated_data['promos']

        # Fetch tax rate and service fee thresholds
        tax = Tax.objects.filter(province=restaurant.province).first()
        tax_rate = Decimal(tax.rate) if tax else Decimal(0)  # Convert tax_rate to Decimal

        # Debug: Initial values
        print(f"Initial Order Total: {order_total}")
        print(f"Tax Rate: {tax_rate}")

        # Sort promos: percentage discounts first, then fixed discounts
        sorted_promos = sorted(promos, key=lambda promo: promo.discount_type == 'fixed')

        # Apply discounts
        discount = Decimal(0)
        discounted_total = Decimal(order_total)
        for promo in sorted_promos:
            print(f"Applying Promo {promo.id}: {promo.discount_type} - {promo.discount}")

            if promo.discount_type == 'percentage':
                discount_amount = discounted_total * (Decimal(promo.discount) / Decimal(100))
            elif promo.discount_type == 'fixed':
                discount_amount = Decimal(promo.discount)

            # Ensure discount does not exceed remaining total
            discount_amount = min(discount_amount, discounted_total)
            print(f"Calculated Discount: {discount_amount}")

            discounted_total -= discount_amount
            print(f"Remaining Total After Discount: {discounted_total}")

            discount += discount_amount
            print(f"Total Discount So Far: {discount}")

        # Calculate tax and fees
        tax_amount = discounted_total * (tax_rate / Decimal(100))
        service_fee = Decimal(tax.get_service_fee(discounted_total)) if tax else Decimal(0)
        service_fee_tax = service_fee * (tax_rate / Decimal(100))
        total = discounted_total + tax_amount + service_fee + service_fee_tax

        # Debug: Tax and fee calculations
        print(f"Discounted Total: {discounted_total}")
        print(f"Tax Amount: {tax_amount}")
        print(f"Service Fee: {service_fee}")
        print(f"Service Fee Tax: {service_fee_tax}")
        print(f"Final Total: {total}")

        return {
            "order_total": round(order_total, 2),
            "discount": round(discount, 2),
            "tax_rate": round(tax_rate, 2),
            "tax_amount": round(tax_amount, 2),
            "service_fee": round(service_fee, 2),
            "service_fee_tax": round(service_fee_tax, 2),
            "total": round(total, 2)
        }

        # Calculate tax and fees
        tax_amount = discounted_total * (tax_rate / Decimal(100))
        service_fee = Decimal(tax.get_service_fee(discounted_total)) if tax else Decimal(0)
        service_fee_tax = service_fee * (tax_rate / Decimal(100))
        total = discounted_total + tax_amount + service_fee + service_fee_tax

        # Debug: Tax and fee calculations
        print(f"Discounted Total: {discounted_total}")
        print(f"Tax Amount: {tax_amount}")
        print(f"Service Fee: {service_fee}")
        print(f"Service Fee Tax: {service_fee_tax}")
        print(f"Final Total: {total}")

        return {
            "order_total": round(order_total, 2),
            "discount": round(discount, 2),
            "tax_rate": round(tax_rate, 2),
            "tax_amount": round(tax_amount, 2),
            "service_fee": round(service_fee, 2),
            "service_fee_tax": round(service_fee_tax, 2),
            "total": round(total, 2)
        }
