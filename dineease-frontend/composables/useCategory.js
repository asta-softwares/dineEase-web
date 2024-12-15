export const useCategories = () => {
    const config = useRuntimeConfig()
    const baseUrl = config.public.apiBaseUrl
    const authToken = useCookie('authToken')
  
    const headers = {
      Authorization: `Bearer ${authToken.value}`,
    }
  
    // --- Fetch Restaurant Categories ---
    const fetchRestaurantCategories = async () => {
      const { data, error } = await useFetch(`${baseUrl}restaurant-categories/`, {
        method: 'GET',
        headers,
      })
      if (error.value) throw error.value
      return data.value
    }
  
    // --- Fetch Menu Categories ---
    const fetchMenuCategories = async () => {
      const { data, error } = await useFetch(`${baseUrl}menu-cuisines/`, {
        method: 'GET',
        headers,
      })
      if (error.value) throw error.value
      return data.value
    }
  
    return {
      fetchRestaurantCategories,
      fetchMenuCategories,
    }
  }
  