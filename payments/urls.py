from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PaymentViewSet, CreateOrderView, UpdatePaymentStatusView, UpdateOrderStatusView
from .webhooks import stripe_webhook

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    # Register DefaultRouter routes under 'router/' to avoid conflicts
    path('router/', include(router.urls)),

    # Custom endpoints
    path('orders/create/', CreateOrderView.as_view(), name='create_order'),
    path('orders/<int:order_id>/update-status/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('<int:payment_id>/update-status/', UpdatePaymentStatusView.as_view(), name='update_payment_status'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),
]