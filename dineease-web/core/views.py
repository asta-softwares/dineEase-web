from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from .models import Restaurant, Promo, Menu, RestaurantImage, ExpiringToken, VerificationCode
from .serializers import RestaurantMiniSerializer, RestaurantSerializer, PromoSerializer, MenuSerializer, Category, CategorySerializer, RegisterSerializer, LoginSerializer, UserSerializer, UserUpdateSerializer, UserProfileSerializer, CustomTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Prefetch
from rest_framework.decorators import action
from rest_framework import permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError
from .utils import send_confirmation_email
from google.oauth2.id_token import verify_oauth2_token
from google.auth.transport.requests import Request

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

        # Filter by name
        if name_query:
            queryset = queryset.filter(name__icontains=name_query)

        # Filter by categories
        if categories_query:
            try:
                category_ids = [int(cat_id) for cat_id in categories_query.split(',')]
                queryset = queryset.filter(categories__id__in=category_ids).distinct()
            except ValueError:
                pass

        if service_type_query:
            if service_type_query == 'dine-in':
                queryset = queryset.filter(service_type__in=['dine-in', 'both'])
            elif service_type_query == 'takeout':
                queryset = queryset.filter(service_type__in=['takeout', 'both'])
            else:
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
            # Find user by email
            user = User.objects.get(email=email)

            # Check if the provided code matches the user's verification code
            if user.verification_code.code == code:
                # Mark the user as verified or activate the account
                user.is_active = True
                user.save()
                return Response({"detail": "Email confirmed successfully."}, status=status.HTTP_200_OK)
            
            return Response({"detail": "Invalid code."}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        except AttributeError:
            return Response({"detail": "Verification code not found for this user."}, status=status.HTTP_400_BAD_REQUEST)
        
class ResendEmailView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
            verification = VerificationCode.objects.get(user=user)

            # Generate a new code
            verification.generate_code()

            # Resend the confirmation email
            send_confirmation_email(user, verification.code)

            return Response({"detail": "Verification code resent."}, status=status.HTTP_200_OK)
        except (User.DoesNotExist, VerificationCode.DoesNotExist):
            return Response({"detail": "User not found or no verification pending."}, status=status.HTTP_404_NOT_FOUND)

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