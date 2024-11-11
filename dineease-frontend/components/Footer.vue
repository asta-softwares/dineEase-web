<template>
    <footer class="text-sm text-center py-4 border-t">
      <p>DineEase © {{ currentYear }}</p>
    </footer>
  </template>
  
  <script setup>  
  // Get the current year dynamically
  const currentYear = new Date().getFullYear()
  </script>
