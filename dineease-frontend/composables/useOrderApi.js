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
      const { data, error } = await useFetch(`${baseUrl}payments/orders/create/`, {
        method: 'POST',
        headers,
        body: orderData,
      })
      if (error.value) throw error.value

      return data.value
    }
  
    const updateOrderStatus = async (orderId, statusData) => {
      const { data, error } = await useFetch(`${baseUrl}payments/orders/${orderId}/update-status/`, {
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
    }
}
  