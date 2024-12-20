import { defineStore } from 'pinia'
import { useAuthApi } from '@/composables/useAuthApi'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const { fetchUser } = useAuthApi()

  // Fetch user details after login or refresh
  const loadUser = async () => {
    try {
      const userData = await fetchUser()  // fetchUser now returns data.value directly
      console.log("USER DATA", userData)
      user.value = userData  // Assign userData directly to user.value
    } catch (error) {
      console.error('Error fetching user:', error)
      user.value = null
    }
  }

  // Set user directly (e.g., after login)
  const setUser = (userData) => {
    user.value = userData
  }

  const clearUser = () => {
    user.value = null
  }

  return { user, loadUser, setUser, clearUser }
})