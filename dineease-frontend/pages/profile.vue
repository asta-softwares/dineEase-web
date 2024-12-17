<script setup>
import ProfileForm from './components/ProfileForm.vue'
import FormsLayout from './layouts/FormsLayout.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const user = computed(() => userStore.user)
</script>

<template>
  <FormsLayout>
    <ProfileForm :user="user"/>
  </FormsLayout>
</template>
