<script setup>
import AccountForm from './components/AccountForm.vue'
import FormsLayout from './layouts/FormsLayout.vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const user = computed(() => userStore.user)
</script>

<template>
  <FormsLayout>
    <AccountForm :user="user"/>
  </FormsLayout>
</template>
