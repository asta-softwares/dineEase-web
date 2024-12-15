<template>
    <div class="p-4">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-3xl font-bold tracking-tight">Promo List</h2>
        <div class="ml-auto">
          <Button>
            <CirclePlus class="mr-2 h-4 w-4" />
            Add Promo
          </Button>
        </div>
      </div>
  
      <div v-if="promos.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="promo in promos"
          :key="promo.id"
          class="flex flex-col gap-2 p-4 border rounded-lg shadow-sm"
        >
          <!-- Promo Name and Edit Button -->
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">{{ promo.name }}</h3>
            <Button
              type="button"
              variant="outline"
              size="sm"
              class="text-xs"
              @click="editPromo(promo.id)"
            >
              Edit
            </Button>
          </div>
  
          <!-- Promo Description -->
          <p class="text-sm text-gray-600">{{ promo.description }}</p>
  
          <!-- Discount -->
          <p class="text-sm font-medium">
            Discount:
            <span class="text-primary">
              {{ promo.discount_type === 'percentage' ? `${promo.discount}%` : `₱${promo.discount}` }}
            </span>
          </p>
  
          <!-- Restaurant Name -->
          <p class="text-xs text-gray-500">
            Restaurant: {{ promo.restaurant ? promo.restaurant.name : 'N/A' }}
          </p>
  
          <!-- Time Offer Badges -->
          <div class="flex flex-wrap gap-2 mt-2">
            <Badge v-for="(time, day) in sortedOperatingHours(promo.time_offer)" :key="day" variant="outlined">
              {{ day }}: {{ time }}
            </Badge>
          </div>
        </div>
      </div>
  
      <!-- No Promos Available -->
      <div v-else class="text-center text-gray-500">
        No promos available.
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useApiEndpoints } from '@/composables/useApiRestaurants.js'
  import { CirclePlus } from 'lucide-vue-next'
  import { Button } from '@/components/ui/button'
  import { Badge } from '@/components/ui/badge'
  import { sortedOperatingHours } from '~/lib/timeUtils';
  
  const promos = ref([])
  const { fetchPromos } = useApiEndpoints()
  
  // Fetch data when the component mounts
  onMounted(async () => {
    try {
      promos.value = await fetchPromos()
      console.log(promos.value)
    } catch (error) {
      console.error('Error fetching data:', error)
    }
  })
  
  // Edit button handler
  const editPromo = (promoId) => {
    // Redirect to the promo edit page
    window.location.href = `/promos/edit/${promoId}`
  }
  
  </script>
  