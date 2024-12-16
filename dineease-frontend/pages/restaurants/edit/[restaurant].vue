<template>
  <div>
    <div v-if="pending" class="loading-container">Loading...</div>
    <div v-else-if="error" class="error-container">Error loading restaurant: {{ error }}</div>
    <div v-else>
      <h2 class="text-2xl font-bold mb-4">Edit Restaurant Details</h2>
      <BreadcrumbNav :items="breadcrumbItems" />
      <RestaurantForm class="mt-4" :initial-data="restaurant" :is-edit-mode="isEditMode" @submit="updateRestaurant" />
    </div>
  </div>
</template>

<script setup>
import { useApiEndpoints } from '@/composables/useApiRestaurants'
import RestaurantForm from '@/components/Forms/RestaurantForm'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { toast } from '@/components/ui/toast'

// Fetch restaurant data
const { fetchRestaurantById, editRestaurant } = useApiEndpoints()
const route = useRoute()
const router = useRouter()
const isEditMode = !!route.params.restaurant

const { data: restaurant, pending, error } = await useAsyncData(
  `restaurant-${route.params.restaurant}`,
  () => fetchRestaurantById(route.params.restaurant)
)

// Make breadcrumbItems reactive
const breadcrumbItems = ref([
  { label: 'Home', href: '/' },
  { label: 'Loading...', href: '#' },
  { label: 'Edit Details' },
])

// Update breadcrumbItems when restaurant data is available
watchEffect(() => {
  if (restaurant.value) {
    breadcrumbItems.value = [
      { label: 'Dashboard', href: '/' },
      { label: 'Restaurant List', href: '/restaurants' },
      { label: restaurant.value.name || 'Name', href: `/restaurants/${restaurant.value.id}` },
      { label: 'Edit Restaurant Details' },
    ]
  }
})

// Function to handle restaurant update
const updateRestaurant = async (formData) => {
  try {
    let action = 'created'
    let restaurantName = formData.get('name') || 'Restaurant'

    if (isEditMode) {
      await editRestaurant(route.params.restaurant, formData)
      action = 'updated'
    }
    // Redirect to the restaurants page
    router.push(`/restaurants/${route.params.restaurant}`)

    // Show success toast notification
    toast({
      title: `Restaurant ${action.charAt(0).toUpperCase() + action.slice(1)} Successfully`,
      description: `The restaurant "${restaurantName}" has been ${action}.`,
      variant: 'success',
      position: 'center',
    })
  } catch (error) {
    console.error('Error updating restaurant:', error)

    // Show error toast notification
    toast({
      title: 'Error Saving Restaurant',
      description: 'An error occurred while saving the restaurant. Please try again.',
      variant: 'destructive',
      position: 'center',
    })
  }
}
</script>
