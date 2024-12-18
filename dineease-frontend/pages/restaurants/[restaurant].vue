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
        <BreadcrumbNav :items="breadcrumbItems" />
        <div class="border p-4 rounded-lg flex flex-col gap-4">
          <div class="flex items-start gap-4">
            <img
              :src="restaurant.image"
              :alt="restaurant.name"
              class="w-[150px] h-[150px] rounded-md object-cover"
            />
            <div class="flex flex-col gap-2">
              <!-- Breadcrumb Navigation -->
              <div class="flex items-center gap-2 text-sm text-gray-600">
                <BreadcrumbNav :items="categories" :separator="Dot" />
              </div>
      
              <!-- Restaurant Name -->
              <div class="flex items-center gap-x-4">
                <h1 class="text-2xl font-bold">{{ restaurant.name }}</h1>
                <NuxtLink
                  :to="`/restaurants/edit/${restaurant.id}`"
                  class="text-xs"
                >
                  <Button type="button" variant="outline" size="sm">
                    Edit
                  </Button>
                </NuxtLink>
              </div>
      
              <!-- Delivery Info -->
              <div class="flex items-center gap-2 text-sm">
                <span class="font-medium">Free delivery</span>
                <span class="line-through text-gray-500">₱29</span>
                <span>• Min. order ₱{{ restaurant.min_order || '0' }}</span>
              </div>

              <!-- Additional Info -->
              <div class="flex flex-wrap gap-4 text-sm">
                <div class="flex items-center gap-1">
                  <Star class="w-4 h-4" />
                  <p>{{ restaurant.ratings }}</p>
                </div>
                <div class="flex items-center gap-1">
                  <Utensils class="w-4 h-4" />
                  <p>{{ restaurant.service_type }}</p>
                </div>
                <div class="flex items-center gap-1">
                  <Phone class="w-4 h-4" />
                  <p>{{ restaurant.telephone }}</p>
                </div>
                <div class="flex items-center gap-1">
                  <Mail class="w-4 h-4" />
                  <p>{{ restaurant.email || 'N/A' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Menus -->
        <div v-if="restaurant.menus.length" class="p-4 border rounded-lg">
          <h2 class="text-lg font-semibold mb-2">Menu</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="menu in restaurant.menus"
              :key="menu.id"
              class="flex items-start justify-between gap-4 p-2 border rounded-lg shadow-sm"
            >
              <img
                :src="menu.images[0]?.image"
                alt="Menu Image"
                class="w-24 h-24 rounded-md object-cover"
              />
              <div class="flex flex-col">
                <p class="flex  items-center font-bold mb-1">
                  {{ menu.name }}
                  <NuxtLink
                    :to="`/menus/edit/${menu.id}`"
                    class="text-xs mt-2 ml-auto"
                  >
                    <Button type="button" variant="outline" size="sm">
                      Edit
                    </Button>
                  </NuxtLink>
                </p>
                <p class="text-sm text-gray-600 mb-1">from ₱{{ menu.cost }}</p>
                <p class="text-sm text-gray-500">{{ menu.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Promos -->
        <div v-if="restaurant.promos.length" class="p-4 border rounded-lg">
          <h2 class="text-lg font-semibold mb-2">Promos</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div
              v-for="promo in restaurant.promos"
              :key="promo.id"
              class="flex items-start justify-between gap-4 p-2 border rounded-lg shadow-sm"
            >
              <div class="flex flex-col flex-1">
                <!-- Promo Name and Edit Button -->
                <p class="flex items-center font-bold mb-1">
                  {{ promo.name }}
                  <NuxtLink
                  :to="`/promos/edit/${promo.id}`"
                  class="text-xs mt-2 ml-auto"
                >
                  <Button type="button" variant="outline" size="sm">
                    Edit
                  </Button>
                </NuxtLink>
                </p>
      
                <!-- Promo Description -->
                <p class="text-sm text-gray-600 mb-1">{{ promo.description }}</p>
      
                <!-- Promo Details (Discount, Minimum Order, Code) -->
                <div class="flex gap-2 text-xs text-gray-500 mb-2">
                  <p><strong>Discount:</strong> {{ promo.discount }}%</p>
                  <p><strong>Min Order:</strong> ₱{{ promo.minimum_order }}</p>
                  <p><strong>Code:</strong> {{ promo.code }}</p>
                </div>
      
                <!-- Time Offer (Day and Time) -->
                <div class="flex flex-wrap gap-2 mt-2">
                  <Badge
                    v-for="(time, day) in sortedOperatingHours(promo.time_offer)"
                    :key="day"
                    variant="outline"
                  >
                    {{ day }}: {{ time }}
                  </Badge>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Operating Hours -->
        <div class="p-4 border rounded-lg">
          <h2 class="text-lg font-semibold">Operating Hours</h2>
          <div class="grid grid-cols-2 gap-2 mt-2">
            <div v-for="(hours, day) in sortedOperatingHours(restaurant.operating_hours)" :key="day" class="flex items-center gap-2 text-xs">
              <p class="font-medium w-32">{{ day }}:</p>
              <Badge class="w-[150px] text-center" variant="outline"> {{ hours }} </Badge>
            </div>
          </div>
        </div>

        <!-- Mapbox Map for Coordinates -->
        <div v-if="coordinates" class="w-full">
          <h2 class="flex items-center gap-1 text-lg font-semibold">
            <MapPin class="w-4 h-4" />
            {{ restaurant.location }}
          </h2>
          <MiniMap class="h-[500px] my-4" :coordinates="coordinates" :rounded="true" />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants.js'
  import MiniMap from '~/components/Maps/MiniMap.vue';
  import BreadcrumbNav from '@/components/BreadcrumbNav.vue';
import { tryOnUnmounted } from '@vueuse/core';
import { Dot, MapPin, Utensils, Phone, Mail, Star } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { sortedOperatingHours } from '~/lib/timeUtils';
  
  const { fetchRestaurantById } = useApiEndpoints()
  const route = useRoute()
  
  // Use asyncData to load the restaurant data
  const { data: restaurant, pending, error } = await useAsyncData(`restaurant-${route.params.restaurant}`, () =>
    fetchRestaurantById(route.params.restaurant)
  )

  const coordinates = computed(() => {
    return restaurant.value?.coordinates || []
})

const breadcrumbItems = ref([
  { label: 'Home', href: '/' },
  { label: 'Loading...', href: '#' },
  { label: 'Edit Details' },
])

// Update breadcrumbItems when restaurant data is available
watchEffect(() => {
  if (restaurant.value) {
    breadcrumbItems.value = [
      { label: 'Home', href: '/' },
      { label: 'Restaurant List', href: `/restaurants/` },
      { label: restaurant.value.name || 'Name' },
    ]
  }
})

const categories = computed(() => {
  return restaurant.value.categories?.map(item => {
    return { label: item.name }
  })
})

  console.log(restaurant)
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
  