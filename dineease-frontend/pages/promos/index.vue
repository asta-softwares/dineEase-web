<template>
  <div class="p-4">
    <div v-if="promos.length && !isLoading" class="flex items-center justify-between mb-4">
      <h2 class="text-3xl font-bold tracking-tight">Promo List</h2>
      <div class="ml-auto">
        <Button @click="addPromo">
          <CirclePlus class="mr-2 h-4 w-4" />
          Add Promo
        </Button>
      </div>
    </div>

    <div v-if="isLoading">
      <!-- Display Skeleton Loader with 2 columns -->
      <SkeletonLoader :columns="2" item-width="100%" item-height="150px" text-width="100%" text-height="16px" :itemsCount="4" />
    </div>

    <div v-else>
      <div v-if="Object.keys(groupedPromos).length" class="space-y-8">
        <div v-for="(promos, restaurantName) in groupedPromos" :key="restaurantName">
          <!-- Restaurant Name as Group Header -->
          <h3 class="text-xl font-semibold mb-4">{{ restaurantName }}</h3>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
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
                  {{ promo.discount_type === 'percentage' ? `${promo.discount}%` : `$${promo.discount}` }}
                </span>
              </p>

              <!-- Time Offer Badges -->
              <div class="flex flex-wrap gap-2 mt-2">
                <Badge v-for="(time, day) in sortedOperatingHours(promo.time_offer)" :key="day" variant="outlined">
                  {{ day }}: {{ time }}
                </Badge>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Promos Available -->
      <div v-else class="flex flex-col items-center justify-center p-8">
        <img src="/images/product.svg" alt="No Restaurant" class="w-64 h-64" />
        <h1 class="text-2xl font-semibold">No Promo Available</h1>
        <span class="text-gray-500 mb-4">Start by adding your first Promo to your restaurant.</span>
        <Button @click="addPromo">
          <CirclePlus class="mr-2 h-4 w-4" />
          Add Promo
        </Button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useApiEndpoints } from '@/composables/useApiRestaurants.js'
import { CirclePlus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { sortedOperatingHours } from '~/lib/timeUtils'
import SkeletonLoader from '@/components/Skeleton/SkeletonLoading.vue'

const promos = ref([])
const isLoading = ref(true) // Loading state
const { fetchPromos } = useApiEndpoints()

onMounted(async () => {
  try {
    promos.value = await fetchPromos()
    console.log(promos.value)
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    isLoading.value = false
  }
})

const groupedPromos = computed(() => {
  return promos.value.reduce((groups, promo) => {
    const restaurantName = promo.restaurant_details ? promo.restaurant_details.name : 'Unassigned'
    if (!groups[restaurantName]) {
      groups[restaurantName] = []
    }
    groups[restaurantName].push(promo)
    return groups
  }, {})
})

const editPromo = (promoId) => {
  window.location.href = `/promos/edit/${promoId}`
}

const addPromo = () => {
  window.location.href = '/promos/create'
}
</script>
