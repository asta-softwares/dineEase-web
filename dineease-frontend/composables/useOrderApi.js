export function useOrderApiEndpoints() {
    const config = useRuntimeConfig()
    const baseUrl = config.public.apiBaseUrl
    const authToken = useCookie('authToken')
  
    const headers = {
      Authorization: `Bearer ${authToken.value}`,
    }
  
    const fetchOrders = async () => {
      const { data, error } = await useFetch(`${baseUrl}payments/orders/`, {
        method: 'GET',
        headers,
      })
      if (error.value) throw error.value
      return data.value
    }

    const createOrder = async (orderData) => {
      const { data, error } = await useFetch(`${baseUrl}payments/order-create/`, {
        method: 'POST',
        headers,
        body: orderData,
      })
      if (error.value) throw error.value

      return data.value
    }

    const createPaymentIntent = async (amount) => {
      try {
        const { data, error } = await useFetch(`${baseUrl}payments/create-payment-intent/`, {
          method: 'POST',
          headers,
          body: { amount },  // Send the amount in the request body
        })
    
        if (error.value) {
          throw error.value
        }
    
        return data.value  // This should contain the clientSecret
      } catch (err) {
        console.error('Error creating payment intent:', err)
        throw err
      }
    }

    const rejectOrder = async (orderId, paymentIntentId) => {
      try {
        const response = await fetch('/api/refund-payment', {
          method: 'POST',
          headers,
          body: JSON.stringify({ payment_intent_id: paymentIntentId }),
        })
    
        if (!response.ok) {
          throw new Error('Refund failed')
        }
    
        console.log(`Order ${orderId} refunded successfully.`)
        // Update order status to refunded in the frontend
      } catch (err) {
        console.error('Failed to refund order:', err)
      }
    }
  
    const updateOrderStatus = async (orderId, statusData) => {
      const { data, error } = await useFetch(`${baseUrl}payments/update-order-status/${orderId}/`, {
        method: 'POST',
        headers,
        body: statusData,
      })
      if (error.value) throw error.value
      return data.value
    }
  
    // --- Payment Endpoints ---
    const updatePaymentStatus = async (paymentId, paymentStatusData) => {
      const { data, error } = await useFetch(`${baseUrl}payments/${paymentId}/update-status/`, {
        method: 'POST',
        headers,
        body: paymentStatusData,
      })
      if (error.value) throw error.value
      return data.value
    }
  
    return {
      fetchOrders,
      createOrder,
      updateOrderStatus,
      updatePaymentStatus,
      createPaymentIntent,
      rejectOrder
    }
}
  