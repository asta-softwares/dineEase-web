<script setup>
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle, ExternalLink } from 'lucide-vue-next'
import { useApiEndpoints } from '@/composables/useApiRestaurants'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const { createStripeOnboardingLink, createDashboardLink } = useApiEndpoints()

const restaurantId = computed(() => userStore.user.active_restaurant.id)
const stripeAccountId = computed(() => userStore.user.active_restaurant.stripe_account_id)

const handleStripeOnboarding = async () => {
  if (!restaurantId.value) return;

  const { success, onboardingUrl } = await createStripeOnboardingLink(restaurantId.value);

  if (success && onboardingUrl) {
    window.location.href = onboardingUrl;
  }
};

const handleDashboardLink = async () => {
  if (!restaurantId.value) return;

  const { success, dashboardUrl, error, onboardingUrl } = await createDashboardLink(restaurantId.value);

  if (success && dashboardUrl) {
    window.location.href = dashboardUrl;
  } else if (onboardingUrl) {
    // If onboarding is incomplete, redirect to onboarding
    alert('Onboarding incomplete. Redirecting to complete setup.');
    window.location.href = onboardingUrl;
  } else {
    console.error('Failed to generate dashboard or onboarding link:', error);
    alert('Unable to access the Stripe dashboard. Please try again later.');
  }
};
</script>

<template>
  <div v-if="!stripeAccountId">
    <Alert variant="destructive">
      <AlertCircle class="w-4 h-4" />
      <AlertTitle>Stripe Account Not Active</AlertTitle>
      <AlertDescription>
        If you want your restaurant to be published, you need to connect your Stripe account with DineEase. 
        <a href="#" @click.prevent="handleStripeOnboarding" class="text-blue-500 underline">
          Click here to setup.
        </a>
      </AlertDescription>
    </Alert>
  </div>

  <div v-if="stripeAccountId">
    <Alert variant="primary">
      <AlertCircle class="w-4 h-4" />
      <AlertTitle>Your Stripe account is active.</AlertTitle>
      <AlertDescription>
        You can access your <a href="#" @click.prevent="handleDashboardLink" class="text-blue-500 underline">
          Stripe Dashboard
        </a> to manage your account.
      </AlertDescription>
    </Alert>
  </div>
</template>
