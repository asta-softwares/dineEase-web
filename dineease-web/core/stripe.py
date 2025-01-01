import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Restaurant
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_onboarding_link(request, restaurant_id):
    try:
        # Fetch the restaurant from the database
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)

        # Create a Stripe Standard connected account if not already created
        if not restaurant.stripe_account_id:
            account = stripe.Account.create(type='standard')
            restaurant.stripe_account_id = account.id
            restaurant.save()
        else:
            account = stripe.Account.retrieve(restaurant.stripe_account_id)

        # Create an onboarding link
        account_link = stripe.AccountLink.create(
            account=account.id,
            refresh_url=request.build_absolute_uri('/reauth/'),
            return_url=request.build_absolute_uri(f'/stripe-success?restaurant_id={restaurant_id}'),
            type='account_onboarding'
        )

        return JsonResponse({'onboarding_url': account_link.url})

    except Restaurant.DoesNotExist:
        return JsonResponse({'error': 'Restaurant not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
def create_customer_portal_session(request):
    """
    Generate a customer portal session for Stripe.
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'User must be authenticated to access the customer portal.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create the Stripe customer for the authenticated user
        email = user.email
        customers = stripe.Customer.list(email=email, limit=1)
        if customers.data:
            customer = customers.data[0]
        else:
            profile = getattr(user, 'profile', None)
            if not profile:
                return Response({'error': 'User profile not found.'}, status=status.HTTP_400_BAD_REQUEST)
            customer = stripe.Customer.create(
                email=email,
                name=f"{user.first_name} {user.last_name}".strip(),
                phone=profile.phone,
                address={
                    'line1': profile.address,
                    'city': profile.city,
                    'state': profile.province,
                    'country': 'CA',
                },
                metadata={'integration_check': 'accept_a_payment'},
            )

        # Create a customer portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=customer.id,
            return_url=request.build_absolute_uri('/dashboard/')  # Redirect after portal session ends
        )

        return Response({'url': portal_session.url}, status=status.HTTP_200_OK)
    except stripe.error.StripeError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def reauth(request):
    return HttpResponse("Please retry onboarding by clicking the link again.")

def success(request):
    return HttpResponse("Stripe account connected successfully!")
