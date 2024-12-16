<script setup>
import { useRoute } from 'vue-router'
import { cn } from '@/lib/utils'

// Define the tabs configuration
const tabs = [
  { label: 'Orders', path: '/' },
  { label: 'Restaurants', path: '/restaurants/' },
  { label: 'Menu', path: '/menus/' },
  { label: 'Promo', path: '/promos/' },
]

const route = useRoute()

// Function to check if the tab is active
const isActive = (path) => {
  return path === '/' ? route.path === '/' : route.path.startsWith(path)
}
</script>

<template>
  <nav :class="cn('flex items-center space-x-4 lg:space-x-6', $attrs.class ?? '')">
    <NuxtLink
      v-for="tab in tabs"
      :key="tab.path"
      :to="tab.path"
      :class="cn(
        'text-sm font-medium transition-colors hover:text-primary',
        { 'text-primary': isActive(tab.path), 'text-muted-foreground': !isActive(tab.path) }
      )"
    >
      {{ tab.label }}
    </NuxtLink>
  </nav>
</template>
