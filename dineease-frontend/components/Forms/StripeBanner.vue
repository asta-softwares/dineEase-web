<script setup>
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { AlertCircle, ExternalLink } from 'lucide-vue-next'
import { useApiEndpoints } from '@/composables/useApiRestaurants'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const { createStripeOnboardingLink } = useApiEndpoints()

const restaurantId = computed(() => userStore.user.active_restaurant.id)
const stripeAccountId = computed(() => userStore.user.active_restaurant.stripe_account_id)

const handleStripeOnboarding = async () => {
  if (!restaurantId.value) return;

  const { success, onboardingUrl } = await createStripeOnboardingLink(restaurantId.value);

  if (success && onboardingUrl) {
    window.location.href = onboardingUrl;
  }
};

</script>

<template>
  <div v-if="!stripeAccountId" class="mb-4">
    <Alert variant="destructive">
      <AlertCircle class="w-4 h-4" />
      <AlertTitle>Stripe Account Not Active</AlertTitle>
      <AlertDescription>
        If you want your restaurant to be published, you need to connect your Stripe account with DineEase. 
        <a href="#" @click.prevent="handleStripeOnboarding" class="text-blue-500 underline">
          Click here to register.
        </a>
      </AlertDescription>
    </Alert>
  </div>

  <div v-if="stripeAccountId" class="text-green-500">
    <Alert variant="primary">
      <AlertCircle class="w-4 h-4" />
      <AlertTitle>Your Stripe account is active.</AlertTitle>
    </Alert>
  </div>
</template>
