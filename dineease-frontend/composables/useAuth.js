import { useCookie } from '#app'

export function useAuth() {
  const authToken = useCookie('authToken')

  const isAuthenticated = () => !!authToken.value

  const logout = () => {
    authToken.value = null // Clear the token
  }

  return { isAuthenticated, logout }
}