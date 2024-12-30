<template>
    <div class="hidden border-r bg-muted/40 md:block">
      <div class="flex h-full max-h-screen flex-col gap-2">
        <!-- Logo Section -->
        <div class="flex h-14 items-center border-b px-4 lg:h-[70px]">
          <NuxtLink to="/" class="flex items-center py-4">
            <img class="w-[40px]" src="/images/logo.svg" alt="DineEase Logo" />
            <div class="flex flex-col ml-2 gap-y-1">
              <img class="w-[110px]" src="/images/logo-text.svg" alt="DineEase" />
              <span class="text-[10px] font-semibold">CRAVE . CLICK . ENJOY</span>
            </div>
          </NuxtLink>
        </div>
  
        <!-- Main Navigation -->
        <div class="flex-1">
          <nav class="grid items-start px-2 text-sm font-medium lg:px-4">
            <NuxtLink
              v-for="(item, index) in navigationItems.filter(item => !item.isBottom)"
              :key="index"
              :to="item.path"
              class="flex items-center gap-3 rounded-lg px-3 py-4 text-muted-foreground transition-all hover:text-primary"
              :class="{ 'bg-muted text-primary': isActive(item.path) }"
              :disabled="item.disabled" 
            >
              <component :is="item.icon" class="h-4 w-4" />
              {{ item.label }}
              <Badge
                v-if="item.badge"
                class="ml-auto flex shrink-0 items-center justify-center rounded-full"
              >
                {{ item.badge }}
              </Badge>
            </NuxtLink>
          </nav>
        </div>
  
        <!-- Bottom Navigation -->
        <nav class="mt-auto flex flex-col items-center gap-4 px-2 sm:py-5">
          <NuxtLink
            v-for="(item, index) in navigationItems.filter(item => item.isBottom)"
            :key="`bottom-${index}`"
            :to="item.path"
            class="flex items-center gap-3 rounded-lg px-3 py-2 text-muted-foreground transition-all hover:text-primary"
            :class="{ 'bg-muted text-primary': isActive(item.path) }"
          >
            <component :is="item.icon" class="h-4 w-4" />
            {{ item.label }}
          </NuxtLink>
        </nav>
      </div>
    </div>
  </template>
  
  <script setup>
  import { Badge } from '@/components/ui/badge';
  import {
    Home,
    ShoppingCart,
    Package,
    Users,
    LineChart,
    Settings,
    UtensilsCrossed,
    SquareMenu
  } from 'lucide-vue-next';

  const route = useRoute();
  
  // Navigation configuration
  const navigationItems = [
    { label: 'Incoming Orders', path: '/', icon: Home },
    // { label: 'Orders', path: '/order', icon: ShoppingCart, badge: 6 },
    { label: 'My Restaurant', path: '/restaurants', icon: UtensilsCrossed },
    { label: 'Menus', path: '/menus', icon: SquareMenu },
    { label: 'Promos', path: '/promos', icon: Package },
    { label: 'Settings', path: '/account', icon: Settings },
    { label: 'Analytics', icon: LineChart, disabled: true, badge: 'Coming Soon' },
  ];
  
  const isActive = (path) => {
  return path === '/' ? route.path === '/' : route.path.startsWith(path)
}
  </script>
  