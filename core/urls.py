from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, PromoViewSet, MenuViewSet, FeaturedMenuListView, FeaturedRestaurantListView, RestaurantCategoryList, MenuCategoryList

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'promos', PromoViewSet)
router.register(r'menus', MenuViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('featured-restaurants/', FeaturedRestaurantListView.as_view(), name='featured-restaurants'),
    path('featured-menus/', FeaturedMenuListView.as_view(), name='featured-menus'),
    path('restaurant-categories/', RestaurantCategoryList.as_view(), name='restaurant-category-list'),
    path('menu-cuisines/', MenuCategoryList.as_view(), name='menu-category-list'),
]