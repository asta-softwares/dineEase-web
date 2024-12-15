<template>
    <div class="border p-4 rounded-md my-4">
      <h2 class="text-lg font-semibold mb-2">Operating Hours</h2>
      <div class="grid grid-cols-2 gap-4">
        <div v-for="(hours, day) in hoursData" :key="day" class="flex flex-col justify-center gap-2 text-sm">
            <label class="w-24 font-medium">{{ day }}:</label>
            <div class="flex items-center gap-2 w-full">
              <Input
                type="time"
                v-model="hoursData[day].start"
                class="w-1/2"
                @blur="validateTime(day, 'start')"
              />
              <span>to</span>
              <Input
                type="time"
                v-model="hoursData[day].end"
                class="w-1/2"
                @blur="validateTime(day, 'end')"
              />
            </div>
            <span v-if="errors[day]" class="text-red-500 text-sm">{{ errors[day] }}</span>
          </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, defineProps, defineEmits } from 'vue'
  import { Input } from '@/components/ui/input'
  import { parse, format } from 'date-fns'

  // Props to receive initial operating hours
  const props = defineProps({
    modelValue: {
      type: Object,
      required: true,
    },
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
  const validateTime = (day, field) => {
    const time = hoursData.value[day][field]
    const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/
  
    if (time && !timeRegex.test(time)) {
      errors.value[day] = `Invalid ${field} time format. Please use HH:MM (24-hour format).`
    } else {
      errors.value[day] = ''
    }
  
    emit('update:modelValue', hoursData.value)
  }

  const transformOperatingHours = (data) => {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    const transformed = {}

    days.forEach((day) => {
        if (data[day]) {
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

      console.log('transformed:', JSON.stringify(transformed, null, 2))
      return transformed
  }

  // Helper function to convert time to 24-hour format using date-fns
  const convertTo24HourFormat = (time) => {
    try {
      const parsedTime = parse(time, 'hh:mma', new Date())
      return format(parsedTime, 'HH:mm')
    } catch (error) {
      console.error('Error parsing time:', time, error)
      return ''
    }
  }

  watchEffect(() => {
    if (props.modelValue) {
      hoursData.value = transformOperatingHours(props.modelValue)
    }
  })
  
  </script>