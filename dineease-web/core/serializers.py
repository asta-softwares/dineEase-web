from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Restaurant, Promo, Menu, UserProfile, RestaurantImage, AddonCategory, AddonOption, Category
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class RestaurantImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = RestaurantImage
        fields = ['id', 'image', 'caption']

class RestaurantMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name']
        
class PromoSerializer(serializers.ModelSerializer):
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), write_only=True)
    restaurant_details = RestaurantMiniSerializer(source='restaurant', read_only=True)

    class Meta:
        model = Promo
        fields = [
            'id', 'restaurant', 'restaurant_details', 'name', 'description', 'discount', 'discount_type', 
            'time_offer', 'status', 'priority_index', 'start_date', 
            'end_date', 'minimum_order', 'code', 'usage_limit', 'target_audience', 'promo_type',
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

class MenuMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'description', 'cost', 'category', 'status', 'image',
        ]

class MenuSerializer(serializers.ModelSerializer):
    addon_categories = AddonCategorySerializer(many=True, read_only=True)
    images = RestaurantImageSerializer(many=True, read_only=True)
    discounted_cost = serializers.SerializerMethodField()

    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all(), write_only=True)
    restaurant_details = RestaurantMiniSerializer(source='restaurant', read_only=True)
    promos = serializers.PrimaryKeyRelatedField(queryset=Promo.objects.all(), many=True, required=False)

    class Meta:
        model = Menu
        fields = [
            'id', 'name', 'description', 'restaurant', 'restaurant_details', 'cost',
            'category', 'status', 'image', 'priority_index', 'addon_categories',
            'images', 'discounted_cost', 'promos'
        ]

    def get_discounted_cost(self, obj):
        """
        Calculate the discounted cost if a promo is applied to the menu.
        """
        promo = obj.promos.filter(status='active').order_by('-priority_index').first()
        if not promo:
            return None

        # Calculate the discounted price
        if promo.discount_type == 'percentage':
            discount = obj.cost * (promo.discount / 100)
        elif promo.discount_type == 'fixed':
            discount = promo.discount
        else:
            discount = 0

        discounted_price = max(obj.cost - discount, 0)
        return round(discounted_price, 2)

    def create(self, validated_data):
        promos_data = validated_data.pop('promos', [])
        menu = Menu.objects.create(**validated_data)
        menu.promos.set(promos_data)
        return menu

    def update(self, instance, validated_data):
        promos_data = validated_data.pop('promos', None)
        instance = super().update(instance, validated_data)
        if promos_data is not None:
            instance.promos.set(promos_data)
        return instance

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
            'promos', 'menus', 'images',
        ]

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15, write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    type_of_user = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password', 'first_name', 'last_name', 'type_of_user')
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
        phone = validated_data.pop('phone', None)
        type_of_user = validated_data.pop('type_of_user')

        user = User.objects.create_user(
            username=validated_data.get('username') or email,
            email=email,
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        # Create UserProfile with phone and type_of_user
        UserProfile.objects.create(user=user, phone=phone, type_of_user=type_of_user)

        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        profile = getattr(instance, 'userprofile', None)
        if profile:
            representation['phone'] = profile.phone
            representation['type_of_user'] = profile.type_of_user
        return representation

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get('identifier')
        password = data.get('password')
        user = None

        # Check if identifier matches an email
        if '@' in identifier:
            user = User.objects.filter(email=identifier).first()

        # Check if identifier matches a phone number
        if not user:
            profile = UserProfile.objects.filter(phone=identifier).first()
            user = profile.user if profile else None

        # Check if identifier matches a username
        if not user:
            user = User.objects.filter(username=identifier).first()

        # Validate password
        if user and user.check_password(password):
            data['user'] = user
            return data

        raise serializers.ValidationError("Incorrect username, email, or phone number, or password.")
    
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        user = None

        # Check if the username is an email
        if '@' in username:
            user = User.objects.filter(email=username).first()

        # Check if the username is a phone number in UserProfile
        if not user:
            profile = UserProfile.objects.filter(phone=username).first()
            user = profile.user if profile else None

        # Check if the username matches the username field
        if not user:
            user = User.objects.filter(username=username).first()

        if user and user.check_password(password):
            # Set the 'username' in attrs for TokenObtainPairSerializer
            attrs['username'] = user.username
            return super().validate(attrs)

        raise serializers.ValidationError("Incorrect email, phone number, or username, or password.")
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone', 'image', 'address', 'city', 'address', 'city']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()  # Nested serializer to include profile data

    class Meta:
        model = User
        fields = ['id', 'profile', 'username', 'email', 'first_name', 'last_name']