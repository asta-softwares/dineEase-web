<template>
  <div class="flex-col md:flex">
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
        <Card
          v-for="order in orders"
          :key="order.id"
          class="p-4 fade-in"
        >
          <CardHeader>
            <CardTitle class="text-lg font-semibold flex items-center">
              Order #{{ order.id }}
              <span v-if="isNewOrder(order.order_time)" class="ml-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full animate-pulse">
                New
              </span>
            </CardTitle>
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
              <Button @click="completeOrder(order.id)" :disabled="order.status !== 'confirmed'">
                Complete Order
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
import { useOrderApiEndpoints } from '~/composables/useOrderApi';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import SkeletonLoader from '@/components/Skeleton/SkeletonLoading.vue';
import { useWebSocket } from '@/lib/websocket';
import { useUserStore } from '@/stores/user'

const orders = ref([]);
const isLoading = ref(true);
const userStore = useUserStore()
const { fetchOrders, updateOrderStatus } = useOrderApiEndpoints();

const userId = computed(() => userStore.user?.id)
const { connectWebSocket, closeWebSocket } = useWebSocket(`restaurant/${userId.value}`, handleWebSocketMessage);

onMounted(async () => {
  await loadOrders();
  connectWebSocket();
});

onUnmounted(() => {
  closeWebSocket();
});

async function loadOrders() {
  try {
    const fetchedOrders = await fetchOrders();
    appendNewOrders(fetchedOrders);
  } catch (error) {
    console.error('Error fetching data:', error);
  } finally {
    isLoading.value = false;
  }
}

// Append new orders to the list and sort by recency
function appendNewOrders(fetchedOrders) {
  const existingOrderIds = orders.value.map((order) => order.id);
  let newOrderAdded = false;

  // Append only new orders
  fetchedOrders.forEach((order) => {
    if (!existingOrderIds.includes(order.id)) {
      orders.value.push(order);
      newOrderAdded = true;
    }
  });

  if (newOrderAdded) {
    alert('New Order Received!');
  }

  // Sort orders by order_time in descending order (most recent first)
  orders.value.sort((a, b) => new Date(b.order_time) - new Date(a.order_time));
}

// Handle incoming WebSocket messages
function handleWebSocketMessage(data) {
  console.log("DATA", data)
  if (data.status === 'pending') {
    loadOrders(); // Fetch new orders when notified
  }
}

function isNewOrder(orderTime) {
  const now = new Date()
  const orderDate = new Date(orderTime)
  const diffInMinutes = (now - orderDate) / (1000 * 60)
  return diffInMinutes <= 5
}

// Accept Order
async function acceptOrder(orderId) {
  try {
    await updateOrderStatus(orderId, { action: 'accept' });
    const order = orders.value.find((o) => o.id === orderId);
    if (order) order.status = 'confirmed';
    console.log(`Order ${orderId} accepted.`);
  } catch (error) {
    console.error('Failed to accept order:', error);
  }
}

// Complete Order
async function completeOrder(orderId) {
  try {
    await updateOrderStatus(orderId, { action: 'complete' });
    const order = orders.value.find((o) => o.id === orderId);
    if (order) order.status = 'completed';
    console.log(`Order ${orderId} has been completed.`);
  } catch (error) {
    console.error('Failed to complete order:', error);
  }
}

// Reject Order
async function rejectOrder(orderId) {
  try {
    await updateOrderStatus(orderId, { action: 'reject' });
    const order = orders.value.find((o) => o.id === orderId);
    if (order) order.status = 'cancelled';
    console.log(`Order ${orderId} rejected.`);
  } catch (error) {
    console.error('Failed to reject order:', error);
  }
}
</script>

<style scoped>
/* Fade-in animation */
.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
