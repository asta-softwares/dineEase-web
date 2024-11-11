export function useApiEndpoints() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl
  const authToken = useCookie('authToken')  // Get the auth token from the cookie or other storage

  const fetchRestaurants = async () => {
    const { data, error } = await useFetch(baseUrl + 'restaurants/', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authToken.value}`,  // Add Authorization header
      },
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchPromos = async () => {
    const { data, error } = await useFetch(baseUrl + 'promos/', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authToken.value}`,  // Add Authorization header
      },
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchMenus = async () => {
    const { data, error } = await useFetch(baseUrl + 'menus/', {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${authToken.value}`,  // Add Authorization header
      },
    })
    if (error.value) throw error.value
    return data.value
  }

  return { fetchRestaurants, fetchPromos, fetchMenus }
}
