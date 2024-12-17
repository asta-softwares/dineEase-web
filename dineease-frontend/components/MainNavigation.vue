<template>
    <div class="border-b bg-white">
      <div class="flex h-16 items-center px-4 max-w-screen-xl mx-auto">
        <!-- Clickable Logo and Tagline -->
        <NuxtLink to="/" class="flex items-center">
          <img class="w-[50px]" src="/images/logo.svg" alt="DineEase Logo" />
          <div class="flex flex-col ml-2 gap-y-1">
            <img class="w-[130px]" src="/images/logo-text.svg" alt="DineEase" />
            <span class="text-[10px] font-semibold">CRAVE . CLICK . ENJOY</span>
          </div>
        </NuxtLink>
        <MainNav class="mx-auto" />
        <!-- Search and UserNav Components -->
        <div class="flex items-center space-x-4">
          <Search />
          <UserNav />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import Search from '@/components/Search.vue'
  import UserNav from '@/components/UserNav.vue'
  import MainNav from './components/MainNav.vue'
  </script>