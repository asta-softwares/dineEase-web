import { defineStore } from 'pinia'
import { useAuthApi } from '@/composables/useAuthApi'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const { fetchUser } = useAuthApi()

  const loadUser = async () => {
    try {
      const userData = await fetchUser()
      user.value = userData
    } catch (error) {
      console.error('Error fetching user:', error)
      user.value = null
    }
  }

  const setUser = (userData) => {
    user.value = userData
  }

  const clearUser = () => {
    user.value = null
  }

  return { user, loadUser, setUser, clearUser }
})