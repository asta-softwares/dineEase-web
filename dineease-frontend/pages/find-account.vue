<template>
  <div class="w-full h-screen flex justify-center items-center">
    <Card class="w-[500px]">
      <CardHeader class="flex flex-col items-center space-y-1 text-center">
        <img class="w-[75px]" src="/images/logo.svg" alt="DineEase Logo" />
        <CardTitle class="text-2xl">Find Your Account</CardTitle>
        <CardDescription>
          Enter your email, phone, or username to find your account.
        </CardDescription>
      </CardHeader>
      <CardContent class="grid gap-4">
        <!-- Identifier Input (Email or Phone) -->
        <input
          v-model="identifier"
          type="text"
          placeholder="Enter your email, phone, or username"
          class="w-full px-3 py-2 border border-gray-300 rounded-md"
        />

        <div v-if="errorMessage" class="text-red-500 text-sm mt-2 mx-auto">
          {{ errorMessage }}
        </div>
      </CardContent>
      <CardFooter>
        <Button
          :disabled="isLoading || !identifier"
          class="w-full flex items-center justify-center"
          @click="handleFindAccount"
        >
          <LucideSpinner v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
          Find Account
        </Button>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup>
import { toast } from '@/components/ui/toast'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { LoaderCircle as LucideSpinner } from 'lucide-vue-next'

const identifier = ref('')
const errorMessage = ref('')
const isLoading = ref(false)
const config = useRuntimeConfig()
const baseUrl = config.public.apiBaseUrl
const router = useRouter()

const handleFindAccount = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''

    const { data, error } = await useFetch(`${baseUrl}find-account/`, {
      method: 'POST',
      body: { identifier: identifier.value },
    })

    if (error.value) {
      errorMessage.value = error.value.detail || 'Account not found.'
      return
    }

    toast({
      title: 'Account Found!',
      description: 'A reset code has been sent to your email.',
    })

    localStorage.setItem('resetIdentifier', data.value.email)

    // Redirect to reset password page
    router.push('/reset-password')
  } catch (err) {
    console.error('Unexpected error:', err)
    errorMessage.value = 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>
