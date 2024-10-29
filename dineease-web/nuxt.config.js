export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },
  css: [
      'primevue/resources/themes/saga-blue/theme.css', 
      'primevue/resources/primevue.min.css', 
      'primeicons/primeicons.css'
  ],
  build: {
      transpile: ['primevue']
  },
  auth: {
    strategies: {
      google: {
        clientId: 'YOUR_GOOGLE_CLIENT_ID',
        codeChallengeMethod: '',
        responseType: 'token id_token',
        redirectUri: 'http://localhost:3000',
      },
      facebook: {
        clientId: 'YOUR_FACEBOOK_CLIENT_ID',
        scope: ['public_profile', 'email'],
        responseType: 'token',
        redirectUri: 'http://localhost:3000',
      },
    }
  }
})
