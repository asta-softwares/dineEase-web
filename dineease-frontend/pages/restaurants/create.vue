<template>
    <div>
      <h2 class="text-2xl font-bold mb-4">Create Restaurant</h2>
  
      <RestaurantForm :is-edit-mode="false" @submit="handleCreateRestaurant" />
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants'
  import RestaurantForm from '@/components/Forms/RestaurantForm.vue'
  import { toast } from '@/components/ui/toast'
  
  const { createRestaurant } = useApiEndpoints()
  const router = useRouter()

  const handleCreateRestaurant = async (formData) => {
  try {
    let action = 'created'
    let restaurantName = formData.get('name') || 'Restaurant'

    await createRestaurant(formData)
    router.push(`/restaurants/`)

    toast({
      title: `Restaurant ${action.charAt(0).toUpperCase() + action.slice(1)} Successfully`,
      description: `The restaurant "${restaurantName}" has been ${action}.`,
      variant: 'success',
    })
  } catch (error) {
    console.error('Error updating restaurant:', error)

    // Show error toast notification
    toast({
      title: 'Error Creating Restaurant',
      description: 'An error occurred while creating the restaurant. Please try again.',
      variant: 'destructive',
    })
  }
}
  </script>
  