from django.db import models
from core.models import Restaurant, Menu, AddonOption, Promo
from django.contrib.auth.models import User

class PromoUsage(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    promo = models.ForeignKey(Promo, on_delete=models.CASCADE, related_name='usages')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_usages')
    used_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    class Meta:
        unique_together = ('promo', 'customer')  # Ensure one customer can only attempt to use a promo once

    def __str__(self):
        return f"{self.customer.username} attempted {self.promo.name} - {self.status}"
class Order(models.Model):
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    menu_items = models.ManyToManyField(Menu, through='OrderItem')
    promo = models.ForeignKey(Promo, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')  # Applied promo
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ])
    order_time = models.DateTimeField(auto_now_add=True)
    special_instructions = models.TextField(blank=True, null=True)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)
    is_delivery = models.BooleanField(default=False)
    order_type = models.CharField(max_length=50, choices=[
        ('dine_in', 'Dine-in'),
        ('takeaway', 'Takeaway'),
        ('delivery', 'Delivery')
    ])
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tip = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name} for Order {self.order.id}"

class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=50, choices=[
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('mobile_payment', 'Mobile Payment'),
        ('wallet', 'Wallet')
    ])
    payment_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ])
    transaction_id = models.CharField(max_length=255, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)  # Store in dollars
    refund_status = models.CharField(max_length=50, choices=[
        ('not_requested', 'Not Requested'),
        ('requested', 'Requested'),
        ('partial', 'Partial Refund'),
        ('full', 'Full Refund')
    ], default='not_requested')
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_gateway = models.CharField(max_length=50, choices=[
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('manual', 'Manual')
    ])
    refund_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_method}"
