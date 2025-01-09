from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RestaurantViewSet,
    PromoViewSet,
    MenuViewSet,
    FeaturedMenuListView,
    FeaturedRestaurantListView,
    RestaurantCategoryList,
    MenuCategoryList,
    RegisterView,
    LoginView,
    LogoutView,
    UserDetailView,
    CustomTokenObtainPairView,
    RestaurantMiniListView,
    UserUpdateView,
    VerifyCodeView,
    ResendEmailView,
    GoogleAuthView,
    SearchView,
    CategoryViewSet,
    FavoriteViewSet,
    CartViewSet, 
    CartItemViewSet
)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .stripe import create_onboarding_link, create_customer_portal_session, create_express_dashboard_link

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'promos', PromoViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')

urlpatterns = [
    path('', include(router.urls)),
    path('featured-restaurants/', FeaturedRestaurantListView.as_view(), name='featured-restaurants'),
    path('featured-menus/', FeaturedMenuListView.as_view(), name='featured-menus'),
    path('restaurant-categories/', RestaurantCategoryList.as_view(), name='restaurant-category-list'),
    path('menu-cuisines/', MenuCategoryList.as_view(), name='menu-category-list'),
    path('restaurants-mini/', RestaurantMiniListView.as_view(), name='restaurant-mini'),  # Updated path
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify_code'),
    path('resend-code/', ResendEmailView.as_view(), name='resend_code'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/logout/', LogoutView.as_view(), name='logout'),
    path('me/', UserDetailView.as_view(), name='user-detail'),
    path('update-user/', UserUpdateView.as_view(), name='update-user'),
    path('token/', CustomTokenObtainPairView.as_view(), name='custom_token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('create-onboarding-link/<int:restaurant_id>/', create_onboarding_link, name='create-onboarding-link'),
    path('create-customer-portal-session/', create_customer_portal_session, name='create-customer-portal-session'),
    path('create-dashboard-link/<int:restaurant_id>/', create_express_dashboard_link, name='create_dashboard_link'),
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('search/', SearchView.as_view(), name='search'),
]
