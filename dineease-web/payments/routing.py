from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/orders/(?P<user_id>\d+)/$', consumers.OrderStatusConsumer.as_asgi()),
    re_path(r'ws/orders/restaurant/(?P<restaurant_id>\d+)/$', consumers.RestaurantOrderConsumer.as_asgi()),
]