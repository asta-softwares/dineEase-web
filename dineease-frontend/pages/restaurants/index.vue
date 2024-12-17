<template>
  <div class="flex-col flex">
    <div v-if="restaurants.length" class="flex items-center justify-between space-y-2 mb-4">
      <h2 class="text-3xl font-bold tracking-tight">
        Restaurant List
      </h2>
      <div class="ml-auto">
        <Button @click="handleAddRestaurant">
          <CirclePlus class="mr-2 h-4 w-4" />
          Add Restaurant
        </Button>
      </div>
    </div>

    <div v-if="restaurants.length === 0" class="flex flex-col items-center justify-center p-8">
      <img src="/images/product.svg" alt="No Restaurant" class="w-64 h-64" />
      <h1 class="text-2xl font-semibold">No Restaurants Available</h1>
      <span class="text-gray-500 mb-4">Start by adding your first restaurant to manage your listings.</span>
      <Button @click="handleAddRestaurant">
        <CirclePlus class="mr-2 h-4 w-4" />
        Add Restaurant
      </Button>
    </div>

    <CardItems v-else :items="restaurants" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CardItems from '@/components/CardItems.vue'
import { useApiEndpoints } from '@/composables/useApiRestaurants.js'
import { CirclePlus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'

const restaurants = ref([])
const { fetchRestaurants } = useApiEndpoints()

// Fetch data when the component mounts
onMounted(async () => {
  try {
    restaurants.value = await fetchRestaurants()
    console.log("rest", restaurants.value)
  } catch (error) {
    console.error("Error fetching data:", error)
  }
})

// Handler for adding a restaurant
const handleAddRestaurant = () => {
  window.location.href = '/restaurants/create'
}
</script>
