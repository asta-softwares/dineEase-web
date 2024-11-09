import { useFetch } from '#app'
import { useRuntimeConfig } from '#app'

export function useApiEndpoints() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl

  const fetchRestaurants = async () => {
    const { data, error } = await useFetch(baseUrl + 'restaurants/', {
      method: 'GET',
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchPromos = async () => {
    const { data, error } = await useFetch(baseUrl + 'promos/', {
      method: 'GET',
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchMenus = async () => {
    const { data, error } = await useFetch(baseUrl + 'menus/', {
      method: 'GET',
    })
    if (error.value) throw error.value
    return data.value
  }

  return { fetchRestaurants, fetchPromos, fetchMenus }
}
