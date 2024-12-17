from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from .models import Restaurant, Promo, Menu, RestaurantImage, ExpiringToken
from .serializers import RestaurantMiniSerializer, RestaurantSerializer, PromoSerializer, MenuSerializer, Category, CategorySerializer, RegisterSerializer, LoginSerializer, UserSerializer, UserUpdateSerializer, UserProfileSerializer, CustomTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Prefetch
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError

class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.all()
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = self.request.user
        prefetch_options = ['menus', 'images']

        # Base queryset
        queryset = Restaurant.objects.all()

        # Annotate distance if user is authenticated and has coordinates
        if user.is_authenticated and hasattr(user, 'profile') and user.profile.coordinates:
            user_location = user.profile.coordinates
            queryset = queryset.annotate(distance=Distance('coordinates', user_location))

        # Apply search filters
        queryset = self.apply_search_filters(queryset)

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

    def apply_search_filters(self, queryset):
        """Apply search filters based on query parameters."""
        name_query = self.request.query_params.get('name')
        categories_query = self.request.query_params.get('categories')
        service_type_query = self.request.query_params.get('service_type')

        if name_query:
            queryset = queryset.filter(name__icontains=name_query)

        if categories_query:
            try:
                category_ids = [int(cat_id) for cat_id in categories_query.split(',')]
                queryset = queryset.filter(categories__id__in=category_ids).distinct()
            except ValueError:
                pass  # Ignore invalid category IDs

        if service_type_query:
            queryset = queryset.filter(service_type=service_type_query)

        return queryset

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

    def get_queryset(self):
        """
        Exclude promos that have been used and approved by the current user.
        If the user is an admin or restaurant owner, show promos related to their restaurants.
        """
        user = self.request.user

        # Check if the user is authenticated
        if user.is_authenticated:
            profile = getattr(user, 'profile', None)
            
            # If user is admin or restaurant owner, return promos for their restaurants
            if profile and profile.type_of_user in ['admin', 'restaurant_owner']:
                return Promo.objects.filter(restaurant__owner=user).distinct()

            # Exclude promos that have been used and approved by the current user
            return Promo.objects.exclude(
                usages__customer=user,
                usages__status="approved"
            ).distinct()

        # For unauthenticated users, return all promos
        return super().get_queryset()

    @action(detail=False, methods=['get'], url_path='restaurant/(?P<restaurant_id>[^/.]+)')
    def by_restaurant(self, request, restaurant_id=None):
        """
        Custom action to get promos by restaurant ID and optionally by promo_type.
        If the user is an admin or owner, ensure they only access their restaurant's promos.
        """
        promo_type = request.query_params.get('promo_type', None)
        user = request.user

        # Base queryset filtered by restaurant ID
        promos = self.get_queryset().filter(restaurant_id=restaurant_id)

        # For admin or restaurant owners, ensure they only access their promos
        if user.is_authenticated:
            profile = getattr(user, 'profile', None)
            if profile and profile.type_of_user in ['admin', 'restaurant_owner']:
                promos = promos.filter(restaurant__owner=user)

        # Further filter by promo_type if provided
        if promo_type:
            promos = promos.filter(promo_type=promo_type)

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


class FeaturedRestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all().order_by('priority_index').prefetch_related('images')
    serializer_class = RestaurantSerializer
    permission_classes = [AllowAny]

class FeaturedMenuListView(generics.ListAPIView):
    queryset = Menu.objects.all().order_by('priority_index').prefetch_related('images')
    serializer_class = MenuSerializer
    permission_classes = [AllowAny]

class RestaurantCategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(category_type='restaurant').order_by('priority_index')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class MenuCategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(category_type='menu').order_by('priority_index')
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
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

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
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
            # Delete the user's token to log them out
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Token.DoesNotExist:
            return Response({"detail": "Token not found."}, status=status.HTTP_400_BAD_REQUEST)
        
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
    permission_classes = [permissions.IsAuthenticated]

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