<template>
    <div class="w-full h-screen flex justify-center items-center">
      <Card class="w-[500px]">
        <CardHeader class="flex flex-col items-center space-y-1 text-center">
          <img class="w-[75px]" src="/images/logo.svg" alt="DineEase Logo" />
          <CardTitle class="text-2xl">Verify Your Email</CardTitle>
          <CardDescription>
            Enter the 6-digit code sent to your email to complete the verification process.
          </CardDescription>
        </CardHeader>
        <CardContent class="grid gap-4">
          <!-- PIN Code Input -->
          <div class="flex justify-center space-x-2">
            <input
              v-for="(digit, index) in code"
              :key="index"
              ref="pinInputs"
              type="text"
              maxlength="1"
              v-model="code[index]"
              @input="onInput(index)"
              @keydown.backspace="onBackspace(index)"
              class="w-[50px] h-[50px] text-center border border-gray-300 rounded-md text-xl font-bold"
            />
          </div>
          <div v-if="errorMessage" class="text-red-500 text-sm mt-2 mx-auto">
            {{ errorMessage }}
          </div>
          <div class="flex justify-between items-center mt-4 mx-auto">
            <p class="text-gray-500 text-sm">
              Did not receive any email? 
              <span v-if="resendTimeout > 0">Resend code in {{ resendTimeout }} seconds</span>
              <button
                v-else
                @click="handleResend"
                class="text-blue-500 text-sm underline"
              >
                Resend Code
              </button>
            </p>
          </div>
        </CardContent>
        <CardFooter>
          <Button
            :disabled="isLoading || code.join('').length < 6"
            class="w-full flex items-center justify-center"
            @click="handleVerify"
          >
            <LucideSpinner v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
            Verify
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

const code = ref(['', '', '', '', '', ''])
const errorMessage = ref('')
const resendTimeout = ref(30)
const isLoading = ref(false)
const pinInputs = ref([])
let countdownInterval = null
const config = useRuntimeConfig()
const baseUrl = config.public.apiBaseUrl

const router = useRouter()

onMounted(() => {
  if (pinInputs.value[0]) {
    pinInputs.value[0].focus()
  }
  startCountdown ()
})

// Focus on the next input automatically
const onInput = (index) => {
  if (code.value[index].length === 1 && index < 5) {
    pinInputs.value[index + 1].focus()
  }
}

// Handle backspace to focus on the previous input
const onBackspace = (index) => {
  if (!code.value[index] && index > 0) {
    pinInputs.value[index - 1].focus()
  }
}

const handleResend = async () => {
  try {
    isLoading.value = true
    resendTimeout.value = 30 // Reset countdown

    const email = localStorage.getItem('registeredEmail') // Get email from localStorage

    if (!email) {
      errorMessage.value = 'Email not found. Please register again.'
      return
    }

    // Use baseUrl for the API endpoint
    const { data, error } = await useFetch(`${baseUrl}resend-code/`, {
      method: 'POST',
      body: { email },
    })

    if (error.value) {
      errorMessage.value = error.value.detail || 'Failed to resend the code. Please try again later.'
      return
    }

    toast({
      title: 'Code Resent',
      description: 'A new verification code has been sent to your email.',
    })

    // Start countdown
    startCountdown()
  } catch (err) {
    console.error('Unexpected error during resend:', err)
    errorMessage.value = 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const startCountdown = () => {
  clearInterval(countdownInterval)
  countdownInterval = setInterval(() => {
    if (resendTimeout.value > 0) {
      resendTimeout.value -= 1
    } else {
      clearInterval(countdownInterval)
    }
  }, 1000)
}

onUnmounted(() => {
  clearInterval(countdownInterval)
})

const handleVerify = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''

    const email = localStorage.getItem('registeredEmail')

    if (!email) {
      errorMessage.value = 'Email not found. Please register again.'
      return
    }

    // Use baseUrl for the API endpoint
    const { data, error } = await useFetch(`${baseUrl}verify-code/`, {
      method: 'POST',
      body: { email, code: code.value.join('') },
    })

    if (error.value) {
      errorMessage.value = error.value.detail || 'Invalid confirmation code. Please try again.'
      return
    }

    toast({
      title: 'Email Verified!',
      description: 'Your email has been successfully verified. You can now log in.',
    })

    // Clear registeredEmail from localStorage after successful verification
    localStorage.removeItem('registeredEmail')

    router.push('/login') // Redirect to login or dashboard
  } catch (err) {
    console.error('Unexpected error during verification:', err)
    errorMessage.value = 'Something went wrong. Please try again.'
  } finally {
    isLoading.value = false
  }
}
</script>