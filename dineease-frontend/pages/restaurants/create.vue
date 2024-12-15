<template>
    <div>
      <h2 class="text-2xl font-bold mb-4">Create Restaurant</h2>
  
      <RestaurantForm @submit="handleCreateRestaurant" />
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants'
  import RestaurantForm from '@/components/Forms/RestaurantForm.vue'
  
  const { editRestaurant } = useApiEndpoints()
  const router = useRouter()
  
  const handleCreateRestaurant = async (formData) => {
    try {
      await editRestaurant(formData)
      router.push('/restaurants')
    } catch (error) {
      console.error('Error creating restaurant:', error)
    }
  }
  </script>
  