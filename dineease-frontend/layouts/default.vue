<template>
    <div>
      <NuxtPage />
    </div>
  </template>
  
  <script setup>
  import { useUserStore } from '@/stores/user'
  
  const userStore = useUserStore()
  
  // Load user data when the layout is mounted
  onBeforeMount(() => {
    if (!userStore.user) {
      userStore.loadUser()
    }
  })
  </script>