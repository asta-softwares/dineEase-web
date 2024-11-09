<template>
    <div class="flex-1 flex flex-col gap-2 p-4 pt-0">
      <TransitionGroup name="list" appear>
        <button
          v-for="item in items"
          :key="item.id"
          :class="cn(
            'flex flex-col items-start gap-2 rounded-lg border p-3 text-left text-sm transition-all hover:bg-accent',
            selectedRestaurant === item.id && 'bg-muted',
          )"
          @click="() => handleItemClick(item)"
        >
          <div class="flex w-full flex-col gap-1">
            <div class="flex items-center">
              <div class="flex items-center gap-2">
                <img :src="item.image" alt="Restaurant Image" class="w-10 h-10 rounded-md object-cover">
                <div class="font-semibold">
                  {{ item.name }}
                </div>
              </div>
              <div
                :class="cn(
                  'ml-auto text-xs',
                  selectedRestaurant === item.id
                    ? 'text-foreground'
                    : 'text-muted-foreground',
                )"
              >
                {{ item.ratings }} ★
              </div>
            </div>

            <div class="text-xs font-medium text-muted-foreground">
              {{ item.location }}
            </div>
            <div v-if="item.categories.length" class="flex gap-x-2 text-xs">
              Service Type: 
              <Badge v-for="category in item.categories" :key="category.id" :variant="getBadgeVariantFromService(category.name)">
                {{ category.name }}
              </Badge>
            </div>
            <div class="line-clamp-2 text-xs text-muted-foreground mt-1">
              {{ item.description }}
            </div>
          </div>

          <div class="flex items-center gap-2">
            <Badge v-for="(hours, day) in item.operating_hours" :key="day" variant="outline">
              {{ day }}: {{ hours }}
            </Badge>
          </div>
        </button>
      </TransitionGroup>
    </div>
</template>

<script setup>
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'

const props = defineProps({
  items: {
    type: Array,
    required: true
  }
})
const selectedRestaurant = defineModel('selectedRestaurant', { required: false })

function getBadgeVariantFromService(serviceType) {
  if (serviceType === 'both') return 'default'
  if (serviceType === 'dine-in') return 'outline'
  if (serviceType === 'delivery') return 'secondary'
  return 'default'
}

const handleItemClick = (item) => {
  router.push(`/restaurant/${item.id}`)
}
</script>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.5s ease;
}

.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(15px);
}

.list-leave-active {
  position: absolute;
}
</style>
