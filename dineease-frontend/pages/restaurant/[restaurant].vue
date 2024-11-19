<template>
    <div>
      <div v-if="pending" class="loading-container">
        Loading...
      </div>
      <div v-else-if="error" class="error-container">
        <p>Error loading restaurant data: {{ error }}</p>
      </div>
      <div v-else class="flex flex-col gap-4 p-4 pt-0">
        <!-- Restaurant Overview -->
        <div class="border p-4 rounded-lg flex flex-col gap-2">
          <div class="flex items-center gap-4">
            <img :src="restaurant.image" :alt="restaurant.name" class="w-16 h-16 rounded-md object-cover" />
            <div>
              <h1 class="text-xl font-bold">{{ restaurant.name }}</h1>
              <p class="text-xs text-muted-foreground">{{ restaurant.ratings }} ★</p>
            </div>
          </div>
          <p class="text-sm">{{ restaurant.description }}</p>
          <div class="flex gap-2 text-sm text-muted-foreground">
            <p><strong>Location:</strong> {{ restaurant.location }}</p>
            <p><strong>Service Type:</strong> {{ restaurant.service_type }}</p>
          </div>
        </div>
  
        <!-- Operating Hours -->
        <div class="border p-4 rounded-lg">
          <h2 class="text-lg font-semibold">Operating Hours</h2>
          <div class="grid gap-2 mt-2">
            <div v-for="(hours, day) in restaurant.operating_hours" :key="day" class="flex items-center gap-2 text-xs">
              <p class="font-medium">{{ day }}:</p>
              <p class="text-muted-foreground">{{ hours }}</p>
            </div>
          </div>
        </div>
  
        <!-- Promos -->
        <div v-if="restaurant.promos.length" class="border p-4 rounded-lg">
          <h2 class="text-lg font-semibold">Promos</h2>
          <div v-for="promo in restaurant.promos" :key="promo.id" class="flex flex-col gap-2 p-3 rounded-lg border mt-2">
            <p class="font-semibold text-sm">{{ promo.name }}</p>
            <p class="text-xs text-muted-foreground">{{ promo.description }}</p>
            <div class="flex gap-2 text-xs">
              <p><strong>Discount:</strong> {{ promo.discount }}%</p>
              <p><strong>Minimum Order:</strong> ${{ promo.minimum_order }}</p>
              <p><strong>Code:</strong> {{ promo.code }}</p>
            </div>
            <div class="grid gap-1 mt-1 text-muted-foreground text-xs">
              <span v-for="(time, day) in promo.time_offer" :key="day">{{ day }}: {{ time }}</span>
            </div>
          </div>
        </div>
  
        <!-- Menus -->
        <div v-if="restaurant.menus.length" class="border p-4 rounded-lg">
          <h2 class="text-lg font-semibold">Menu</h2>
          <div v-for="menu in restaurant.menus" :key="menu.id" class="flex gap-4 mt-2">
            <img :src="menu.images[0]?.image" alt="Menu Image" class="w-16 h-16 rounded-md object-cover" />
            <div>
              <p class="font-semibold">{{ menu.name }} - ${{ menu.cost }}</p>
              <p class="text-xs text-muted-foreground">{{ menu.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants.js'
  
  const { fetchRestaurantById } = useApiEndpoints()
  const route = useRoute()
  
  // Use asyncData to load the restaurant data
  const { data: restaurant, pending, error } = await useAsyncData(`restaurant-${route.params.restaurant}`, () =>
    fetchRestaurantById(route.params.restaurant)
  )
  </script>
  
  <style scoped>
  .loading-container {
    display: flex;
    justify-content: center;
    margin-top: 20px;
  }
  
  .error-container {
    color: red;
    text-align: center;
    margin-top: 20px;
  }
  </style>
  