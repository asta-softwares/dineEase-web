from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as gis_models
from .constants import CANADA_PROVINCE_CHOICES
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.utils.text import slugify

class Category(models.Model):
    CATEGORY_TYPES = (
        ('restaurant', 'Restaurant'),
        ('menu', 'Menu'),
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    category_type = models.CharField(max_length=50, choices=CATEGORY_TYPES)
    priority_index = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"
    
class Restaurant(models.Model):
    STATUSES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('premium', 'Premium'),
    )

    SERVICE_TYPES = (
        ('dine-in', 'Dine-in'),
        ('takeout', 'Takeout'),
        ('both', 'Both'),
    )

    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='restaurant_images/')
    categories = models.ManyToManyField(
        Category,
        blank=True,
        limit_choices_to={'category_type': 'restaurant'},
        related_name='restaurants'
    )
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPES, default='both')
    operating_hours = models.JSONField(
        default={
            "Monday": "9:00AM – 3:00PM",
            "Tuesday": "9:00AM – 3:00PM",
            "Wednesday": "9:00AM – 3:00PM",
            "Thursday": "9:00AM – 3:00PM",
            "Friday": "9:00AM – 3:00PM",
            "Saturday": "Closed",
            "Sunday": "Closed"
        }
    )
    slug = models.SlugField(max_length=255, unique=False, blank=True, null=True)
    location = models.CharField(max_length=255)
    coordinates = gis_models.PointField()
    city = models.CharField(max_length=100, null=True, blank=True)
    province = models.CharField(max_length=2, choices=CANADA_PROVINCE_CHOICES, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    telephone = models.CharField(max_length=15)
    ratings = models.FloatField(default=0.0)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUSES, default='active')
    owner = models.ForeignKey(User , on_delete=models.CASCADE, related_name='restaurants')
    priority_index = models.PositiveIntegerField(null=True, blank=True)
    social_media_links = models.JSONField(
        default={
            "fb": "",
            "twitter": "",
            "instagram": "",
            "linkedin": ""
        }
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
class Promo(models.Model):
    STATUSES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    DISCOUNT_TYPES = (
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    )

    restaurant = models.ForeignKey('Restaurant', on_delete=models.CASCADE, related_name='promos', null=True, blank=True)
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='promos', null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='percentage')
    image = models.ImageField(upload_to='promo_images/', blank=True, null=True)
    usage_limit = models.PositiveIntegerField(null=True, blank=True)  # Total times promo can be used
    usage_count = models.PositiveIntegerField(default=0)  # Tracks how many times it has been used
    status = models.CharField(max_length=10, choices=STATUSES, default='active')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    time_offer = models.JSONField(
        default={
            "Monday": "9:00AM – 3:00PM",
            "Tuesday": "9:00AM – 3:00PM",
            "Wednesday": "9:00AM – 3:00PM",
            "Thursday": "9:00AM – 3:00PM",
            "Friday": "9:00AM – 3:00PM",
            "Saturday": "Closed",
            "Sunday": "Closed"
        }
    )
    priority_index = models.PositiveIntegerField(null=True, blank=True)
    minimum_order = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    code = models.CharField(max_length=50, unique=True, null=True, blank=True)
    target_audience = models.CharField(max_length=50, null=True, blank=True)


    def can_be_used(self):
        """Check if the promo is valid and can be used."""
        if self.status != 'active':
            return False
        if self.usage_limit is not None and self.usage_count >= self.usage_limit:
            return False
        return True

    def increment_usage(self):
        """Increment usage count when the promo is used."""
        if self.can_be_used():
            self.usage_count += 1
            self.save()
            return True
        return False

    def __str__(self):
        return self.name
    
class Menu(models.Model):
    STATUSES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'category_type': 'menu'}, related_name='menus')
    name = models.CharField(max_length=255)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUSES, default='active')
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    priority_index = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    
class AddonCategory(models.Model):
    # Each category is tied to a specific menu item
    menu = models.ForeignKey('Menu', on_delete=models.CASCADE, related_name='addon_categories')
    name = models.CharField(max_length=255)  # Category name like "Protein Addition", "Serving Choice"
    required = models.BooleanField(default=False)  # Is the category required?
    max_selections = models.PositiveIntegerField(default=1)  # Max number of selections from this category

    def __str__(self):
        return self.name

class AddonOption(models.Model):
    category = models.ForeignKey(AddonCategory, on_delete=models.CASCADE, related_name='addon_options')
    name = models.CharField(max_length=255, blank=True, null=True)  # Option name
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Additional price for the option
    menu_item = models.ForeignKey('Menu', on_delete=models.SET_NULL, null=True, blank=True, related_name='as_addon_options')  # Can also be a Menu item

    def __str__(self):
        if self.menu_item:
            return f"Menu Item: {self.menu_item.name}"
        return f"{self.name} (+${self.price})"

class RestaurantImage(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='images', null=True, blank=True)
    image = models.ImageField(upload_to='images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        if self.restaurant:
            return f"Image for restaurant: {self.restaurant.name}"
        elif self.menu:
            return f"Image for menu: {self.menu.name}"
        else:
            return "Unassigned image"
    
class UserProfile(models.Model):
    USER_TYPES = [
        ('restaurant_owner', 'Restaurant Owner'),
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email = models.EmailField(unique=True, null=True, blank=True)
    type_of_user = models.CharField(max_length=20, choices=USER_TYPES, default='customer')
    phone = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='user_pictures/', blank=True)
    
    def __str__(self):
        return self.user.username
    
class ExpiringToken(Token):
    class Meta:
        proxy = True  # Use this model as a proxy to add additional methods without creating a new table

    def has_expired(self):
        expiration_date = self.created + timedelta(hours=24)  # Set the token validity duration here
        return timezone.now() > expiration_date

    @classmethod
    def get_or_create(cls, user):
        token, created = cls.objects.get_or_create(user=user)
        if not created and token.has_expired():
            token.delete()
            token = cls.objects.create(user=user)
        return token
