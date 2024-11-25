from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from .models import Restaurant, Promo, Menu, RestaurantImage, ExpiringToken
from .serializers import RestaurantSerializer, PromoSerializer, MenuSerializer, Category, CategorySerializer, RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q, Prefetch

class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.all()

    def get_queryset(self):
        user = self.request.user

        # Check if the user is authenticated
        if not user.is_authenticated:
            return Restaurant.objects.prefetch_related('promos', 'menus', 'images')

        # Get user profile
        profile = user.profile

        # If the user is a customer, return all restaurants with promos available for the user
        if profile.type_of_user == 'customer':
            available_promos = Promo.objects.exclude(
                usages__customer=user,
                usages__status="approved"
            )
            return Restaurant.objects.prefetch_related(
                Prefetch('promos', queryset=available_promos),
                'menus',
                'images'
            )

        # If the user is an admin or restaurant owner, return only the restaurants they created
        if profile.type_of_user in ['admin', 'restaurant_owner']:
            return Restaurant.objects.filter(owner=user).prefetch_related(
                Prefetch('promos', queryset=Promo.objects.filter(restaurant__owner=user)),
                'menus',
                'images'
            )

        # Default behavior for other cases
        return Restaurant.objects.prefetch_related('promos', 'menus', 'images')

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer

    def get_queryset(self):
        """
        Exclude promos that have been used and approved by the current user.
        """
        if self.request.user.is_authenticated:
            # Exclude promos where the user has an approved usage
            return Promo.objects.exclude(
                usages__customer=self.request.user,
                usages__status="approved"
            ).distinct()

        # For unauthenticated users, return all promos
        return super().get_queryset()

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all().prefetch_related(
        'images',
        'addon_categories__addon_options'
    )
    serializer_class = MenuSerializer

class FeaturedRestaurantListView(generics.ListAPIView):
    queryset = Restaurant.objects.all().order_by('priority_index').prefetch_related('images')
    serializer_class = RestaurantSerializer

class FeaturedMenuListView(generics.ListAPIView):
    queryset = Menu.objects.all().order_by('priority_index').prefetch_related('images')
    serializer_class = MenuSerializer

class RestaurantCategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(category_type='restaurant').order_by('priority_index')
    serializer_class = CategorySerializer

class MenuCategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(category_type='menu').order_by('priority_index')
    serializer_class = CategorySerializer

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except ValidationError as e:
            # Explicitly return validation errors as a 400 Bad Request
            print(f"Unexpected error during registration1: {e}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log unexpected errors and return a 500 Internal Server Error with details
            print(f"Unexpected error during registration: {e}")  # Log the error for debugging
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
    
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        return Response({"message": "User not authenticated"}, status=401)