from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Restaurant, Promo, Menu, UserProfile, RestaurantImage, AddonCategory, AddonOption, Category
from django.core.exceptions import ValidationError

class RestaurantImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = RestaurantImage
        fields = ['id', 'image', 'caption']

class PromoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)  # Keeps the image field with URL usage

    class Meta:
        model = Promo
        fields = [
            'id', 'restaurant', 'name', 'description', 'discount', 'discount_type', 
            'time_offer', 'status', 'image', 'priority_index', 'start_date', 
            'end_date', 'minimum_order', 'code', 'usage_limit', 'target_audience'
        ]

class AddonOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddonOption
        fields = ['id', 'name', 'price']

class AddonCategorySerializer(serializers.ModelSerializer):
    addon_options = AddonOptionSerializer(many=True, read_only=True)

    class Meta:
        model = AddonCategory
        fields = ['id', 'name', 'required', 'max_selections', 'addon_options']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image']

class MenuSerializer(serializers.ModelSerializer):
    addon_categories = AddonCategorySerializer(many=True, read_only=True)
    images = RestaurantImageSerializer(many=True, read_only=True)  # Include images if you need to
    discounted_cost = serializers.SerializerMethodField()  # New field for discounted price

    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'description', 'cost', 'category', 'status', 'image', 
            'priority_index', 'addon_categories', 'images', 'discounted_cost'
        ]

    def get_discounted_cost(self, obj):
        """
        Calculate the discounted cost if a promo is applied to the menu.
        """
        # Get promos associated with the menu
        promo = obj.promos.filter(status='active').order_by('-priority_index').first()

        # If there's no active promo, return None (or original price if desired)
        if not promo:
            return None

        # Calculate the discounted price
        if promo.discount_type == 'percentage':
            discount = obj.cost * (promo.discount / 100)
        elif promo.discount_type == 'fixed':
            discount = promo.discount
        else:
            discount = 0

        # Ensure discounted price is not negative
        discounted_price = max(obj.cost - discount, 0)

        return round(discounted_price, 2)

class RestaurantSerializer(serializers.ModelSerializer):
    promos = PromoSerializer(many=True, read_only=True)
    menus = MenuSerializer(many=True, read_only=True)
    images = RestaurantImageSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'categories', 'service_type', 'image', 'city', 'province', 'email',
            'operating_hours', 'location', 'coordinates',
            'priority_index', 'telephone', 'ratings', 'description', 'status', 'owner', 
            'social_media_links',
            'promos', 'menus', 'images'
        ]

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def validate_phone(self, value):
        if value and UserProfile.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone number is already taken.")
        return value

    def validate_username(self, value):
        if value and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        email = validated_data.get('email')
        phone = validated_data.get('phone')
        username = validated_data.get('username') or email

        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password']
        )
        UserProfile.objects.create(user=user, phone=phone)

        return user

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')

        # Check if identifier is an email
        user = User.objects.filter(email=identifier).first()
        
        # If no user found with email, check if identifier is a phone
        if not user:
            profile = UserProfile.objects.filter(phone=identifier).first()
            user = profile.user if profile else None

        if user and user.check_password(password):
            data['user'] = user
            return data
        raise serializers.ValidationError("Incorrect username or password.")
    
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'image', 'address', 'city', 'address', 'city']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()  # Nested serializer to include profile data

    class Meta:
        model = User
        fields = ['id', 'profile', 'username', 'email', 'first_name', 'last_name']