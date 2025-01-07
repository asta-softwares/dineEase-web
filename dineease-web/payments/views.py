import requests
import stripe
from rest_framework import viewsets, status
from .models import Order, OrderItem, Payment, Promo, PromoUsage, Menu, Restaurant
from .serializers import OrderSerializer, PaymentSerializer, OrderPreviewSerializer
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.pagination import PageNumberPagination
from decimal import Decimal
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
from .filters import OrderFilter
from django_filters.rest_framework import DjangoFilterBackend
from .utils import send_push_notification

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

class OrderPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 100

class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for viewing and editing order instances.
    """
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_queryset(self):
        """
        Optionally filter orders by the authenticated user.
        """
        user = self.request.user
        queryset = super().get_queryset()

        # Filter by user type
        if user.profile.type_of_user == 'admin':
            queryset = Order.objects.all()
        elif user.profile.type_of_user == 'restaurant_owner':
            queryset = Order.objects.filter(restaurant__owner=user)
        else:
            queryset = Order.objects.filter(customer=user)

        return queryset

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all().select_related('order')
    serializer_class = PaymentSerializer

class OrderPreviewAPI(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = OrderPreviewSerializer(data=request.data)
        if serializer.is_valid():
            totals = serializer.calculate_totals()
            return Response(totals, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CreateOrderView(APIView):
    @transaction.atomic
    def post(self, request):
        """
        Creates an order, initializes payment, and tracks promo usage.
        """
        try:
            data = request.data
            customer = request.user
            promo_ids = data.get('promo_ids', [])
            owner_id = data['owner_id']
            payment_id = data['transaction_id']

            # Validate Promos
            promos = Promo.objects.filter(id__in=promo_ids, status='active')
            if len(promo_ids) != promos.count():
                return Response({"error": "One or more promos are invalid or inactive."}, status=status.HTTP_400_BAD_REQUEST)

            # Check Promo Usage
            invalid_promos = PromoUsage.objects.filter(
                promo__in=promos, customer=customer, status='approved'
            )
            if invalid_promos.exists():
                return Response({"error": "Some promos have already been used."}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate Order Total from Menu Items
            order_total = 0
            for item in data['menu_items']:
                try:
                    menu_item = Menu.objects.get(id=item['menu_item_id'])
                    order_total += menu_item.cost * item['quantity']
                except Menu.DoesNotExist:
                    return Response({"error": f"Menu item {item['menu_item_id']} does not exist."}, status=status.HTTP_400_BAD_REQUEST)

            # Create the Order
            order = Order.objects.create(
                customer=customer,
                restaurant_id=data['restaurant_id'],
                order_total=order_total,  # Base order total before discounts
                status='pending',  # Always pending until payment is approved
                is_delivery=data.get('is_delivery', False),
                order_type=data.get('order_type', 'dine_in'),
                delivery_address=data.get('delivery_address', ''),
                tip=data.get('tip', 0.0)
            )

            # Attach Promos to Order
            order.promos.set(promos)

            # Add Order Items
            for item in data['menu_items']:
                OrderItem.objects.create(
                    order=order,
                    menu_item=Menu.objects.get(id=item['menu_item_id']),
                    quantity=item['quantity'],
                    price=menu_item.cost,
                    special_instructions=item.get('special_instructions', '')
                )

            # Record Promo Usage
            PromoUsage.objects.bulk_create([
                PromoUsage(promo=promo, customer=customer, status='pending') for promo in promos
            ])

            # Final Save to Calculate Totals
            order.save()

            # if Decimal(data['payment']['amount_paid']) < order.total:
            #     return Response({"error": "Amount paid is less than the total order amount."}, status=status.HTTP_400_BAD_REQUEST)

             # Fetch Payment Details from Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_id)
            payment_method_details = stripe.PaymentMethod.retrieve(payment_intent.payment_method)
            card_details = payment_method_details['card']

            # Create Payment with card details and Stripe data
            payment = Payment.objects.create(
                order=order,
                payment_method=payment_intent.payment_method_types[0],  # e.g., "card"
                payment_status=stripe_status_mapping.get(payment_intent.status, 'pending'),
                amount_paid=Decimal(payment_intent.amount_received) / 100,  # Convert cents to dollars
                payment_gateway='stripe',
                transaction_id=payment_intent.id,
                card_brand=card_details['brand'],
                card_last4=card_details['last4'],
                card_exp_month=card_details['exp_month'],
                card_exp_year=card_details['exp_year'],
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
                        'total': float(order.total),
                        'order_time': order.created_at.isoformat(),
                    }
                }
            )

            # Send push notification
            if hasattr(customer, 'profile') and customer.profile.notification_token:
                restaurant_name = order.restaurant.name if order.restaurant else "Unknown Restaurant"
                title = f"Order Created at {restaurant_name}"
                message = (
                    f"Your order at {restaurant_name} has been created successfully and is awaiting approval."
                )
                send_push_notification(
                    customer.profile.notification_token,
                    title,
                    message,
                    data={"order_id": order.id, "status": order.status}
                )

            return Response({
                "order_id": order.id,
                "order": OrderSerializer(order).data,
                "verification_code": order.verification_code.code,
                "payment_id": payment.id,
                "message": "Order created successfully. Awaiting payment approval."
            }, status=status.HTTP_201_CREATED)

        except Restaurant.DoesNotExist:
            return Response({"error": "Invalid restaurant ID."}, status=status.HTTP_400_BAD_REQUEST)
        except Promo.DoesNotExist:
            return Response({"error": "Invalid promo ID."}, status=status.HTTP_400_BAD_REQUEST)
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
            restaurant_name = order.restaurant.name if order.restaurant else "Unknown Restaurant"

            if order.status == "pending" and hasattr(order, "payment"):
                if order.payment.payment_status != "completed":
                    return Response({"error": "Cannot accept order. Payment is not approved."}, status=status.HTTP_400_BAD_REQUEST)

            action = request.data.get("action")
            if action not in ["accept", "reject", "complete"]:
                return Response({"error": "Invalid action. Use 'accept', 'reject', or 'complete'."}, status=status.HTTP_400_BAD_REQUEST)

            if action == "accept":
                order.status = "confirmed"
                title = f"{restaurant_name} Order Accepted"
                message = "Your order has been accepted and is now being prepared."
            elif action == "reject":
                order.status = "cancelled"
                title = f"{restaurant_name} Order Rejected"
                message = "Unfortunately, your order has been rejected. Please contact the restaurant for more details."
            elif action == "complete":
                # Require and validate verification code
                verification_code = request.data.get("verification_code")
                if not verification_code:
                    return Response({"error": "Verification code is required to complete the order."}, status=status.HTTP_400_BAD_REQUEST)

                if not order.verification_code or order.verification_code.code != verification_code:
                    return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

                # Update order status
                order.status = "completed"
                title = f"{restaurant_name} Order Completed"
                message = "Your order has been completed successfully. Thank you for choosing our service!"
                order.save()

                order.verification_code.delete()
            else:
                order.status = "pending"
                title = f"{restaurant_name} Order Update"
                message = "There is an update on your order. Please check for more details."

            # Save the order for "accept" and "reject" actions
            if action in ["accept", "reject"]:
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

            # Push notification using Expo Push Notification API
            if hasattr(order.customer, 'profile') and order.customer.profile.notification_token:
                notification_token = order.customer.profile.notification_token
                payload = {
                    "to": notification_token,
                    "title": title,
                    "body": message,
                    "data": {
                        "order_id": order.id,
                        "status": order.status,
                        "restaurant_id": order.restaurant.id,
                    }
                }
                headers = {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                }
                response = requests.post("https://exp.host/--/api/v2/push/send", json=payload, headers=headers)

                # Log response for debugging
                if response.status_code != 200:
                    print(f"Expo notification failed: {response.text}")

            return Response({"message": title}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_payment_intent(request):
    try:
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'User must be authenticated to create a payment intent.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Validate and calculate totals using OrderPreviewSerializer
        serializer = OrderPreviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        totals = serializer.calculate_totals()
        restaurant_payment = totals['restaurant_payment']
        platform_revenue = totals['platform_revenue']
        amount_cents = int(totals['total'] * 100)  # Convert total to cents for Stripe

        # Get customer details
        email = user.email
        profile = getattr(user, 'profile', None)
        if not profile:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Get restaurant details
        restaurant = serializer.validated_data['restaurant']

        # Create or retrieve Stripe customer
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            customer = customers.data[0]
        else:
            customer_data = {
                'email': email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'phone': profile.phone,
                'address': {
                    'line1': profile.address,
                    'city': profile.city,
                    'state': profile.province,
                    'country': 'CA',
                },
                'metadata': {'integration_check': 'accept_a_payment'},
            }
            customer = stripe.Customer.create(**customer_data)

        # Determine payment destination (restaurant's wallet or default)
        transfer_data = None
        if restaurant.stripe_account_id:
            transfer_data = {
                'destination': restaurant.stripe_account_id,
                'amount': int(restaurant_payment * 100),  # Convert to cents
            }

        # Create PaymentIntent
        payment_intent = stripe.PaymentIntent.create(
            customer=customer.id,
            setup_future_usage='off_session',
            amount=amount_cents,
            currency='cad',
            receipt_email=email,
            metadata={
                'integration_check': 'accept_a_payment',
                'user_id': user.id,
                'user_email': email,
                'restaurant_id': restaurant.id,
                'restaurant_name': restaurant.name,
                'platform_revenue': str(platform_revenue),  # Include platform revenue in metadata
            },
            transfer_data=transfer_data,  # Route payment to the restaurant if stripe_account_id exists
        )

        # Generate ephemeral key for client-side operations
        ephemeral_key = stripe.EphemeralKey.create(
            customer=customer.id,
            stripe_version='2022-11-15',
        )

        return Response({
            'clientSecret': payment_intent.client_secret,
            'customerId': customer.id,
            'ephemeralKey': ephemeral_key.secret,
            'totals': totals,  # Return calculated totals for client reference
        }, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError) as e:
        return Response({'error': 'Invalid amount provided.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def get_payment_methods(request):
    """
    Retrieve saved payment methods (cards) for the authenticated user.
    """
    try:
        # Ensure the user is authenticated
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'User must be authenticated to retrieve payment methods.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get the email from request parameters, fallback to user's email
        email = request.query_params.get('email', user.email)

        # Retrieve the user's Stripe customer object
        customers = stripe.Customer.list(email=email, limit=1)
        if not customers.data:
            return Response({'payment_methods': []}, status=status.HTTP_200_OK)  # No customer found, return empty list
        
        customer = customers.data[0]  # Get the first matched customer

        # Retrieve saved payment methods (cards) for the Stripe customer
        payment_methods = stripe.PaymentMethod.list(
            customer=customer.id,
            type='card'
        )

        # Format the payment methods
        formatted_methods = [
            {
                'id': pm.id,
                'brand': pm.card.brand,
                'last4': pm.card.last4,
                'exp_month': pm.card.exp_month,
                'exp_year': pm.card.exp_year
            }
            for pm in payment_methods.data
        ]

        return Response({'payment_methods': formatted_methods}, status=status.HTTP_200_OK)
    
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
def create_setup_intent(request):
    """
    Create a Stripe Setup Intent and ensure customer email exists in Stripe.
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return Response({"error": "User must be authenticated to save a payment method."}, status=status.HTTP_403_FORBIDDEN)
        
        # Retrieve or create Stripe customer
        customers = stripe.Customer.list(email=user.email, limit=1)
        if customers.data:
            customer = customers.data[0]
            # Ensure customer email exists; if not, update it
            if not customer.get("email"):
                stripe.Customer.modify(
                    customer.id,
                    email=user.email,
                    name=f"{user.first_name} {user.last_name}"
                )
        else:
            # Create a new customer if not found
            customer = stripe.Customer.create(
                email=user.email,
                name=f"{user.first_name} {user.last_name}"
            )

        # Create Setup Intent
        setup_intent = stripe.SetupIntent.create(
            customer=customer.id,
            payment_method_types=["card"],
            metadata={"user_id": user.id}
        )

        return Response({"clientSecret": setup_intent.client_secret}, status=status.HTTP_200_OK)

    except stripe.error.StripeError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
@api_view(['POST'])
def refund_payment(request):
    try:
        payment_intent_id = request.data.get('payment_intent_id')
        refund = stripe.Refund.create(payment_intent=payment_intent_id)
        return Response({'message': 'Refund successful', 'refund': refund}, status=status.HTTP_200_OK)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)