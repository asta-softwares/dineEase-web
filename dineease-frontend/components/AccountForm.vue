<template>
  <div>
    <h3 class="text-lg font-medium">Account</h3>
    <p class="text-sm text-muted-foreground">
      Update your account settings. Some fields cannot be edited.
    </p>
  </div>
  <Separator />
  <form class="space-y-8" @submit="onSubmit">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- First Name Field -->
      <FormField v-slot="{ componentField }" name="first_name">
        <FormItem>
          <FormLabel>First Name</FormLabel>
          <FormControl>
            <Input type="text" placeholder="First Name" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Last Name Field -->
      <FormField v-slot="{ componentField }" name="last_name">
        <FormItem>
          <FormLabel>Last Name</FormLabel>
          <FormControl>
            <Input type="text" placeholder="Last Name" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <!-- Username Field (Disabled) -->
    <FormField v-slot="{ componentField }" name="username">
      <FormItem>
        <FormLabel>Username</FormLabel>
        <FormControl>
          <Input type="text" v-bind="componentField" disabled />
        </FormControl>
        <FormDescription>Your unique username. This cannot be changed.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Email Field (Disabled) -->
    <FormField v-slot="{ componentField }" name="email">
      <FormItem>
        <FormLabel>Email</FormLabel>
        <FormControl>
          <Input type="email" v-bind="componentField" disabled />
        </FormControl>
        <FormDescription>Your email address. This cannot be changed.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Phone Field (Disabled) -->
    <FormField v-slot="{ componentField }" name="phone">
      <FormItem>
        <FormLabel>Phone</FormLabel>
        <FormControl>
          <Input type="text" v-bind="componentField" disabled />
        </FormControl>
        <FormDescription>Your registered phone number. This cannot be changed.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Password Fields -->
    <div v-if="showPasswordFields" class="grid grid-cols-1 gap-4">
      <FormField v-slot="{ componentField }" name="current_password">
        <FormItem>
          <FormLabel>Current Password</FormLabel>
          <FormControl>
            <Input type="password" placeholder="Current Password" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ componentField }" name="new_password">
        <FormItem>
          <FormLabel>New Password</FormLabel>
          <FormControl>
            <Input type="password" placeholder="New Password" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <FormField v-slot="{ componentField }" name="confirm_password">
        <FormItem>
          <FormLabel>Confirm Password</FormLabel>
          <FormControl>
            <Input type="password" placeholder="Confirm Password" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <!-- Change Password Button -->
    <div>
      <Button type="button" variant="outline" @click="showPasswordFields = !showPasswordFields">
        {{ showPasswordFields ? 'Cancel Password Change' : 'Change Password' }}
      </Button>
    </div>

    <div class="flex justify-start">
      <Button type="submit">Update Account</Button>
    </div>
  </form>
</template>

<script setup>
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Separator } from '@/components/ui/separator'
import { toast } from '@/components/ui/toast'
import * as z from 'zod'
import { useAuthApi } from '@/composables/useAuthApi'

const { updateUser } = useAuthApi()
const showPasswordFields = ref(false)

const props = defineProps({
  user: {
    type: Object,
    default: null,
  },
})

const emit = defineEmits(['submit'])

const accountFormSchema = toTypedSchema(
  z.object({
    username: z.string().nonempty('Username is required'),
    email: z.string().email('Invalid email').nonempty('Email is required'),
    phone: z.string().nonempty('Phone is required'),
    first_name: z.string().min(2, 'First name is required'),
    last_name: z.string().min(2, 'Last name is required'),
    current_password: z.string().optional(),
    new_password: z.string().optional(),
    confirm_password: z.string().optional(),
  }).refine(data => !data.new_password || data.new_password === data.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  })
)

const { handleSubmit, setFieldValue } = useForm({
  validationSchema: accountFormSchema,
  initialValues: {
    username: props.user.username || '',
    email: props.user.email || '',
    phone: props.user.profile?.phone || '',
    first_name: props.user.first_name || '',
    last_name: props.user.last_name || '',
  },
})

const onSubmit = handleSubmit(async (values) => {
  try {
    const payload = {
      first_name: props.user.first_name || '',
      last_name: props.user.last_name || '',
      current_password: values.current_password || undefined,
      new_password: values.new_password || undefined,
      confirm_password: values.confirm_password || undefined,
      profile: {
        phone: props.user.profile?.phone || undefined,
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

