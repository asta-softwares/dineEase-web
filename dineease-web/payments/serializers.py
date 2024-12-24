from rest_framework import serializers
from .models import Order, OrderItem, Payment, Refund
from core.models import Menu, AddonOption
from core.serializers import MenuMiniSerializer, UserSerializer

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

    class Meta:
        model = Order
        fields = [
            'id',
            'customer',
            'restaurant',
            'items',
            'order_total',
            'status',
            'order_time',
            'delivery_address',
            'is_delivery',
            'order_type',
            'tax',
            'tip',
            'payment',
        ]
