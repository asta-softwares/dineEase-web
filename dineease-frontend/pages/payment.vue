<template>
    <form @submit.prevent="handlePayment" class="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
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
  
  const stripe = await loadStripe('pk_test_51QMpBEAECjFQcoAiIBBR2ytlseH5Ztrp19gx9RWhTox7fzADahNcnjrnyLz0a4N3cv0xp63wx2daPuf3TXWaBSRE00muGzaBD0')
  const elements = stripe.elements()
  
  const style = {
    base: {
      color: '#32325d',
      fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
      fontSize: '16px',
      '::placeholder': {
        color: '#aab7c4',
      },
    },
    invalid: {
      color: '#fa755a',
      iconColor: '#fa755a',
    },
  }
  
  const cardElement = elements.create('card', { style })
  const isProcessing = ref(false)
  const errorMessage = ref('')
  
  onMounted(() => {
    cardElement.mount('#card-element')
  })

  const orderData = {
  restaurant_id: 1,
  promo_id: 2,
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
    const response = await fetch('/api/create-payment-intent', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(orderData),
    })
    const { clientSecret } = await response.json()

    const { error } = await stripe.confirmCardPayment(clientSecret, {
      payment_method: { card: cardElement }
    })

    if (!error) {
      alert('Payment successful!')
    }
  } catch (err) {
    console.error('Payment failed:', err)
  } finally {
      isProcessing.value = false
    }
  }
  </script>
  
  <style scoped>
  form {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
  }
  #card-element {
    background-color: #fff;
    border: 1px solid #d1d5db;
    padding: 12px;
    border-radius: 6px;
  }
  </style>
  