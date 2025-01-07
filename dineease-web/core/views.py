from rest_framework import (
    viewsets,
    generics,
    status,
    permissions
)
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from django.db.models import Q, Prefetch, F, Count
from django.utils.timezone import now
from datetime import timedelta
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point

from .models import (
    Restaurant,
    Promo,
    Menu,
    RestaurantImage,
    ExpiringToken,
    VerificationCode
)
from .serializers import (
    RestaurantMiniSerializer,
    RestaurantSerializer,
    PromoSerializer,
    MenuSerializer,
    Category,
    CategorySerializer,
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    CustomTokenObtainPairSerializer,
    RestaurantSearchSerializer,
    PromoSearchSerializer,
    MenuSearchSerializer,
)
from .utils import send_confirmation_email
from collections import defaultdict
from rest_framework.filters import SearchFilter
from .filters import RestaurantFilter

from google.oauth2.id_token import verify_oauth2_token
from google.auth.transport.requests import Request

class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.all()
    permission_classes = [AllowAny]

    # Enable filtering and searching
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RestaurantFilter

    def get_queryset(self):
        user = self.request.user
        prefetch_options = ['menus', 'images']

        # Base queryset
        queryset = Restaurant.objects.all()

        # Annotate distance if user is authenticated and has coordinates
        if user.is_authenticated and hasattr(user, 'profile') and user.profile.coordinates:
            user_location = user.profile.coordinates
            queryset = queryset.annotate(distance=Distance('coordinates', user_location))

        # Handle specific cases for different user types
        if user.is_authenticated:
            profile = user.profile

            if profile.type_of_user == 'customer':
                available_promos = Promo.objects.exclude(
                    usages__customer=user,
                    usages__status="approved"
                )
                prefetch_options.append(Prefetch('promos', queryset=available_promos))

            elif profile.type_of_user in ['admin', 'restaurant_owner']:
                user_promos = Promo.objects.filter(restaurant__owner=user)
                return queryset.filter(owner=user).prefetch_related(
                    Prefetch('promos', queryset=user_promos),
                    *prefetch_options
                )

        else:
            prefetch_options.append('promos')

        return queryset.prefetch_related(*prefetch_options)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
class RestaurantMiniListView(generics.ListAPIView):
    serializer_class = RestaurantMiniSerializer

    def get_queryset(self):
        user = self.request.user

        # Check if the user is authenticated
        if not user.is_authenticated:
            return Restaurant.objects.none()

        # Get user profile
        profile = user.profile

        # If the user is an admin or restaurant owner, return restaurants they own
        if profile.type_of_user in ['admin', 'restaurant_owner']:
            return Restaurant.objects.filter(owner=user)

        # Default behavior: return an empty queryset
        return Restaurant.objects.none()

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = [AllowAny]

    def get_filtered_promos(self, user, restaurant_id=None):
        """
        Shared logic for filtering promos based on user type and other conditions.
        """
        current_date = now().date()
        # Initial query includes all promos
        promos = Promo.objects.all()

        # If restaurant_id is provided, include promos for that restaurant or no restaurant (DineEase promos)
        if restaurant_id is not None:
            promos = promos.filter(Q(restaurant_id=restaurant_id) | Q(restaurant__isnull=True))
            print(f"Initial promos for restaurant {restaurant_id} (including DineEase promos): {promos}")
        else:
            print(f"Initial promos (global): {promos}")

        if user.is_authenticated:
            profile = getattr(user, 'profile', None)

            if profile and profile.type_of_user == 'admin':
                # Admins: Include promos without restaurants
                promos = promos.filter(Q(restaurant__isnull=True) | Q(restaurant_id=restaurant_id))
                print(f"Admin detected. Promos: {promos}")

            elif profile and profile.type_of_user == 'restaurant_owner':
                # Restaurant owners: Include only their own promos
                promos = promos.filter(restaurant__owner=user)
                print(f"Restaurant owner detected. Owned promos: {promos}")

            else:
                # Customers: Apply filters for active promos, valid dates, and specific promo types
                print("Customer detected. Applying customer-specific filters.")
                promos = promos.filter(
                    Q(status='active'),
                    Q(start_date__isnull=True) | Q(start_date__lte=current_date),
                    Q(end_date__isnull=True) | Q(end_date__gte=current_date),
                    promo_type__in=['restaurant', 'dineease']  # Include only restaurant and DineEase promos
                )
                print(f"After status and promo_type filters: {promos}")

                # Apply minimum order filter
                order_total = self.request.query_params.get('order_total', 0)
                promos = promos.filter(
                    Q(minimum_order__isnull=True) | Q(minimum_order__lte=order_total)
                )
                print(f"After minimum_order filter: {promos}")

                # Annotate usage counts and exclude overused promos
                promos = promos.annotate(
                    total_usages=Count('usages', filter=Q(usages__status='approved')),
                    customer_usages=Count(
                        'usages',
                        filter=Q(usages__status='approved', usages__customer=user)
                    )
                ).exclude(
                    Q(usage_limit__isnull=False, total_usages__gte=F('usage_limit')) |
                    Q(
                        usage_limit_per_customer__isnull=False,
                        customer_usages__gte=F('usage_limit_per_customer')
                    )
                )
                print(f"After usage limits exclusion: {promos}")

        else:
            # Unauthenticated users: Apply active and valid date filters
            print("Unauthenticated user detected. Applying basic filters.")
            promos = promos.filter(
                Q(status='active'),
                Q(start_date__isnull=True) | Q(start_date__lte=current_date),
                Q(end_date__isnull=True) | Q(end_date__gte=current_date)
            )
            print(f"Unauthenticated filtered promos: {promos}")

        return promos.distinct()

    def get_queryset(self):
        """
        Main queryset logic shared across the viewset.
        """
        return self.get_filtered_promos(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='restaurant/(?P<restaurant_id>[^/.]+)')
    def by_restaurant(self, request, restaurant_id=None):
        """
        Retrieve promos specific to a given restaurant with appropriate filtering.
        """
        promos = self.get_filtered_promos(user=self.request.user, restaurant_id=restaurant_id)

        # Serialize and return filtered promos
        serializer = self.get_serializer(promos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all().prefetch_related(
        'images',
        'addon_categories__addon_options'
    )
    serializer_class = MenuSerializer

    # Allow unauthenticated access to the view
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        If the user is an admin or restaurant owner, return menus for their restaurants.
        Otherwise, return all menus.
        """
        user = self.request.user

        # Check if the user is authenticated
        if user.is_authenticated:
            profile = getattr(user, 'profile', None)

            # If user is admin or restaurant owner, return menus for their restaurants
            if profile and profile.type_of_user in ['admin', 'restaurant_owner']:
                return Menu.objects.filter(restaurant__owner=user).prefetch_related(
                    'images',
                    'addon_categories__addon_options'
                ).distinct()

        # For unauthenticated or general users, return all menus
        return super().get_queryset()


class FeaturedRestaurantListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # Determine the grouping field based on the query parameter
        group_by = request.query_params.get('group_by', 'city')  # Default to 'city'

        if group_by not in ['city', 'province']:
            return Response({"error": "Invalid group_by parameter. Use 'city' or 'province'."}, status=400)

        # Fetch restaurants with non-null priority_index and order by priority_index
        queryset = (
            Restaurant.objects.filter(priority_index__isnull=False)
            .order_by('priority_index')
            .prefetch_related('images')
        )

        # Serialize data, passing the request context
        serializer = RestaurantSerializer(queryset, many=True, context={'request': request})

        # Group restaurants dynamically by the specified field
        grouped_restaurants = defaultdict(list)
        for restaurant in serializer.data:
            # Use 'Unknown' if the group_by field is empty or null
            group_value = restaurant.get(group_by, 'Unknown') or 'Unknown'
            grouped_restaurants[group_value].append(restaurant)

        # Convert to desired output format
        grouped_data = [{'group': group_value, 'restaurants': restaurants} for group_value, restaurants in grouped_restaurants.items()]

        return Response(grouped_data)

class FeaturedMenuListView(generics.ListAPIView):
    queryset = Menu.objects.all().order_by('priority_index').prefetch_related('images')
    serializer_class = MenuSerializer
    permission_classes = [AllowAny]

class RestaurantCategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(category_type='restaurant').order_by('priority_index')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class MenuCategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Return categories based on user type:
        - If admin or restaurant owner, return categories tied to their restaurant or global categories.
        - Otherwise, return all global categories.
        """
        user = self.request.user

        # Base queryset: menu categories ordered by priority index
        queryset = Category.objects.filter(category_type='menu').order_by('priority_index')

        if user.is_authenticated and hasattr(user, 'profile') and user.profile.type_of_user in ['admin', 'restaurant_owner']:
            # Categories tied to the user's restaurant or global categories
            return queryset.filter(
                Q(restaurant__owner=user) | Q(restaurant__isnull=True)
            )

        # For other users or unauthenticated users, return global categories only
        return queryset.filter(restaurant__isnull=True)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Category instances.
    """
    queryset = Category.objects.all().order_by('priority_index', 'name')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    # Add filter backends for search and filtering
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category_type']  # Enable filtering by category_type
    search_fields = ['name']  # Enable searching by name

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = self.perform_create(serializer)
            
            # Generate a 6-digit code
            verification_code = VerificationCode.objects.create(user=user)
            verification_code.generate_code()
            
            # Send the confirmation email
            send_confirmation_email(user, verification_code.code)
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error during registration: {e}")
            return Response(
                {"detail": "An unexpected error occurred during registration."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        return serializer.save()

class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"detail": "Email and code are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)

            verification_code = VerificationCode.objects.filter(
                user=user, 
                created_at__gte=now() - timedelta(minutes=30)
            ).order_by('-created_at').first()

            if not verification_code:
                return Response({"detail": "No valid verification code found for this user. Please request for a new code."}, status=status.HTTP_404_NOT_FOUND)

            if verification_code.code == code:
                user.is_active = True
                user.save()

                verification_code.delete()

                return Response({"detail": "Email confirmed successfully."}, status=status.HTTP_200_OK)

            return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        
class ResendEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            verification = VerificationCode.objects.get(user=user)

            # Generate a new code
            verification.generate_code()

            send_confirmation_email(user, verification.code)

            return Response({"detail": "Verification code resent."}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, VerificationCode.DoesNotExist):
            return Response({"detail": "User not found or no verification pending."}, status=status.HTTP_404_NOT_FOUND)

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            # Return 401 Unauthorized for invalid credentials
            return Response({"error": e.detail}, status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data['user']

        # Create JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'refresh': str(refresh),
            'access': str(access_token),
            'user': {
                'username': user.username,
                'email': user.email,
                'phone': user.profile.phone if hasattr(user, 'profile') else None
            }
        }, status=status.HTTP_200_OK)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract the refresh token from the request
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({"message": "User not authenticated"}, status=401)

class UserUpdateView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        return UserUpdateSerializer

    def partial_update(self, request, *args, **kwargs):
        
        user = self.get_object()
        user_serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        profile_serializer = UserProfileSerializer(user.profile, data=request.data.get('profile', {}), partial=True)

        # Validate and save user fields
        if user_serializer.is_valid():
            user_data = user_serializer.validated_data

            # Handle password change
            current_password = user_data.get('current_password')
            new_password = user_data.get('new_password')
            if current_password and new_password:
                if not user.check_password(current_password):
                    raise ValidationError({'current_password': 'Current password is incorrect.'})
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep the user logged in after password change

            user.first_name = user_data.get('first_name', user.first_name)
            user.last_name = user_data.get('last_name', user.last_name)
            user.save()
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validate and save profile fields
        if profile_serializer.is_valid():
            profile_serializer.save()
        else:
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'user': user_serializer.data,
            'profile': profile_serializer.data
        }, status=status.HTTP_200_OK)
    

from core.models import UserProfile
    
class GoogleAuthView(APIView):
    permission_classes = [AllowAny]
    """
    Handle Google OAuth login and registration.
    """

    def post(self, request, *args, **kwargs):
        google_token = request.data.get("google_token")
        type_of_user = request.data.get("type_of_user")

        if not google_token:
            return Response({"error": "Google token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verify the Google ID token
            idinfo = verify_oauth2_token(google_token, Request())

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid issuer.')

            email = idinfo['email']
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            # Check if user exists, otherwise create a new user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": first_name,
                    "last_name": last_name,
                }
            )

            if created:
                UserProfile.objects.create(user=user, type_of_user=type_of_user)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                "access": access_token,
                "refresh": refresh_token,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                }
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class SearchView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        query = request.query_params.get('query', '').strip()

        if not query:
            return Response({"error": "Query parameter 'query' is required."}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user if request.user.is_authenticated else None
        type_of_user = getattr(user.profile, 'type_of_user', 'customer') if user else 'customer'

        if type_of_user == 'restaurant_owner':
            # Show owned promos and unrestricted restaurants and menus
            restaurant_results = Restaurant.objects.filter(owner=user)
            promo_results = Promo.objects.filter(restaurant__owner=user, name__icontains=query)
            menu_results = Menu.objects.filter(restaurant__owner=user, name__icontains=query)
        else:
            # For customers or unauthenticated users, show unrestricted restaurants and menus
            restaurant_results = Restaurant.objects.filter(name__icontains=query)
            promo_results = Promo.objects.none()  # No promos for customers
            menu_results = Menu.objects.filter(name__icontains=query)

        results = (
            RestaurantSearchSerializer(restaurant_results, many=True).data +
            PromoSearchSerializer(promo_results, many=True).data +
            MenuSearchSerializer(menu_results, many=True).data
        )

        # Sort results by name
        results = sorted(results, key=lambda x: x['name'])

        return Response(results, status=status.HTTP_200_OK)