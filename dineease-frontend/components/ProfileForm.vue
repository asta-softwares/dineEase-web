<template>
  <div>
    <h3 class="text-lg font-medium">Profile</h3>
    <p class="text-sm text-muted-foreground">
      Update your account settings. This is how others will see you on the site.
    </p>
  </div>
  <Separator />
  <form class="space-y-8" @submit="onSubmit">
    <!-- Address Field -->
    <FormField v-slot="{ componentField }" name="address">
      <FormItem>
        <FormLabel>Address</FormLabel>
        <FormControl>
          <Input type="text" placeholder="Address" v-bind="componentField" />
        </FormControl>
        <FormDescription>Your residential address.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- City Field -->
    <FormField v-slot="{ componentField }" name="city">
      <FormItem>
        <FormLabel>City</FormLabel>
        <FormControl>
          <Input type="text" placeholder="City" v-bind="componentField" />
        </FormControl>
        <FormDescription>Your city of residence.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Province Field -->
    <FormField v-slot="{ componentField }" name="province">
      <FormItem>
        <FormLabel>Province</FormLabel>
        <Select v-bind="componentField">
          <FormControl>
            <SelectTrigger>
              <SelectValue placeholder="Select a province" />
            </SelectTrigger>
          </FormControl>
          <SelectContent>
            <SelectGroup>
              <SelectItem
                v-for="province in CANADA_PROVINCE_CHOICES"
                :key="province.code"
                :value="province.code"
              >
                {{ province.name }}
              </SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
        <FormDescription>Your province of residence.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Coordinates Field -->
    <FormField v-slot="{ componentField }" name="coordinates">
      <FormItem>
        <FormLabel>Coordinates</FormLabel>
        <FormControl>
          <Input type="text" placeholder="Coordinates (e.g., 125.404, 7.316)" v-bind="componentField" disabled />
        </FormControl>
        <FormDescription>Your location coordinates in [longitude, latitude] format. Click on the map to change your location.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Mini Map Component -->
    <MiniMap class="h-[500px] my-4" v-model="selectedCoordinates" :coordinates="selectedCoordinates" :is-edit-mode="true" />

    <div class="flex justify-start">
      <Button type="submit">Update Account</Button>
    </div>
  </form>
</template>

<script setup>
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { FormField, FormItem, FormLabel, FormControl, FormDescription, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { toast } from '@/components/ui/toast'
import { ref, watch, computed } from 'vue'
import * as z from 'zod'
import { useAuthApi } from '@/composables/useAuthApi'
import MiniMap from '@/components/Maps/MiniMap.vue'
import { CANADA_PROVINCE_CHOICES } from '@/lib/constants'

const { updateUser } = useAuthApi()

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['submit'])

const selectedCoordinates = ref(props.user.profile?.coordinates || [0, 0])

// Validation schema
const accountFormSchema = toTypedSchema(
  z.object({
    address: z.string().optional(),
    city: z.string().optional(),
    province: z.string().optional(),
    coordinates: z.string().optional(),
  })
)

// Create the form
const { handleSubmit, setFieldValue } = useForm({
  validationSchema: accountFormSchema,
  initialValues: {
    address: props.user.profile?.address || '',
    city: props.user.profile?.city || '',
    province: props.user.profile?.province || '',
    coordinates: props.user.profile?.coordinates?.join(', ') || '0, 0',
  },
})

watch(selectedCoordinates, (newCoordinates) => {
  setFieldValue('coordinates', newCoordinates.join(', '))
})

// Handle form submission
const onSubmit = handleSubmit(async (values) => {
  try {
    const payload = {
      profile: {
        address: values.address || undefined,
        city: values.city || undefined,
        province: values.province || undefined,
        coordinates: selectedCoordinates.value || undefined,
      },
    }

    console.log('Payload:', payload)

    await updateUser(payload)

    toast({
      title: 'Profile Updated Successfully!',
      description: 'Your account information has been updated.',
    })

    emit('submit', values)
  } catch (error) {
    console.error('Error updating profile:', error)

    toast({
      title: 'Profile Update Failed',
      description: 'There was an error updating your profile. Please try again.',
      variant: 'destructive',
    })
  }
})
</script>
