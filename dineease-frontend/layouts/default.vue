<template>
  <div 
    :class="computedGridClass"
    class="min-h-screen w-full"
  >
    <Sidebar v-if="user"/>
    <!-- Main Content Wrapper -->
    <div class="relative z-10 flex flex-1 flex-col">
      <div class="absolute inset-0 bg-short-bg bg-no-repeat bg-center opacity-20 -z-10"></div>
      <Toaster />
      <NuxtLoadingIndicator />
  
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
      <div v-else class="flex min-h-screen w-full flex-col gap-y-4 bg-muted/40 p-4  px-4 sm:px-8">
        <Header v-if="user" :breadcrumbs="breadcrumbs"/>
        <NuxtPage />
      </div>

      <Footer />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watchEffect } from 'vue'
import { useUserStore } from '@/stores/user'
import MainNavigation from '@/components/MainNavigation.vue'
import Footer from '@/components/Footer.vue'
import { useRouter, useRoute } from 'vue-router'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import Toaster from '@/components/ui/toast/Toaster.vue'
import Sidebar from '@/components/Sidebar.vue'
import Header from '~/components/Header.vue'
import { useBreadcrumb } from '@/composables/useBreadcrumb';
import { useAuth } from '@/composables/useAuth'

const userStore = useUserStore()
const { isAuthenticated } = useAuth()
const router = useRouter()
const route = useRoute()
const loading = ref(true)
const error = ref(null)

const user = computed(() => userStore.user)
const { breadcrumbs } = useBreadcrumb();

// Load User Data
const { data, pending, error: fetchError } = await useAsyncData('user-data', async () => {
  if (isAuthenticated()) {
    if (!userStore.user) {
      await userStore.loadUser();
    }
    return userStore.user;
  }
  return null;
});

watchEffect(() => {
  if (!pending.value) {
    setTimeout(() => {
      loading.value = false
    }, 1000)
  }
  error.value = fetchError.value
})

const computedGridClass = computed(() => {
  return user.value
    ? 'grid md:grid-cols-[220px_1fr] lg:grid-cols-[280px_1fr]'
    : 'grid-cols-1';
});
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
