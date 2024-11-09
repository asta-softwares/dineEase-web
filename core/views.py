from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from .models import Restaurant, Promo, Menu, RestaurantImage, ExpiringToken
from .serializers import RestaurantSerializer, PromoSerializer, MenuSerializer, Category, CategorySerializer, RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer
    queryset = Restaurant.objects.all().prefetch_related('promos', 'menus', 'images')

    def get_queryset(self):
        # If the user is authenticated, filter restaurants by the owner (logged-in user)
        if self.request.user.is_authenticated:
            return Restaurant.objects.filter(owner=self.request.user).prefetch_related('promos', 'menus', 'images')
        # Otherwise, return all restaurants for public access
        return super().get_queryset()

class PromoViewSet(viewsets.ModelViewSet):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer

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

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Create or retrieve an expiring token
        token = ExpiringToken.get_or_create(user)
        
        return Response({
            'token': token.key,
            'user': {
                'username': user.username,
                'email': user.email,
                'phone': user.profile.phone if hasattr(user, 'profile') else None
            }
        }, status=status.HTTP_200_OK)
    
class UserDetailView(APIView):
    def get(self, request):
        
        print("USER", request.user)
        if request.user.is_authenticated:
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        
        # If the user is not authenticated, return a default response
        return Response({"message": "User not authenticated"}, status=401)