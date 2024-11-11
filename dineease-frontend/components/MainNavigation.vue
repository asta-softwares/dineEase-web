<template>
    <div class="border-b">
      <div class="flex h-16 items-center px-4 max-w-screen-xl mx-auto">
        <img class="w-[50px]" src="/images/logo.svg" alt="DineEase Logo" />
        <div class="flex flex-col ml-2 gap-y-1">
          <img class="w-[130px]" src="/images/logo-text.svg" alt="DineEase" />
          <span class="text-[10px] font-semibold">CRAVE . CLICK . ENJOY</span>
        </div>
        <div class="ml-auto flex items-center space-x-4">
          <Search />
          <UserNav />
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import Search from '@/components/Search.vue'
  import UserNav from '@/components/UserNav.vue'
  </script>
  
  <style scoped>
  /* Add any additional styles here */
  </style>
  