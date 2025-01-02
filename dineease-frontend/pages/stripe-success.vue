<template>
    <div class="flex flex-col items-center justify-center p-6 gap-4 max-w-md mx-auto">
      <h2 class="text-2xl font-bold">Stripe Onboarding Successful!</h2>
      <p v-if="isLoading">Loading...</p>
      <p v-if="errorMessage" class="text-red-500">{{ errorMessage }}</p>
      <p v-if="successMessage" class="text-green-500">{{ successMessage }}</p>
      <Button @click="goToRestaurantForm">Back to Restaurant Page</Button>
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants';
  import { Button } from '@/components/ui/button';

  const { fetchRestaurantById } = useApiEndpoints()
  
  const route = useRoute();
  const router = useRouter();
  
  const isLoading = ref(true);
  const errorMessage = ref('');
  const successMessage = ref('');
  const restaurantId = route.query.restaurant_id;
  
  onMounted(async () => {
    try {
      if (!restaurantId) {
        throw new Error('Restaurant ID not found.');
      }
  
      // Fetch the updated restaurant data
      const restaurant = await fetchRestaurantById(restaurantId);
  
      if (restaurant.stripe_account_id) {
        successMessage.value = 'Your Stripe account is successfully connected!';
      } else {
        throw new Error('Stripe account not found. Please try again.');
      }
    } catch (error) {
      errorMessage.value = error.message;
    } finally {
      isLoading.value = false;
    }
  });
  
  const goToRestaurantForm = () => {
    router.push(`/restaurants/`);
  };
  </script>
  