<template>
  <div class="w-full h-screen flex justify-center items-center">
    <Card class="w-[500px]">
      <CardHeader class="flex flex-col items-center space-y-1">
        <img class="w-[75px]" src="/images/logo.svg" alt="DineEase Logo" />
        <CardTitle class="text-2xl">Login to DineEase</CardTitle>
        <CardDescription>Enter your details below to log in</CardDescription>
      </CardHeader>
      <CardContent class="grid gap-4">
        <div class="grid gap-2">
          <Label for="identifier">Email or Phone</Label>
          <Input id="identifier" v-model="identifier" placeholder="m@example.com or 1234567890" />
        </div>
        <div class="grid gap-2 relative">
          <Label for="password">Password</Label>
          <Input 
            :type="isPasswordVisible ? 'text' : 'password'" 
            id="password" 
            v-model="password" 
            placeholder="Password" 
          />
          <div 
            type="button" 
            class="absolute right-0 top-1/2 transform -translate-y-1/4 p-2 cursor-pointer" 
            @click="togglePasswordVisibility">
            <EyeIcon v-if="isPasswordVisible" />
            <EyeOffIcon v-else />
          </div>
        </div>
        <div v-if="errorMessage" class="text-red-500 text-sm mt-2">
          {{ errorMessage }}
        </div>
        <div class="mt-4 flex flex-col gap-4">
          <Button :disabled="isLoading" class="w-full flex items-center justify-center" @click="handleLogin">
            <LoaderCircle v-if="isLoading" class="mr-2 h-4 w-4 animate-spin" />
            Log in
          </Button>
          <Button variant="outline" class="w-full flex items-center justify-center gap-2" @click="handleGoogleLogin">
            <img class="w-[20px]" src="/images/google-icon.svg" alt="Google Logo" />
            Log in with Google
          </Button>
        </div>
      </CardContent>
      <CardFooter class="flex flex-col gap-y-4">
        <div class="text-sm text-center">
          Don't have an account? 
          <span class="text-blue-500 cursor-pointer" @click="goToRegister">Register</span>
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
import { toast } from '@/components/ui/toast'
import { Eye as EyeIcon, EyeOff as EyeOffIcon, LoaderCircle } from 'lucide-vue-next'

const identifier = ref('')
const password = ref('')
const errorMessage = ref('')
const isPasswordVisible = ref(false) // State to toggle password visibility
const { login, googleAuth } = useAuthApi()
const isLoading = ref(false)
const router = useRouter()

const handleLogin = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''
    const data = await login(identifier.value, password.value)
    toast({
      title: 'Logged In Successfully!',
      description: 'You can now interact with your restaurant.',
    })
    localStorage.setItem('authToken', data.token)
    router.push('/')
  } catch (error) {
    console.error(error)
    errorMessage.value = error.response?.data?.detail || 'Incorrect username or password.'
  } finally {
    isLoading.value = false
  }
}

const togglePasswordVisibility = () => {
  isPasswordVisible.value = !isPasswordVisible.value
}

const goToRegister = () => {
  router.push('/register')
}

const handleGoogleLogin = async () => {
  try {
    isLoading.value = true;

    // Initialize Google Identity Services
    window.google.accounts.id.initialize({
      client_id: '481133992953-7d6dmauctabfht3j3q9s2onpd1thfs17.apps.googleusercontent.com',
      callback: async (response) => {
        if (response.error) {
          throw new Error(response.error);
        }

        const idToken = response.credential; // This is the ID Token (JWT)

        // Use googleAuth to handle backend communication
        await googleAuth(idToken);

        toast({
          title: 'Login Successful!',
          description: 'You are now logged in with Google.',
        });

        router.push('/'); // Redirect to dashboard
      },
    });

    // Show the Google Sign-In button or prompt the user
    window.google.accounts.id.prompt(); // Prompts the user to log in
  } catch (error) {
    console.error('Google Login Error:', error);
    toast({
      title: 'Login Failed',
      description: 'Unable to log in with Google.',
      variant: 'destructive',
    });
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  handleGoogleLogin();
})
</script>