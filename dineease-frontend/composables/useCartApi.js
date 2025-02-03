export function useCartApiEndpoints() {
    const config = useRuntimeConfig();
    const baseUrl = config.public.apiBaseUrl;
    const authToken = useCookie('authToken');
  
    const headers = {
      Authorization: `Bearer ${authToken.value}`,
      'Content-Type': 'application/json',
    };
  
    const createCart = async (cartData) => {
      const { data, error } = await useFetch(`${baseUrl}carts/`, {
        method: 'POST',
        headers,
        body: cartData,
      });
      if (error.value) throw error.value;
      return data.value;
    };
  
    const updateCart = async (cartId, cartData) => {
      const { data, error } = await useFetch(`${baseUrl}carts/${cartId}/`, {
        method: 'PATCH',
        headers,
        body: cartData,
      });
      if (error.value) throw error.value;
      return data.value;
    };
  
    const deleteItemCart = async (cartId, itemId) => {
      const url = `${baseUrl}carts/${cartId}/remove-item/?item_id=${itemId}`;
      const { data, error } = await useFetch(url, {
        method: 'DELETE',
        headers,
      });
      if (error.value) throw error.value;
      return data.value;
    };

    const deleteCart = async (cartId) => {
      const { data, error } = await useFetch(`${baseUrl}carts/${cartId}/`, {
        method: 'DELETE',
        headers,
      });
      if (error.value) throw error.value;
      return data.value;
    };
  
    return {
      createCart,
      updateCart,
      deleteItemCart,
      deleteCart,
    };
  }
  