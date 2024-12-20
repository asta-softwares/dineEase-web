from rest_framework import viewsets, status
from .models import Order, OrderItem, Payment, Promo, PromoUsage, Menu
from .serializers import OrderSerializer, PaymentSerializer
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

stripe_status_mapping = {
    'requires_payment_method': 'pending',
    'requires_confirmation': 'pending',
    'requires_action': 'pending',
    'processing': 'pending',
    'requires_capture': 'pending',
    'succeeded': 'completed',
    'canceled': 'failed',
    'failed': 'failed',
    'refunded': 'refunded',
}

class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing order instances.
    """
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally filter orders by the authenticated user or other criteria.
        """
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(customer=user)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related('order')
    serializer_class = PaymentSerializer

class CreateOrderView(APIView):
    @transaction.atomic
    def post(self, request):
        """
        Creates an order, initializes payment, and tracks promo usage.
        """
        try:
            data = request.data
            customer = request.user
            promo_id = data.get('promo_id')
            owner_id = data['owner_id']

            # Validate Promo
            promo = None
            if promo_id:
                promo = Promo.objects.get(id=promo_id)

                # Check if the promo is still valid
                if not promo.can_be_used():
                    return Response({"error": "Promo cannot be used"}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the customer has already used this promo
                existing_usage = PromoUsage.objects.filter(promo=promo, customer=customer).first()
                if existing_usage and existing_usage.status == 'approved':
                    return Response({"error": "Promo has already been used and approved"}, status=status.HTTP_400_BAD_REQUEST)

            # Create the Order
            order = Order.objects.create(
                customer=customer,
                restaurant_id=data['restaurant_id'],
                promo=promo,
                order_total=data['order_total'],
                status='pending',  # Always pending until payment is approved
                is_delivery=data['is_delivery'],
                order_type=data['order_type'],
                delivery_address=data.get('delivery_address', ''),
                tax=data['tax'],
                tip=data['tip']
            )

            # Add Order Items
            for item in data['menu_items']:
                menu_item = Menu.objects.get(id=item['menu_item_id'])
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=item['quantity'],
                    price=menu_item.cost,
                    special_instructions=item.get('special_instructions', '')
                )

            # Record Promo Usage
            if promo:
                PromoUsage.objects.create(promo=promo, customer=customer, status='pending')

            # Create Payment
            stripe_status = data['payment']['payment_status']
            payment_status = stripe_status_mapping.get(stripe_status, 'pending')

            payment = Payment.objects.create(
                order=order,
                payment_method=data['payment']['payment_method'],
                payment_status=payment_status,
                amount_paid=data['payment']['amount_paid'],
                payment_gateway=data['payment']['payment_gateway'],
                transaction_id=data['payment']['transaction_id']
            )

            # Send WebSocket notification to the user
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"restaurant_{owner_id}",
                {
                    'type': 'send_new_order',
                    'order_id': order.id,
                    'status': order.status,
                    'order_details': {
                        'customer': customer.username,
                        'total': order.order_total,
                        'order_time': order.created_at.isoformat(),
                    }
                }
            )

            return Response({
                "order_id": order.id,
                "payment_id": payment.id,
                "message": "Order created successfully. Awaiting payment approval."
            }, status=status.HTTP_201_CREATED)

        except Promo.DoesNotExist:
            return Response({"error": "Invalid promo"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
class UpdatePaymentStatusView(APIView):
    def post(self, request, payment_id):
        """
        Update the payment status and confirm the order if payment is successful.
        """
        try:
            # Retrieve the payment
            payment = Payment.objects.get(id=payment_id)

            # Get the new payment status from the request
            new_status = request.data.get("payment_status")
            if new_status not in ["pending", "completed", "failed", "refunded"]:
                return Response({"error": "Invalid payment status"}, status=status.HTTP_400_BAD_REQUEST)

            # Update the payment status
            payment.payment_status = new_status
            payment.save()

            # If the payment is completed, update the order status
            if new_status == "completed":
                order = payment.order
                order.status = "confirmed"
                order.save()

                # Approve the promo usage if applicable
                if order.promo:
                    promo_usage = PromoUsage.objects.filter(promo=order.promo, customer=order.customer, status="pending").first()
                    if promo_usage:
                        promo_usage.status = "approved"
                        promo_usage.save()

                return Response({"message": "Payment approved and order confirmed"}, status=status.HTTP_200_OK)

            # If payment failed, reject the order
            elif new_status == "failed":
                order = payment.order
                order.status = "cancelled"
                order.save()

                # Reject the promo usage if applicable
                if order.promo:
                    promo_usage = PromoUsage.objects.filter(promo=order.promo, customer=order.customer, status="pending").first()
                    if promo_usage:
                        promo_usage.status = "rejected"
                        promo_usage.save()

                return Response({"message": "Payment failed and order cancelled"}, status=status.HTTP_200_OK)

            return Response({"message": "Payment status updated successfully"}, status=status.HTTP_200_OK)

        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateOrderStatusView(APIView):
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            if order.status == "pending" and hasattr(order, "payment"):
                if order.payment.payment_status != "completed":
                    return Response({"error": "Cannot accept order. Payment is not approved."}, status=status.HTTP_400_BAD_REQUEST)

            action = request.data.get("action")
            if action not in ["accept", "reject", "complete"]:
                return Response({"error": "Invalid action. Use 'accept', 'reject', or 'complete'."}, status=status.HTTP_400_BAD_REQUEST)

            if action == "accept":
                order.status = "confirmed"
                message = "Your order has been accepted!"
            elif action == "reject":
                order.status = "cancelled"
                message = "Your order has been rejected."
            elif action == "complete":
                order.status = "completed"
                message = "Your order has been completed."

            order.save()

            # Send notification to the user
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"order_{order.customer.id}",
                {
                    'type': 'send_order_status',
                    'message': message,
                    'status': order.status
                }
            )

            return Response({"message": f"Order {action}ed successfully"}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

from django.conf import settings
import stripe
from rest_framework.decorators import api_view
stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
def create_payment_intent(request):
    try:
        amount = int(request.data.get('amount'))  # Amount in cents
        currency = 'usd'  # Change the currency as needed

        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={'integration_check': 'accept_a_payment'}
        )

        return Response({'clientSecret': payment_intent.client_secret}, status=status.HTTP_200_OK)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def refund_payment(request):
    try:
        payment_intent_id = request.data.get('payment_intent_id')
        refund = stripe.Refund.create(payment_intent=payment_intent_id)
        return Response({'message': 'Refund successful', 'refund': refund}, status=status.HTTP_200_OK)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)