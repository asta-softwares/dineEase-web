<template>
  <form @submit.prevent="handlePayment" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
    <div>
      <h2>Order Notifications</h2>
      <p v-if="notification">{{ notification }}</p>
    </div>

    <h2 class="text-2xl font-bold mb-4">Payment Details</h2>

    <div class="mb-4">
      <label for="card-element" class="block text-sm font-medium text-gray-700">Card Details</label>
      <div id="card-element" class="p-3 border rounded-lg shadow-sm"></div>
    </div>

    <div v-if="errorMessage" class="text-red-500 mb-4">{{ errorMessage }}</div>

    <Button type="submit" :disabled="isProcessing" class="w-full mt-4">
      <span v-if="isProcessing">Processing...</span>
      <span v-else>Pay</span>
    </Button>
  </form>
</template>

<script setup>
import { loadStripe } from '@stripe/stripe-js'
import { ref, onMounted } from 'vue'
import { Button } from '@/components/ui/button'
import { useOrderApiEndpoints } from '@/composables/useOrderApi'
const config = useRuntimeConfig()
const baseUrl = config.public.apiBaseUrl

const { createOrder, createPaymentIntent } = useOrderApiEndpoints()

const stripe = await loadStripe('pk_test_51QMpBEAECjFQcoAiIBBR2ytlseH5Ztrp19gx9RWhTox7fzADahNcnjrnyLz0a4N3cv0xp63wx2daPuf3TXWaBSRE00muGzaBD0')
const elements = stripe.elements()
const cardElement = elements.create('card')
const isProcessing = ref(false)
const errorMessage = ref('')
const notification = ref('')

onMounted(() => {
  cardElement.mount('#card-element');

  const userId = 1;
  const baseUrl = config.public.apiBaseUrl;
  
  const wsProtocol = baseUrl.startsWith('https') ? 'wss://' : 'ws://';
  
  const host = new URL(baseUrl).host;

  console.log(baseUrl, host, wsProtocol)
  
  // Construct the WebSocket URL
  const socket = new WebSocket(`${wsProtocol}${host}/ws/orders/${userId}/`);

  socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    notification.value += `\n${data.message}`;
  };

  socket.onopen = () => console.log('WebSocket connected');
  socket.onerror = (error) => console.error('WebSocket error:', error);
  socket.onclose = () => console.log('WebSocket closed');
});

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})

// Fixed order data (replace with dynamic data as needed)
const orderData = {
  amount: 5000, // $50.00 in cents
  restaurant_id: 1,
  // promo_id: 6,
  order_total: 50.0,
  is_delivery: true,
  order_type: 'delivery',
  delivery_address: '123 Main Street',
  tax: 5.0,
  tip: 3.0,
  menu_items: [
    { menu_item_id: 1, quantity: 2, special_instructions: 'Extra cheese' },
    { menu_item_id: 2, quantity: 1 },
  ],
}

const handlePayment = async () => {
  isProcessing.value = true
  errorMessage.value = ''

  try {
    // Step 1: Get the clientSecret from the backend
    const { clientSecret } = await createPaymentIntent(orderData.amount)

    console.log("CLIENT SECRET:", clientSecret)

    // Step 2: Confirm the payment with Stripe
    const { paymentIntent, error } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: { card: cardElement },
    })

    if (error) {
      throw new Error(error.message)
    }

    console.log("PAYMENT INTENT:", paymentIntent)

    // Extract payment details from the PaymentIntent
    const paymentDetails = {
      id: paymentIntent.id,
      status: paymentIntent.status,
      amount_received: paymentIntent.amount / 100, // Convert from cents to dollars
      payment_method: paymentIntent.payment_method,
      transaction_id: paymentIntent.id,
      payment_gateway: 'stripe',
    }

    alert('Payment successful!')

    // Step 3: Create the order with the payment details
    const result = await createOrder({
      ...orderData,
      payment: {
        payment_method: 'credit_card',
        payment_status: paymentIntent.status,
        amount_paid: paymentDetails.amount_received,
        payment_gateway: paymentDetails.payment_gateway,
        transaction_id: paymentDetails.transaction_id,
      },
    })

    console.log("ORDER RESULT:", result)
    alert('Order created successfully!')
  } catch (err) {
    console.error('Error:', err)
    errorMessage.value = err.message || 'An error occurred. Please try again.'
  } finally {
    isProcessing.value = false
  }
}
</script>
