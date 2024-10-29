<template>
    <div class="login-container">
      <Card class="login-card">
        <h2 class="login-title">Login</h2>
        <div>
          <label for="email">Email</label>
          <InputText v-model="email" id="email" placeholder="Enter your email" class="w-full mb-3" />
        </div>
        <div>
          <label for="password">Password</label>
          <Password v-model="password" id="password" placeholder="Enter your password" class="w-full mb-3" />
        </div>
        <Button label="Login" class="p-button-primary w-full mb-2" @click="login" />
  
        <div class="auth-buttons">
          <Button label="Login with Google" icon="pi pi-google" class="p-button-danger w-full mb-2" @click="loginWithGoogle" />
          <Button label="Login with Facebook" icon="pi pi-facebook" class="p-button-info w-full" @click="loginWithFacebook" />
        </div>
      </Card>
    </div>
  </template>
  
  <script setup>
  import InputText from 'primevue/inputtext'
  import Password from 'primevue/password'
  import Button from 'primevue/button'
  import Card from 'primevue/card'
  
  const email = ref('')
  const password = ref('')
//   const auth = useAuth()
  
  const login = async () => {
    try {
      // Implement your login logic
    } catch (error) {
      console.error(error)
    }
  }
  
  const loginWithGoogle = () => {
    // auth.loginWith('google')
  }
  
  const loginWithFacebook = () => {
    // auth.loginWith('facebook')
  }
  </script>
  
  <style scoped>
  .login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
  }
  .login-card {
    width: 400px;
    padding: 20px;
  }
  .login-title {
    text-align: center;
    margin-bottom: 20px;
  }
  .auth-buttons {
    margin-top: 20px;
  }
  </style>
  