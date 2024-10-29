import { defineNuxtPlugin } from '#app';
import PrimeVue from 'primevue/config';
import Dialog from 'primevue/dialog';
import Card from 'primevue/card';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';

// Styles
import 'primevue/resources/themes/saga-blue/theme.css';   // Pick a theme
import 'primevue/resources/primevue.min.css';            // Core CSS
import 'primeicons/primeicons.css';                      // Icons CSS

export default defineNuxtPlugin((nuxtApp) => {
    nuxtApp.vueApp.use(PrimeVue);

    // Register components globally
    nuxtApp.vueApp.component('Dialog', Dialog);
    nuxtApp.vueApp.component('Card', Card);
    nuxtApp.vueApp.component('Button', Button);
    nuxtApp.vueApp.component('InputText', InputText);
});