<script setup>
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb'

const props = defineProps({
  items: {
    type: Array,
    required: true,
  },
  separator: {
    type: Object,
    default: () => null, 
  },
})
</script>

<template>
  <Breadcrumb>
    <BreadcrumbList>
      <template v-for="(item, index) in items" :key="index">
        <BreadcrumbItem>
          <BreadcrumbLink v-if="item.href" :href="item.href">
            {{ item.label }}
          </BreadcrumbLink>
          <span v-else>{{ item.label }}</span>
        </BreadcrumbItem>

        <!-- Add a separator unless it's the last item -->
        <BreadcrumbSeparator v-if="index < items.length - 1">
          <component :is="separator" />
        </BreadcrumbSeparator>
      </template>
    </BreadcrumbList>
  </Breadcrumb>
</template>
