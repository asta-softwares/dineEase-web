<template>
  <div>
    <!-- Show MainNavigation if the user is logged in -->
    <MainNavigation v-if="user" />

    <!-- Loading Skeleton -->
    <div v-if="loading" class="loading-container">
      <Skeleton class="w-[200px] h-[40px] rounded-full mb-4" />
      <Skeleton class="w-[150px] h-[20px] rounded-full mb-2" />
      <Skeleton class="w-[180px] h-[20px] rounded-full" />
    </div>

    <!-- Error Placeholder -->
    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
    </div>

    <!-- Main Content -->
    <div v-else>
      <NuxtPage />
    </div>

    <Footer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import MainNavigation from '@/components/MainNavigation.vue'
import { Skeleton } from '@/components/ui/skeleton'
import Footer from '@/components/Footer.vue'

// Use the user store to get user data
const userStore = useUserStore()
const loading = ref(true)
const error = ref(null)
const user = ref(null)

// Load user data on the server or client
const { data, pending, error: fetchError } = await useAsyncData('user-data', async () => {
  if (!userStore.user) {
    await userStore.loadUser()
  }
  return userStore.user
})

watchEffect(() => {
  loading.value = pending.value
  error.value = fetchError.value
  user.value = data.value
})
</script>

<style scoped>
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20vh;
}

.error-container {
  text-align: center;
  margin-top: 20vh;
}

.error-image {
  width: 100px;
  height: 100px;
  margin-bottom: 16px;
}

.error-text {
  color: #f44336;
  font-size: 1.2em;
}
</style>
