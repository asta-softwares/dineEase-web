from django.db import models
from core.models import Restaurant, Menu, AddonOption, Promo, VerificationCode
from django.contrib.auth.models import User
from core.constants import CANADA_PROVINCE_CHOICES
from decimal import Decimal

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

    # class Meta:
    #     unique_together = ('promo', 'customer')

    def __str__(self):
        return f"{self.customer.username} attempted {self.promo.name} - {self.status}"

def default_service_fee_thresholds():
    """
    Define thresholds for service fees:
    Below $25 - $0.49
    $25-50 - $0.99
    $50-75 - $1.49
    $75-100 - $1.99
    Increase $0.50 for every $25 spent.
    """
    return {
        '<25': 0.49,
        '25-50': 0.99,
        '50-75': 1.49,
        '75-100': 1.99,
        '>=100': 2.49,  # Increment by $0.50 for every $25 spent beyond $100
    }

class Tax(models.Model):
    province = models.CharField(max_length=2, choices=CANADA_PROVINCE_CHOICES, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Tax rate as a percentage (e.g., 5 for 5%)")
    service_fee_thresholds = models.JSONField(
        default=default_service_fee_thresholds,
        help_text="Define thresholds for service fees. E.g., {'<25': 0.49, '25-50': 0.99, '50-75': 1.49, '>=100': 2.49}"
    )
    is_active = models.BooleanField(default=True, help_text="Indicates whether the tax rate is active.")

    def get_service_fee(self, order_total):
        """
        Determine the service fee based on the thresholds:
        - Below $25: $0.49
        - $25-50: $0.99
        - $50-75: $1.49
        - $75-100: $1.99
        - Every additional $25 beyond $100 adds $0.50.
        """
        for key, fee in self.service_fee_thresholds.items():
            if key.startswith('<') and order_total < float(key[1:]):
                return fee
            elif '-' in key:
                low, high = map(float, key.split('-'))
                if low <= order_total < high:
                    return fee
            elif key.startswith('>=') and order_total >= float(key[2:]):
                # Calculate increments beyond $100 dynamically
                base_fee = fee
                additional_amount = order_total - 100
                additional_increments = int(additional_amount // 25)  # Count $25 increments
                return base_fee + (additional_increments * 0.50)
        return 0  # Default fee if no match

    def __str__(self):
        return f"{self.get_province_display()} - Tax: {self.rate}% {'(Active)' if self.is_active else '(Inactive)'}"
    
class Order(models.Model):
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    menu_items = models.ManyToManyField(Menu, through='OrderItem')
    promos = models.ManyToManyField(Promo, related_name='orders', blank=True)
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
    tip = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    service_fee_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    stripe_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    restaurant_payment_before_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Restaurant payment before Stripe fee
    restaurant_payment = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Final restaurant payment after Stripe fee
    platform_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))  # Revenue retained by the platform

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verification_code = models.OneToOneField(VerificationCode, on_delete=models.CASCADE, null=True, blank=True, related_name='order')

    class Meta:
        ordering = ['-order_time']
        
    def calculate_totals(self):
        """Calculate discounts, tax, service fee, and final total."""
        if not self.pk:  # Ensure the instance is saved
            raise ValueError("Order instance must be saved before calculating totals.")

        # Fetch tax rate and service fee thresholds
        tax = Tax.objects.filter(province=self.restaurant.province).first()
        if not tax:
            # No tax configuration; set defaults
            self.tax_rate = Decimal(0)
            self.tax_amount = Decimal(0)
            self.service_fee = Decimal(0)
            self.service_fee_tax = Decimal(0)
            self.total = self.order_total
            return

        # Sort promos: apply percentage discounts first, then fixed discounts
        sorted_promos = sorted(self.promos.all(), key=lambda promo: promo.discount_type == 'fixed')

        # Calculate total discount
        self.discount = Decimal(0)
        discounted_total = Decimal(self.order_total)
        for promo in sorted_promos:
            if promo.discount_type == 'percentage':
                discount_amount = discounted_total * (Decimal(promo.discount) / Decimal(100))
            elif promo.discount_type == 'fixed':
                discount_amount = Decimal(promo.discount)

            # Ensure discount does not exceed remaining total
            discount_amount = min(discount_amount, discounted_total)
            discounted_total -= discount_amount
            self.discount += discount_amount

        # Calculate tax amount on the discounted total
        self.tax_rate = Decimal(tax.rate)
        self.tax_amount = discounted_total * (self.tax_rate / Decimal(100))

        # Calculate service fee
        self.service_fee = Decimal(tax.get_service_fee(discounted_total))

        # Calculate tax on service fee
        self.service_fee_tax = self.service_fee * (self.tax_rate / Decimal(100))

        # Final total
        self.total = discounted_total + self.tax_amount + self.service_fee + self.service_fee_tax

    def save(self, *args, **kwargs):
        """Override save to calculate totals only on creation."""
        if not self.pk:  # Only calculate totals on creation
            super().save(*args, **kwargs)  # Save to generate a primary key
            self.calculate_totals()  # Calculate totals after instance creation

            super().save(update_fields=[
                'discount', 'tax_rate', 'tax_amount',
                'service_fee', 'service_fee_tax', 'total'
            ])
        else:
            super().save(*args, **kwargs)

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
        ('card', 'Card'),
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
    card_brand = models.CharField(max_length=50, null=True, blank=True)
    card_last4 = models.CharField(max_length=4, null=True, blank=True)
    card_exp_month = models.PositiveIntegerField(null=True, blank=True)
    card_exp_year = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order.id} - {self.payment_method}"

class Refund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_date = models.DateTimeField(auto_now_add=True)
    refund_reason = models.TextField(null=True, blank=True)
    refund_status = models.CharField(max_length=50, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ])

    def __str__(self):
        return f"Refund {self.id} - {self.refund_amount}"
