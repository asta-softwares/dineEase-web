<template>
    <header class="sticky top-0 z-30 flex h-14 items-center gap-4 border-b bg-background sm:static sm:h-auto sm:border-0 sm:bg-transparent">
      <Sheet>
        <SheetTrigger as-child>
          <Button size="icon" variant="outline" class="sm:hidden">
            <Menu class="h-5 w-5" />
            <span class="sr-only">Toggle Menu</span>
          </Button>
        </SheetTrigger>
        <SheetContent side="left" class="sm:max-w-xs">
          <nav class="grid gap-6 text-lg font-medium">
            <NuxtLink to="/" class="flex items-center py-2">
                <img class="w-[40px]" src="/images/logo.svg" alt="DineEase Logo" />
                <div class="flex flex-col ml-2 gap-y-1">
                  <img class="w-[110px]" src="/images/logo-text.svg" alt="DineEase" />
                  <span class="text-[10px] font-semibold">CRAVE . CLICK . ENJOY</span>
                </div>
              </NuxtLink>
            <NuxtLink
              v-for="(item, index) in navigationItems"
              :key="index"
              :to="item.path"
              class="flex items-center gap-3 rounded-lg px-3 py-1 text-muted-foreground transition-all hover:text-primary"
              :class="{ 'bg-muted text-primary': isActive(item.path) }"
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
        </SheetContent>
      </Sheet>
      <Breadcrumb class="hidden md:flex">
        <BreadcrumbList>
          <BreadcrumbItem v-for="(breadcrumb, index) in breadcrumbs" :key="index">
            <BreadcrumbLink as-child v-if="!breadcrumb.isCurrent">
              <NuxtLink :to="breadcrumb.path">{{ breadcrumb.label }}</NuxtLink>
            </BreadcrumbLink>
            <BreadcrumbPage v-else>{{ breadcrumb.label }}</BreadcrumbPage>
            <BreadcrumbSeparator v-if="index < breadcrumbs.length - 1" />
          </BreadcrumbItem>
        </BreadcrumbList>
      </Breadcrumb>
      <div class="relative ml-auto flex-1 md:grow-0">
        <Search />
      </div>
      <UserNav />
    </header>
  </template>
  
  <script setup>
  import UserNav from '@/components/UserNav.vue';
  import {
    Breadcrumb,
    BreadcrumbItem,
    BreadcrumbLink,
    BreadcrumbList,
    BreadcrumbPage,
    BreadcrumbSeparator,
  } from '@/components/ui/breadcrumb';
  import { Button } from '@/components/ui/button';
  import { Input } from '@/components/ui/input';
  import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
  import { Badge } from '@/components/ui/badge';
  import {
    Home,
    Package,
    Package2,
    Menu,
    ShoppingCart,
    Users,
    LineChart,
    Settings,
    UtensilsCrossed,
    SquareMenu
  } from 'lucide-vue-next';
  import { useRoute } from 'vue-router';
  import Search from '@/components/Search';
  
  const navigationItems = [
    { label: 'Dashboard', path: '/', icon: Home },
    // { label: 'Orders', path: '/order', icon: ShoppingCart, badge: 6 },
    { label: 'My Restaurant', path: '/restaurants', icon: UtensilsCrossed },
    { label: 'Menus', path: '/menus', icon: SquareMenu },
    { label: 'Promos', path: '/promos', icon: Package },
    { label: 'Settings', path: '/account', icon: Settings },
    { label: 'Analytics', icon: LineChart, disabled: true, badge: 'Coming Soon' },
  ];
  
  const route = useRoute();
  const isActive = (path) => {
    return path === '/' ? route.path === '/' : route.path.startsWith(path);
  };
  
  import { useBreadcrumb } from '@/composables/useBreadcrumb';
  const { breadcrumbs } = useBreadcrumb();
  </script>
  