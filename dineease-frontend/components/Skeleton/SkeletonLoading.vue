<script setup>
import { defineProps, computed } from 'vue'
import { Skeleton } from '@/components/ui/skeleton'

// Define props for customization
const props = defineProps({
  columns: {
    type: Number,
    default: 3, // Number of skeleton items to display per row
  },
  itemWidth: {
    type: String,
    default: '250px', // Width of each skeleton item
  },
  itemHeight: {
    type: String,
    default: '125px', // Height of each skeleton item
  },
  textWidth: {
    type: String,
    default: '250px', // Width of the skeleton text line
  },
  textHeight: {
    type: String,
    default: '16px', // Height of the skeleton text line
  },
  itemsCount: {
    type: Number,
    default: 6, // Total number of skeleton items
  },
})

// Generate an array based on the number of items
const skeletonItems = computed(() => Array.from({ length: props.itemsCount }))
</script>

<template>
  <div class="grid gap-x-4 gap-y-4" :style="{ gridTemplateColumns: `repeat(${columns}, 1fr)` }">
    <div v-for="(_, index) in skeletonItems" :key="index" class="flex flex-col space-y-2">
      <Skeleton :class="`h-[${itemHeight}] w-full rounded-xl`" />
      <div class="space-y-2">
        <Skeleton :class="`h-[${textHeight}] w-full`" />
        <Skeleton :class="`h-[${textHeight}] w-[80%]`" />
      </div>
    </div>
  </div>
</template>
