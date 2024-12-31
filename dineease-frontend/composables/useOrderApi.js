export function useOrderApiEndpoints() {
    const config = useRuntimeConfig()
    const baseUrl = config.public.apiBaseUrl
    const authToken = useCookie('authToken')
  
    const headers = {
      Authorization: `Bearer ${authToken.value}`,
    }
  
    const fetchOrders = async ({ page = 1, page_size = 30 } = {}) => {
      const { data, error } = await useFetch(`${baseUrl}payments/orders/`, {
        method: 'GET',
        headers,
        query: {
          page,
          page_size,
        },
      });
    
      if (error.value) throw error.value;
    
      return {
        results: data.value.results || [],
        count: data.value.count || 0,
      };
    };

    const createOrder = async (orderData) => {
      const { data, error } = await useFetch(`${baseUrl}payments/order-create/`, {
        method: 'POST',
        headers,
        body: orderData,
      })
      if (error.value) throw error.value

      return data.value
    }

    const createPaymentIntent = async (amount, restaurantId, restaurantStripeAccountId) => {
      try {
        const { data, error } = await useFetch(`${baseUrl}payments/create-payment-intent/`, {
          method: 'POST',
          headers,
          body: {
            amount: amount,
            restaurant_stripe_account_id: restaurantStripeAccountId,
            restaurant_id: restaurantId,
          },
        })
    
        if (error.value) {
          throw new Error(error.value.message || 'Failed to create payment intent');
        }
    
        return data.value
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
  