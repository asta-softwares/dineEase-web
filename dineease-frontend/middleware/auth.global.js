import { useAuth } from '@/composables/useAuth'

export default defineNuxtRouteMiddleware((to) => {
  const { isAuthenticated } = useAuth()
  const protectedRoutes = ['/dashboard', '/user', '/profile', '/settings']
  const requiresAuth = protectedRoutes.some(route => to.path.startsWith(route))

  // Redirect to login if accessing a protected route without authentication
  if (requiresAuth && !isAuthenticated()) {
    return navigateTo('/login')
  }

  // Redirect to dashboard if already authenticated and trying to access the login or register page
  if ((to.path === '/login' || to.path === '/register') && isAuthenticated()) {
    return navigateTo('/') // Redirect to home or dashboard
  }
})
