// composables/useAuthApi.js
import { useFetch, useCookie } from '#app'
import { useRuntimeConfig } from '#app'
import { useUserStore } from '@/stores/user'

export function useAuthApi() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl
  const authToken = useCookie('authToken', { maxAge: 86400 }) // Token stored for 24 hours
  const userStore = useUserStore()

  const register = async (email, phone, username, password, name, typeOfUser) => {
    const { data, error } = await useFetch(baseUrl + 'register/', {
      method: 'POST',
      body: { email, phone, username, password, name, typeOfUser },
    })
    if (error.value) throw error.value

    // Store the token in a cookie after successful registration
    authToken.value = data.value.token
    return data.value
  }

  const login = async (identifier, password) => {
    const { data, error } = await useFetch(baseUrl + 'login/', {
      method: 'POST',
      body: { identifier, password },
    })
    if (error.value) throw error.value
    authToken.value = data.value.token

    // Fetch and set user details after login
    await userStore.loadUser()
    return data.value
  }

  const fetchUser = async () => {
    console.log("ENTER HERE", authToken.value)
    const { data, error } = await useFetch(baseUrl + 'me/', {
      headers: {
        Authorization: `Bearer ${authToken.value}`,
      },
    })
    if (error.value) throw error.value

    console.log("DATA", data.value)
    return data.value
  }

  const logout = () => {
    authToken.value = null
    userStore.clearUser()
  }

  return { register, login, logout, fetchUser }
}
