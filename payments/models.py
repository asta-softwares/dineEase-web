from django.db import models
from core.models import Restaurant, Menu, AddonOption

class Order(models.Model):
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Assuming the user model is in the main auth system
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')  # Connected to core app
    menu_items = models.ManyToManyField(Menu, through='OrderItem')
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ])
    order_time = models.DateTimeField(auto_now_add=True)
    special_instructions = models.TextField(blank=True, null=True)
    addon_options = models.ManyToManyField(AddonOption, blank=True)
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
    addon_options = models.ManyToManyField(AddonOption, blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    special_instructions = models.TextField(blank=True, null=True)

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
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_gateway = models.CharField(max_length=50, choices=[
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('manual', 'Manual')
    ])
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_refunded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_method}"
