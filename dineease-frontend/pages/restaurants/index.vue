<template>
    <div class="flex-col flex">
      <div class="flex items-center justify-between space-y-2 p-4">
        <h2 class="text-3xl font-bold tracking-tight">
          Restaurant List
        </h2>
        <div class="ml-auto">
          <Button>
              <CirclePlus class="mr-2 h-4 w-4" />
              Add Restaurant
          </Button>
      </div>
      </div>
      <CardItems :items="restaurants"/>
    </div>
  </template>
  
  <script setup>
  import CardItems from '@/components/CardItems.vue'
  import { useApiEndpoints } from '@/composables/useApiRestaurants.js'
  import { useOrderActions } from '~/composables/orderTest.js'
  import { CirclePlus } from 'lucide-vue-next'
  
  const restaurants = ref([])
  const promos = ref([])
  const menus = ref([])
  const { fetchRestaurants, fetchPromos, fetchMenus } = useApiEndpoints()
  
  // Fetch data when the component mounts
  onMounted(async () => {
    try {
      restaurants.value = await fetchRestaurants()
    } catch (error) {
      console.error("Error fetching data:", error)
    }
  })
  </script>
  