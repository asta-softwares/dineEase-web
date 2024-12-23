import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from .models import Restaurant
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

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

def reauth(request):
    return HttpResponse("Please retry onboarding by clicking the link again.")

def success(request):
    return HttpResponse("Stripe account connected successfully!")
