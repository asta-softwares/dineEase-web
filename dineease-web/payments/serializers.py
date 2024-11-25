from rest_framework import serializers
from .models import Order, OrderItem, Payment
from core.models import Menu, AddonOption

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.StringRelatedField()

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity', 'price', 'addon_options', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True)
    restaurant = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'restaurant', 'items', 'order_total', 'status', 'order_time', 'delivery_address', 'is_delivery', 'order_type', 'tax', 'tip']

class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.StringRelatedField()

    class Meta:
        model = Payment
        fields = ['id', 'order', 'payment_method', 'payment_status', 'transaction_id', 'amount_paid', 'payment_date', 'payment_gateway', 'is_refunded', 'refund_amount']
