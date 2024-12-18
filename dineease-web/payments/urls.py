from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, PaymentViewSet, CreateOrderView, UpdatePaymentStatusView, UpdateOrderStatusView
from .webhooks import stripe_webhook
from .views import create_payment_intent, refund_payment

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('order-create/', CreateOrderView.as_view(), name='create_order'),
    path('update-order-status/<int:order_id>/', UpdateOrderStatusView.as_view(), name='update_order_status'),
    path('payments/<int:payment_id>/update-status/', UpdatePaymentStatusView.as_view(), name='update_payment_status'),
    path('stripe/webhook/', stripe_webhook, name='stripe_webhook'),

    path('create-payment-intent/', create_payment_intent, name='create-payment-intent'),
    path('refund-payment/', refund_payment, name='refund-payment'),
]
