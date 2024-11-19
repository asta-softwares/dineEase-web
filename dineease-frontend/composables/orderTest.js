import { useOrderApiEndpoints } from './useOrderApi.js'

export function useOrderActions() {
  const { createOrder, updateOrderStatus, updatePaymentStatus } = useOrderApiEndpoints()

  // --- Function to Create an Order ---
  const callCreateOrder = async () => {
    const orderData = {
      restaurant_id: 1,
      promo_id: 2,
      order_total: 50.00,
      is_delivery: true,
      order_type: 'delivery',
      delivery_address: '123 Main Street',
      tax: 5.00,
      tip: 3.00,
      menu_items: [
        { menu_item_id: 1, quantity: 2, special_instructions: 'Extra cheese' },
        { menu_item_id: 2, quantity: 1 },
      ],
      payment: {
        payment_method: 'credit_card',
        payment_status: 'pending',
        amount_paid: 50.00,
        payment_gateway: 'manual',
        transaction_id: 'txn_123456789',
      },
    }

    try {
      const response = await createOrder(orderData)
      console.log('Order created successfully:', response)
      return response
    } catch (error) {
      console.error('Error creating order:', error)
      throw error
    }
  }

  // --- Function to Update Order Status ---
  const callUpdateOrderStatus = async (orderId, action) => {
    const statusData = { action } // 'accept' or 'reject'

    try {
      const response = await updateOrderStatus(orderId, statusData)
      console.log(`Order status updated to ${action} successfully:`, response)
      return response
    } catch (error) {
      console.error(`Error updating order status to ${action}:`, error)
      throw error
    }
  }

  // --- Function to Update Payment Status ---
  const callUpdatePaymentStatus = async (paymentId, paymentStatus) => {
    const paymentStatusData = { payment_status: paymentStatus } // 'completed' or 'failed'

    try {
      const response = await updatePaymentStatus(paymentId, paymentStatusData)
      console.log(`Payment status updated to ${paymentStatus} successfully:`, response)
      return response
    } catch (error) {
      console.error(`Error updating payment status to ${paymentStatus}:`, error)
      throw error
    }
  }

  return {
    callCreateOrder,
    callUpdateOrderStatus,
    callUpdatePaymentStatus,
  }
}
