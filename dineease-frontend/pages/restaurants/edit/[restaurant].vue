<template>
  <div>
    <div v-if="pending" class="loading-container">Loading...</div>
    <div v-else-if="error" class="error-container">Error loading restaurant: {{ error }}</div>
    <div v-else>
      <h2 class="text-2xl font-bold mb-4">Edit Restaurant Details</h2>
      <BreadcrumbNav :items="breadcrumbItems" />
      <RestaurantForm class="mt-4" :initial-data="restaurant" @submit="updateRestaurant" />
    </div>
  </div>
</template>

<script setup>
import { useApiEndpoints } from '@/composables/useApiRestaurants'
import RestaurantForm from '@/components/Forms/RestaurantForm.vue'
import BreadcrumbNav from '@/components/BreadcrumbNav.vue'

// Fetch restaurant data
const { fetchRestaurantById, editRestaurant } = useApiEndpoints()
const route = useRoute()
const router = useRouter()

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
      { label: restaurant.value.name || 'Name', href: `/restaurants/${restaurant.value.id}` },
      { label: 'Edit Restaurant Details' },
    ]
  }
})

// Function to handle restaurant update
const updateRestaurant = async (formData) => {
  try {
    await editRestaurant(route.params.restaurant, formData)
    router.push('/restaurants')
  } catch (error) {
    console.error('Error updating restaurant:', error)
  }
}
</script>
