<template>
  <div class="relative h-screen w-screen overflow-x-hidden">
    <div class="absolute inset-0 bg-short-bg bg-no-repeat bg-center opacity-20 -z-10"></div>
    <Toaster />

    <!-- Loading Skeleton -->
    <div v-if="loading" class="splash-screen">
      <div class="flex flex-col items-center justify-center gap-y-4">
        <img src="/images/logo.svg" alt="Logo" class="splash-logo" />
        <div class="splash-spinner"></div>
      </div>
    </div>

    <!-- Error Placeholder -->
    <div v-else-if="error" class="error-container">
      <p class="error-text">{{ error }}</p>
    </div>

    <!-- Main Content -->
    <div v-else class="relative z-10 max-w-screen-xl w-full mx-auto p-4 min-h-full h-auto">
      <MainNavigation v-if="user" />
      <NuxtPage />
    </div>

    <!-- Footer -->
    <Footer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import MainNavigation from '@/components/MainNavigation.vue'
import Footer from '@/components/Footer.vue'
import Toaster from '@/components/ui/toast/Toaster.vue'

const userStore = useUserStore()
const loading = ref(true)
const error = ref(null)

const user = computed(() => userStore.user)

onMounted(async () => {
  try {
    await userStore.loadUser()
    error.value = null
  } catch (err) {
    console.error('Error loading user data:', err)
    error.value = 'Failed to load user data. Please try again later.'
  } finally {
    setTimeout(() => {
      loading.value = false
    }, 1000)
  }
})
</script>

<style scoped>
/* Splash Screen Styles */
.splash-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: #f8f9fa;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.splash-logo {
  width: 100px;
  margin-bottom: 20px;
}

/* Simple Spinner Animation */
.splash-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #ccc;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* Error Placeholder */
.error-container {
  text-align: center;
  margin-top: 20vh;
}

.error-text {
  color: #f44336;
  font-size: 1.2em;
}
</style>
