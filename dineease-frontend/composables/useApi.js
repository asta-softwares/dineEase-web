// composables/useApi.js
import { useFetch } from '#app'
import { useRuntimeConfig } from '#app'

export function useApi() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl

  const get = async (url, options = {}) => {
    const { data, error, pending, refresh } = await useFetch(baseUrl + url, {
      ...options,
      method: 'GET',
    })
    if (error.value) throw error.value
    return { data: data.value, error: error.value, pending: pending.value, refresh }
  }

  const post = async (url, body, options = {}) => {
    const { data, error, pending, refresh } = await useFetch(baseUrl + url, {
      ...options,
      method: 'POST',
      body,
    })
    if (error.value) throw error.value
    return { data: data.value, error: error.value, pending: pending.value, refresh }
  }

  const put = async (url, body, options = {}) => {
    const { data, error, pending, refresh } = await useFetch(baseUrl + url, {
      ...options,
      method: 'PUT',
      body,
    })
    if (error.value) throw error.value
    return { data: data.value, error: error.value, pending: pending.value, refresh }
  }

  const del = async (url, options = {}) => {
    const { data, error, pending, refresh } = await useFetch(baseUrl + url, {
      ...options,
      method: 'DELETE',
    })
    if (error.value) throw error.value
    return { data: data.value, error: error.value, pending: pending.value, refresh }
  }

  return { get, post, put, del }
}
