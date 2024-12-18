<template>
  <div class="border p-4 rounded-md my-4">
    <h2 class="text-lg font-semibold mb-2">{{ title }}</h2>
    <div class="grid grid-cols-2 gap-4">
      <div v-for="(hours, day) in hoursData" :key="day" class="flex flex-col justify-center gap-2 text-sm">
        <label class="w-24 font-medium">{{ day }}:</label>
        <div class="flex items-center gap-2 w-full">
          <!-- Start Time Input with Clear Button -->
          <div class="relative w-1/2">
            <Input
              type="time"
              v-model="hoursData[day].start"
              class="w-full"
              @blur="validateTime(day)"
            />
            <button
              type="button"
              class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-red-500"
              @click="clearTime(day, 'start')"
              v-if="hoursData[day].start"
            >
              ✕
            </button>
          </div>

          <span>to</span>

          <!-- End Time Input with Clear Button -->
          <div class="relative w-1/2">
            <Input
              type="time"
              v-model="hoursData[day].end"
              class="w-full"
              @blur="validateTime(day)"
            />
            <button
              type="button"
              class="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-red-500"
              @click="clearTime(day, 'end')"
              v-if="hoursData[day].end"
            >
              ✕
            </button>
          </div>
        </div>
        <span v-if="errors[day]" class="text-red-500 text-sm">{{ errors[day] }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits, watchEffect } from 'vue'
import { Input } from '@/components/ui/input'
import { parse, format } from 'date-fns'

const props = defineProps({
  data: {
    type: Object,
    required: true,
  },
  title: {
    type: String,
    default: 'Operating Hours'
  }
})

const emit = defineEmits(['update:modelValue'])

// Local copy of operating hours for two-way binding
const hoursData = ref({
  Monday: { start: '09:00', end: '17:00' },
  Tuesday: { start: '09:00', end: '17:00' },
  Wednesday: { start: '09:00', end: '17:00' },
  Thursday: { start: '09:00', end: '17:00' },
  Friday: { start: '09:00', end: '17:00' },
  Saturday: { start: '', end: '' },
  Sunday: { start: '', end: '' },
})

const errors = ref({})

// Function to validate time input in 24-hour format
const validateTime = (day) => {
  const startTime = hoursData.value[day].start
  const endTime = hoursData.value[day].end
  const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/

  if (startTime && !timeRegex.test(startTime)) {
    errors.value[day] = `Invalid start time format. Please use HH:MM (24-hour format).`
  } else if (endTime && !timeRegex.test(endTime)) {
    errors.value[day] = `Invalid end time format. Please use HH:MM (24-hour format).`
  } else {
    errors.value[day] = ''
  }

  emit('update:modelValue', formatOperatingHours())
}

// Function to clear the time input
const clearTime = (day, field) => {
  hoursData.value[day][field] = ''
  errors.value[day] = ''
  emit('update:modelValue', formatOperatingHours())
}

// Function to transform operating hours to desired format
const formatOperatingHours = () => {
  const formatted = {}
  for (const [day, { start, end }] of Object.entries(hoursData.value)) {
    if (start && end) {
      formatted[day] = `${convertTo12HourFormat(start)} – ${convertTo12HourFormat(end)}`
    } else {
      formatted[day] = 'Closed'
    }
  }
  return formatted
}

// Helper function to convert time to 12-hour format using date-fns
const convertTo12HourFormat = (time) => {
  try {
    const parsedTime = parse(time, 'HH:mm', new Date())
    return format(parsedTime, 'h:mma')
  } catch (error) {
    console.error('Error converting time:', time, error)
    return ''
  }
}

const transformOperatingHours = (data) => {
  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
  const transformed = {}

  days.forEach((day) => {
    if (data[day] && data[day] !== 'Closed') {
      const [start, end] = data[day]
        .split('–')
        .map((time) => time.trim().replace(/[^\x00-\x7F]/g, ''))

      transformed[day] = {
        start: start ? convertTo24HourFormat(start) : '',
        end: end ? convertTo24HourFormat(end) : '',
      }
    } else {
      transformed[day] = { start: '', end: '' }
    }
  })

  return transformed
}

// Helper function to convert time to 24-hour format using date-fns
const convertTo24HourFormat = (time) => {
  try {
    const parsedTime = parse(time, 'h:mma', new Date())
    return format(parsedTime, 'HH:mm')
  } catch (error) {
    console.error('Error parsing time:', time, error)
    return ''
  }
}

onMounted(() => {
  if (props.data) {
    hoursData.value = transformOperatingHours(props.data)
    emit('update:modelValue', formatOperatingHours())
  }
})
</script>
