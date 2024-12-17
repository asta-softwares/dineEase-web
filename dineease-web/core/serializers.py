from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Restaurant, Promo, Menu, UserProfile, RestaurantImage, AddonCategory, AddonOption, Category
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.gis.geos import Point
from datetime import datetime
from django.utils.timezone import now, localtime, activate

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
    coordinates = serializers.SerializerMethodField()
    distance = serializers.SerializerMethodField()
    is_open = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'categories', 'service_type', 'image', 'city', 'province', 'email',
            'operating_hours', 'location', 'coordinates', 'distance', 'is_open',
            'priority_index', 'telephone', 'ratings', 'description', 'status', 'owner', 
            'social_media_links',
            'promos', 'menus', 'images',
        ]

    def __init__(self, *args, **kwargs):
        # Get the context from the serializer
        context = kwargs.get('context', {})
        user = context.get('request').user if context.get('request') else None

        # If the user is not authenticated or has no coordinates, remove the 'distance' field
        super().__init__(*args, **kwargs)
        if not user or not user.is_authenticated or not getattr(user.profile, 'coordinates', None):
            self.fields.pop('distance', None)

    def get_coordinates(self, obj):
        if obj.coordinates and isinstance(obj.coordinates, Point):
            return [obj.coordinates.x, obj.coordinates.y]
        return None

    def get_distance(self, obj):
        if hasattr(obj, 'distance') and obj.distance:
            return round(obj.distance.km, 2)
        return None

    def to_internal_value(self, data):
        # Handle input for coordinates as a list [longitude, latitude]
        coordinates = data.get('coordinates')
        if coordinates and isinstance(coordinates, list) and len(coordinates) == 2:
            data['coordinates'] = Point(coordinates[0], coordinates[1])
        return super().to_internal_value(data)
    
    def get_is_open(self, obj):
        # activate('Asia/Manila') 
        current_time = localtime(now())  # Get current time in PHT
        current_day = current_time.strftime("%A")  # Get current day (e.g., 'Monday')

        # Get today's operating hours
        operating_hours = obj.operating_hours.get(current_day)

        if not operating_hours or operating_hours.lower() == 'closed':
            return False

        try:
            open_time_str, close_time_str = operating_hours.replace('–', '-').split('-')
            open_time = datetime.strptime(open_time_str.strip(), "%I:%M%p").time()
            close_time = datetime.strptime(close_time_str.strip(), "%I:%M%p").time()

            # Debugging logs
            print(obj.name)
            print(f"Current PHT time: {current_time.time()}")
            print(f"Open time: {open_time}")
            print(f"Close time: {close_time}")

            # Handle case where close time is past midnight
            if close_time < open_time:
                # If current time is before midnight or after midnight
                if current_time.time() >= open_time or current_time.time() <= close_time:
                    return True
            else:
                if open_time <= current_time.time() <= close_time:
                    return True

        except Exception as e:
            print(f"Error parsing operating hours: {e}")
            return False

        return False

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
    # Use a ListField to accept [longitude, latitude] as input
    coordinates = serializers.ListField(
        child=serializers.FloatField(),
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['phone', 'image', 'address', 'city', 'province', 'coordinates']

    def validate_coordinates(self, value):
        # Ensure coordinates are a valid list with two float values
        if len(value) != 2:
            raise serializers.ValidationError("Coordinates must be a list with two float values.")
        return Point(value[0], value[1])

    def update(self, instance, validated_data):
        # Handle coordinates separately
        coordinates = validated_data.pop('coordinates', None)
        if coordinates:
            print("Updating coordinates to:", coordinates)  # Debugging log
            instance.coordinates = coordinates

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        print("Instance coordinates after save:", instance.coordinates)  # Debugging log
        return instance

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        instance = super().update(instance, validated_data)

        # Update the related UserProfile instance
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
    
class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'current_password', 'new_password', 'confirm_password']

    def validate(self, data):
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if new_password or confirm_password:
            if not current_password:
                raise serializers.ValidationError({'current_password': 'Current password is required to change the password.'})
            if new_password != confirm_password:
                raise serializers.ValidationError({'confirm_password': 'New passwords do not match.'})

        return data