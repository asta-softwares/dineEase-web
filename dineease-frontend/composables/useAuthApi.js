import { useRuntimeConfig } from '#app'
import { useUserStore } from '@/stores/user'
import errorMap from 'zod/locales/en.js'

export function useAuthApi() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl
  const authToken = useCookie('authToken')
  const refreshToken = useCookie('refreshToken')
  const userStore = useUserStore()

  const register = async (email, phone, username, password, firstName, lastName, typeOfUser) => {
    const { data, error } = await useFetch(baseUrl + 'register/', {
      method: 'POST',
      body: { email, phone, username, password, first_name: firstName, last_name: lastName, type_of_user: typeOfUser },
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
    });
  
    if (error.value) {
      const success = await refreshAccessToken();
      if (success) {
        return await fetchUser();
      }
  
      // If refresh fails, throw the original error
      throw error.value;
    }
  
    return data.value;
  };

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

  const updateUser = async (userData) => {
    const { data, error } = await useFetch(baseUrl + 'update-user/', {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${authToken.value}`,
      },
      body: userData,
    })

    if (error.value) throw error.value

    // Reload user data in the store after a successful update
    await userStore.loadUser()
    return data.value
  }

  return { register, login, logout, fetchUser, updateUser }
}
