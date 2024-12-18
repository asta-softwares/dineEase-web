<template>
  <div class="flex-col flex">
    <div v-if="menus.length && !isLoading" class="flex items-center justify-between space-y-2 p-4">
      <h2 class="text-3xl font-bold tracking-tight">
        Menu List
      </h2>
      <div class="ml-auto">
        <NuxtLink to="/menus/create/">
          <Button>
            <CirclePlus class="mr-2 h-4 w-4" />
            Add Menu
          </Button>
        </NuxtLink>
      </div>
    </div>

    <div v-if="isLoading">
      <!-- Display Skeleton Loader with 2 columns -->
      <SkeletonLoader :columns="2" item-width="100%" item-height="150px" text-width="100%" text-height="16px" :itemsCount="6" />
    </div>

    <div v-else>
      <!-- Grouped Menus by Restaurant -->
      <div v-if="Object.keys(groupedMenus).length">
        <div v-for="(menus, restaurantName) in groupedMenus" :key="restaurantName" class="mb-8 px-4">
          <!-- Restaurant Name -->
          <h3 class="text-xl font-semibold mb-4">{{ restaurantName }}</h3>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="menu in menus"
              :key="menu.id"
              class="flex items-start justify-between gap-4 p-2 border rounded-lg shadow-sm"
            >
              <!-- Menu Image -->
              <img
                :src="menu.image || menu.images[0]?.image"
                :alt="menu.name"
                class="w-36 h-36 rounded-md object-cover"
              />

              <div class="flex flex-col flex-1">
                <!-- Menu Name and Edit Button -->
                <p class="flex items-center font-bold mb-2">
                  {{ menu.name }}
                  <NuxtLink
                    :to="`/menus/edit/${menu.id}`"
                    class="ml-auto"
                  >
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      class="text-xs"
                    >
                      Edit
                    </Button>
                  </NuxtLink>
                </p>

                <!-- Cost or Discounted Cost -->
                <p class="text-sm text-gray-600 mb-1">
                  from ₱{{ menu.discounted_cost || menu.cost }}
                </p>

                <!-- Description -->
                <p class="text-sm text-gray-500">{{ menu.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- No Menus Available -->
      <div v-else class="flex flex-col items-center justify-center p-8">
        <img src="/images/product.svg" alt="No Restaurant" class="w-64 h-64" />
        <h1 class="text-2xl font-semibold">No Menu Available</h1>
        <span class="text-gray-500 mb-4">Start by adding your first Menu to your restaurant.</span>
        <NuxtLink to="/menus/create/">
          <Button @click="handleAddMenu">
            <CirclePlus class="mr-2 h-4 w-4" />
            Add Menu
          </Button>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue'
import { useApiEndpoints } from '@/composables/useApiRestaurants.js'
import { CirclePlus } from 'lucide-vue-next'
import { Button } from '@/components/ui/button'
import SkeletonLoader from '@/components/Skeleton/SkeletonLoading'

const menus = ref([])
const groupedMenus = ref({})
const isLoading = ref(true) // Loading state
const { fetchMenus } = useApiEndpoints()

// Function to group menus by restaurant
const groupMenusByRestaurant = (menuList) => {
  return menuList.reduce((groups, menu) => {
    const restaurantName = menu.restaurant_details?.name || 'Unknown Restaurant'
    if (!groups[restaurantName]) {
      groups[restaurantName] = []
    }
    groups[restaurantName].push(menu)
    return groups
  }, {})
}

// Fetch data when the component mounts
onMounted(async () => {
  try {
    const fetchedMenus = await fetchMenus()
    menus.value = fetchedMenus
    groupedMenus.value = groupMenusByRestaurant(fetchedMenus)
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    isLoading.value = false
  }
})

// Handler for adding a menu
const handleAddMenu = () => {
  window.location.href = '/menus/create'
}
</script>
