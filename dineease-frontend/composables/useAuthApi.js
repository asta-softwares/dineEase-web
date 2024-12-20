import { useRuntimeConfig } from '#app'
import { useUserStore } from '@/stores/user'

export function useAuthApi() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl
  const authToken = useCookie('authToken')
  const refreshToken = useCookie('refreshToken')
  const userStore = useUserStore()

  const register = async (email, phone, username, password, name, typeOfUser) => {
    const { data, error } = await useFetch(baseUrl + 'register/', {
      method: 'POST',
      body: { email, phone, username, password, name, typeOfUser },
    })
    if (error.value) throw error.value

    authToken.value = data.value.access
    refreshToken.value = data.value.refresh
    return data.value
  }

  const login = async (identifier, password) => {
    const { data, error } = await useFetch(baseUrl + 'token/', {
      method: 'POST',
      body: { username: identifier, password },
    })
  
    if (error.value) throw error.value
  
    authToken.value = data.value.access
    refreshToken.value = data.value.refresh

    await userStore.loadUser()
    return data.value
  }
  
  const fetchUser = async () => {
    const { data, error } = await useFetch(baseUrl + 'me/', {
      headers: {
        Authorization: `Bearer ${authToken.value}`, 
      },
    })
  
    if (error.value) {
      // Check if the error is related to token expiration (e.g., 401 or 403)
      if (error.value.status === 401) {
        // Attempt to refresh the token
        const success = await refreshAccessToken()
        if (success) {
          // Retry fetching user details with the new access token
          return await fetchUser()
        }
      }
      throw error.value
    }
  
    console.log("USER DATA FROM API:", data)
    return data.value
  }
  
  const refreshAccessToken = async () => {
    if (!refreshToken.value) {
      console.error("No refresh token found. Please log in again.")
      return false
    }
  
    const { data, error } = await useFetch(baseUrl + 'token/refresh/', {
      method: 'POST',
      body: { refresh: refreshToken.value },
    })
  
    if (error.value) {
      console.error("Error refreshing access token:", error.value)
      return false
    }
  
    authToken.value = data.value.access
    return true
  }

  const logout = async () => {
    if (!authToken.value) {
      console.error("No auth token found. Cannot log out.")
      return
    }
  
    try {
      await useFetch(baseUrl + 'token/logout/', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${authToken.value}`,
        },
      })
    } catch (error) {
      console.error("Error logging out on server:", error)
    } finally {
      
      authToken.value = null
      refreshToken.value = null
  
      // Clear user data from the store
      userStore.clearUser()
    }
  }

  return { register, login, logout, fetchUser }
}
