<template>
  <div class="hidden flex-col md:flex">
    <div class="flex-1 space-y-4 p-8 pt-2 max-w-screen-xl w-full mx-auto">
      <div class="flex items-center justify-between space-y-2">
        <h2 class="text-3xl font-bold tracking-tight">Order List</h2>
      </div>

      <!-- Display Skeleton Loader while loading -->
      <div v-if="isLoading">
        <SkeletonLoader :columns="1" item-width="100%" item-height="150px" text-width="100%" text-height="16px" :itemsCount="4" />
      </div>

      <!-- Orders Grid -->
      <div v-else-if="orders.length" class="grid gap-4">
        <Card v-for="order in orders" :key="order.id" class="p-4">
          <CardHeader>
            <CardTitle class="text-lg font-semibold">Order #{{ order.id }}</CardTitle>
            <CardDescription>Status: {{ order.status }}</CardDescription>
          </CardHeader>
          <CardContent class="space-y-2">
            <p><strong>Customer:</strong> {{ order.customer }}</p>
            <p><strong>Restaurant:</strong> {{ order.restaurant }}</p>
            <p><strong>Total:</strong> ${{ order.order_total }}</p>
            <p><strong>Order Time:</strong> {{ order.order_time }}</p>

            <!-- Order Items -->
            <div>
              <h4 class="font-medium">Items:</h4>
              <ul class="list-disc list-inside">
                <li v-for="item in order.items" :key="item.menu_item.id">
                  {{ item.menu_item.name }} (x{{ item.quantity }}) - ${{ item.price }}
                </li>
              </ul>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-2 mt-4">
              <Button @click="acceptOrder(order.id)" :disabled="order.status !== 'pending'">
                Accept
              </Button>
              <Button variant="destructive" @click="rejectOrder(order.id)" :disabled="order.status !== 'pending'">
                Reject
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- No Orders Available -->
      <div v-else class="flex flex-col items-center justify-center p-8">
        <img src="/images/order.svg" alt="No Orders" class="w-64 h-64" />
        <h1 class="text-2xl font-semibold">No Orders Available</h1>
        <span class="text-gray-500 mb-4 w-[400px] text-center">
          There are currently no orders to display. Once customers place orders, they'll appear here.
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useOrderApiEndpoints } from '~/composables/useOrderApi'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import SkeletonLoader from '@/components/Skeleton/SkeletonLoading.vue'

const orders = ref([])
const isLoading = ref(true) // Loading state
const { fetchOrders, updateOrderStatus } = useOrderApiEndpoints()

// Fetch data when the component mounts
onMounted(async () => {
  try {
    orders.value = await fetchOrders()
    console.log(orders.value)
  } catch (error) {
    console.error('Error fetching data:', error)
  } finally {
    isLoading.value = false
  }
})

// Accept Order
async function acceptOrder(orderId) {
  try {
    await updateOrderStatus(orderId, { status: 'accepted' })
    const order = orders.value.find((o) => o.id === orderId)
    if (order) order.status = 'accepted'
    console.log(`Order ${orderId} accepted.`)
  } catch (error) {
    console.error('Failed to accept order:', error)
  }
}

// Reject Order
async function rejectOrder(orderId) {
  try {
    await updateOrderStatus(orderId, { status: 'rejected' })
    const order = orders.value.find((o) => o.id === orderId)
    if (order) order.status = 'rejected'
    console.log(`Order ${orderId} rejected.`)
  } catch (error) {
    console.error('Failed to reject order:', error)
  }
}
</script>
