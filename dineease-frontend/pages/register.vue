<template>
  <div class="w-full h-screen flex justify-center items-center">
    <Card class="w-[500px]">
      <CardHeader class="flex flex-col items-center space-y-1">
        <img class="w-[75px]" src="/images/logo.svg" alt="DineEase Logo" />
        <CardTitle class="text-2xl">Create a DineEase Account</CardTitle>
        <CardDescription>Enter your details below to create an account</CardDescription>
      </CardHeader>
      <CardContent class="grid gap-4">
        <div class="grid grid-cols-2 gap-4">
          <div class="grid gap-2">
            <Label for="firstName">First Name</Label>
            <Input id="firstName" v-model="firstName" placeholder="First Name" />
          </div>
          <div class="grid gap-2">
            <Label for="lastName">Last Name</Label>
            <Input id="lastName" v-model="lastName" placeholder="Last Name" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="grid gap-2">
            <Label for="email">Email</Label>
            <Input id="email" v-model="email" placeholder="m@example.com" />
            <p v-if="errors.email" class="text-red-500 text-xs mt-1">{{ errors.email }}</p>
          </div>
          <div class="grid gap-2">
            <Label for="phone">Phone</Label>
            <Input id="phone" v-model="phone" placeholder="1234567890" />
            <p v-if="errors.phone" class="text-red-500 text-xs mt-1">{{ errors.phone }}</p>
          </div>
        </div>
        <div class="grid gap-2">
          <Label for="username">Username (optional)</Label>
          <Input id="username" v-model="username" placeholder="Username" />
          <p v-if="errors.username" class="text-red-500 text-xs mt-1">{{ errors.username }}</p>
        </div>
        <div class="grid gap-2">
          <Label for="password">Password</Label>
          <Input id="password" type="password" v-model="password" @input="checkPasswordStrength" placeholder="Password" />
          <div v-if="password" class="mt-2">
            <div class="progress-bar" :style="{ width: `${strengthPercentage}%`, backgroundColor: strengthColor }"></div>
            <p class="text-sm mt-1" :class="strengthColorClass">Password Strength: {{ passwordStrengthText }}</p>
            <ul class="text-xs mt-2 list-disc pl-5">
              <li :class="{ 'text-green-500': hasMinLength }">At least 8 characters</li>
              <li :class="{ 'text-green-500': hasUppercase }">At least one uppercase letter</li>
              <li :class="{ 'text-green-500': hasNumber }">At least one number</li>
              <li :class="{ 'text-green-500': hasSpecialChar }">At least one special character (!@#$%^&*)</li>
            </ul>
            <p class="text-xs text-gray-500 mt-2">{{ feedback }}</p>
          </div>
        </div>
        <div class="grid gap-2">
          <Label for="confirmPassword">Confirm Password</Label>
          <Input id="confirmPassword" type="password" v-model="confirmPassword" placeholder="Confirm Password" />
          <div v-if="passwordMismatch" class="text-red-500 text-sm mt-1">Passwords do not match.</div>
        </div>
        <div v-if="errorMessage" class="text-red-500 text-sm mt-2">
          {{ errorMessage }}
        </div>
        <!-- Toggle for isTesting -->
        <!-- <div class="flex items-center mt-4">
          <input type="checkbox" id="isTesting" v-model="isTesting" @change="autofillFields" />
          <Label for="isTesting" class="ml-2">Enable Autofill (Testing Mode)</Label>
        </div> -->
      </CardContent>
      <CardFooter>
        <Button class="w-full" @click="handleRegister" :disabled="!canSubmit">Create Account</Button>
      </CardFooter>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthApi } from '@/composables/useAuthApi'
import { useAuth } from '@/composables/useAuth'
import zxcvbn from 'zxcvbn'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

// Form fields
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const phone = ref('')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const passwordStrength = ref(0)
const feedback = ref('')
const errors = ref({})
const isTesting = ref(false) // Testing mode toggle

// Password rules
const hasMinLength = computed(() => password.value.length >= 8)
const hasUppercase = computed(() => /[A-Z]/.test(password.value))
const hasNumber = computed(() => /\d/.test(password.value))
const hasSpecialChar = computed(() => /[!@#$%^&*]/.test(password.value))

// Autofill fields for testing
const autofillFields = () => {
  if (isTesting.value) {
    firstName.value = 'Test'
  lastName.value = 'User'
    email.value = 'testuser@example.com'
    phone.value = '1234567890'
    username.value = 'testuser'
    password.value = 'Test@1234!'
    confirmPassword.value = 'Test@1234!'
  } else {
    firstName.value = ''
  lastName.value = ''
    email.value = ''
    phone.value = ''
    username.value = ''
    password.value = ''
    confirmPassword.value = ''
  }
}

// Password strength checker function using zxcvbn
const checkPasswordStrength = () => {
  const result = zxcvbn(password.value)
  passwordStrength.value = result.score
  feedback.value = result.feedback.suggestions.join(' ')
}

// Computed properties for strength progress, color, and feedback
const strengthPercentage = computed(() => (passwordStrength.value + 1) * 20)
const passwordStrengthText = computed(() => ['Too Weak', 'Weak', 'Fair', 'Good', 'Strong'][passwordStrength.value])
const strengthColor = computed(() => {
  switch (passwordStrength.value) {
    case 4: return 'green'
    case 3: return 'lightgreen'
    case 2: return 'yellow'
    case 1: return 'orange'
    default: return 'red'
  }
})
const strengthColorClass = computed(() => {
  switch (passwordStrength.value) {
    case 4: return 'text-green-500'
    case 3: return 'text-green-400'
    case 2: return 'text-yellow-500'
    case 1: return 'text-orange-500'
    default: return 'text-red-500'
  }
})

// Confirm password validation
const passwordMismatch = computed(() => confirmPassword.value && password.value !== confirmPassword.value)
const canSubmit = computed(() => firstName.value && lastName.value && email.value && phone.value && password.value && !passwordMismatch.value && passwordStrength.value >= 2)

const { register } = useAuthApi()
const { isAuthenticated } = useAuth()
const router = useRouter()

// Redirect to dashboard if already logged in
if (isAuthenticated()) {
  router.push('/dashboard')
}

const handleRegister = async () => {
  try {
    errorMessage.value = ''
    errors.value = {}

    await register(email.value, phone.value, username.value, password.value, firstName.value, lastName.value, 'restaurant_owner')

    // Redirect to dashboard after successful registration
    router.push('/login')
  } catch (error) {
      console.error("Unexpected error during registration:", error)
      const responseErrors = error.data || {}

      // Capture specific field errors if they exist
      errors.value.email = responseErrors.email?.[0] || ''
      errors.value.phone = responseErrors.phone?.[0] || ''
      errors.value.username = responseErrors.username?.[0] || ''
      errors.value.password = responseErrors.password?.[0] || ''
      
      // Fallback error message
      errorMessage.value = 'Registration failed. Please check the errors above.'
  }
}
</script>

<style scoped>
.progress-bar {
  height: 8px;
  border-radius: 4px;
  margin-top: 8px;
  transition: width 0.3s ease;
}
.text-green-500 { color: green; }
.text-green-400 { color: lightgreen; }
.text-yellow-500 { color: yellow; }
.text-orange-500 { color: orange; }
.text-red-500 { color: red; }
</style>
