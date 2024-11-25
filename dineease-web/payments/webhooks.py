from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from .models import Payment, Order
from django.conf import settings

# Set your Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        # Verify the webhook signature
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        # Invalid payload
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        transaction_id = payment_intent['id']

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.payment_status = 'completed'
            payment.save()
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)

    elif event['type'] == 'charge.refunded':
        refund = event['data']['object']
        payment_intent = refund['payment_intent']

        try:
            payment = Payment.objects.get(transaction_id=payment_intent)
            payment.payment_status = 'refunded'
            payment.save()
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)

    # Add other event handlers as needed

    return JsonResponse({"status": "success"}, status=200)
