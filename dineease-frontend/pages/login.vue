<template>
  <div class="w-full h-screen flex justify-center items-center">
    <Card class="w-[500px]">
      <CardHeader class="flex flex-col items-center space-y-1">
        <img class="w-[100px]" src="/images/logo.svg" alt="DineEase Logo" />
        <CardTitle class="text-2xl">Login to DineEase</CardTitle>
        <CardDescription>Enter your details below to log in</CardDescription>
      </CardHeader>
      <CardContent class="grid gap-4">
        <div class="grid gap-2">
          <Label for="identifier">Email or Phone</Label>
          <Input id="identifier" v-model="identifier" placeholder="m@example.com or 1234567890" />
        </div>
        <div class="grid gap-2">
          <Label for="password">Password</Label>
          <Input id="password" type="password" v-model="password" placeholder="Password" />
        </div>
        <div v-if="errorMessage" class="text-red-500 text-sm mt-2">
          {{ errorMessage }}
        </div>
      </CardContent>
      <CardFooter class="flex flex-col gap-y-4">
        <Button class="w-full" @click="handleLogin">Log in</Button>
        <div class="relative">
          <div class="absolute inset-0 flex items-center">
            <span class="w-full border-t" />
          </div>
          <div class="relative flex justify-center text-xs uppercase">
            <span class="bg-background px-2 text-muted-foreground">
              Or continue with
            </span>
          </div>
        </div>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthApi } from '@/composables/useAuthApi'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const identifier = ref('')
const password = ref('')
const errorMessage = ref('')
const { login } = useAuthApi()
const router = useRouter()

const handleLogin = async () => {
  try {
    errorMessage.value = '' // Reset error message
    const data = await login(identifier.value, password.value)
    console.log(data)
    alert('Login successful!')
    localStorage.setItem('authToken', data.token)
    router.push('/') // Redirect to a protected route or dashboard
  } catch (error) {
    console.error(error)
    errorMessage.value = error.response?.data?.detail || 'Incorrect username or password.'
  }
}
</script>
