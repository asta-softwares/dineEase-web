<template>
    <form @submit="handleSubmit">
      <!-- Image Upload Field with Preview -->
      <FormField v-slot="{ componentField }" name="image">
        <FormItem>
          <FormLabel>Image</FormLabel>
          <FormControl>
            <div class="relative w-48 h-48">
              <input type="file" @change="handleImageUpload" class="hidden" ref="fileInput" />
              <div class="w-48 h-48 rounded-full border-2 border-dashed flex items-center justify-center cursor-pointer" @click="triggerFileInput">
                <img v-if="imagePreview" :src="imagePreview" alt="Image Preview" class="w-48 h-48 rounded-full object-cover" />
                <div v-else class="w-48 h-48 flex items-center justify-center rounded-full bg-gray-200">
                  <span class="text-gray-500">Upload Image</span>
                </div>
              </div>
            </div>
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Name Field -->
      <FormField v-slot="{ componentField }" name="name">
        <FormItem>
          <FormLabel>Name</FormLabel>
          <FormControl>
            <Input type="text" placeholder="Restaurant name" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Description Field -->
      <FormField v-slot="{ componentField }" name="description">
        <FormItem>
          <FormLabel>Description</FormLabel>
          <FormControl>
            <Textarea class="w-full border rounded-md p-2" rows="4" placeholder="Description" v-bind="componentField"></Textarea>
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Service Type Field -->
      <FormField v-slot="{ componentField }" name="service_type">
        <FormItem>
          <FormLabel>Service Type</FormLabel>
          <FormControl>
            <select class="w-full border rounded-md p-2" v-bind="componentField">
              <option value="dine-in">Dine-in</option>
              <option value="takeout">Takeout</option>
              <option value="both">Both</option>
            </select>
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Location Field -->
      <FormField v-slot="{ componentField }" name="location">
        <FormItem>
          <FormLabel>Location</FormLabel>
          <FormControl>
            <Input type="text" placeholder="Restaurant location" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Email Field -->
      <FormField v-slot="{ componentField }" name="email">
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <Input type="email" placeholder="Restaurant email" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Telephone Field -->
      <FormField v-slot="{ componentField }" name="telephone">
        <FormItem>
          <FormLabel>Telephone</FormLabel>
          <FormControl>
            <Input type="text" placeholder="Restaurant telephone" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Ratings Field -->
      <FormField v-slot="{ componentField }" name="ratings">
        <FormItem>
          <FormLabel>Ratings</FormLabel>
          <FormControl>
            <Input type="number" step="0.5" min="0" max="5" placeholder="Ratings (0.0 - 5.0)" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>

      <OperatingHours v-model="operatingHours" />
  
      <!-- Social Media Links Section -->
      <div class="border p-4 rounded-md my-4">
        <h2 class="text-lg font-semibold mb-2">Social Media Links</h2>
        <div v-for="(link, index) in socialMediaLinks" :key="index" class="flex items-center gap-2 mb-2">
          <Input type="text" v-model="socialMediaLinks[index].platform" placeholder="Platform (e.g., Facebook)" class="w-1/3" />
          <Input type="url" v-model="socialMediaLinks[index].link" placeholder="Link (e.g., https://facebook.com/yourpage)" class="w-2/3" />
          <Button type="button" @click="removeSocialMediaLink(index)" variant="outline">Remove</Button>
        </div>
        <Button type="button" @click="addSocialMediaLink" class="mt-2">Add Social Media</Button>
      </div>
  
      <!-- Submit Button -->
      <div class="mt-6">
        <Button type="submit">{{ isEditMode ? 'Update Restaurant' : 'Create Restaurant' }}</Button>
      </div>
    </form>
  </template>
  
  <script setup>
  import { useForm } from 'vee-validate'
  import { toTypedSchema } from '@vee-validate/zod'
  import * as z from 'zod'
  import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
  import { Input } from '@/components/ui/input'
  import { Textarea } from '@/components/ui/textarea'
  import { Button } from '@/components/ui/button'
  import OperatingHours from '../Time/OperatingHours.vue'
  import { ref, watchEffect } from 'vue'
  
  const props = defineProps({
    initialData: {
      type: Object,
      default: null,
    },
  })
  
  const emit = defineEmits(['submit'])
  
  // Define the validation schema
  const restaurantFormSchema = toTypedSchema(
    z.object({
      name: z.string().min(2, 'Name is required'),
      description: z.string().min(10, 'Description is required'),
      location: z.string().min(2, 'Location is required'),
      service_type: z.string(),
      email: z.string().email('Invalid email').optional(),
      telephone: z.string().min(10, 'Telephone is required'),
      ratings: z.number().min(0).max(5).optional(),
    })
  )
  
  // Initialize the form with `useForm`
  const { handleSubmit, resetForm, setFieldValue } = useForm({
    validationSchema: restaurantFormSchema,
    initialValues: props.initialData || {
      name: '',
      description: '',
      location: '',
      service_type: 'both',
      email: '',
      telephone: '',
      ratings: 0,
    },
  })
  
  // Image upload and preview logic
  const imageFile = ref(null)
  const imagePreview = ref(props.initialData?.image || null)
  const fileInput = ref(null)
  
  const triggerFileInput = () => {
    fileInput.value.click()
  }
  
  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      imageFile.value = file
      imagePreview.value = URL.createObjectURL(file)
      setFieldValue('image', file) // Update form field with the uploaded file
    }
  }

  // Social media links
  const socialMediaLinks = ref([{ platform: '', link: '' }])
  
  const addSocialMediaLink = () => {
    socialMediaLinks.value.push({ platform: '', link: '' })
  }
  
  const removeSocialMediaLink = (index) => {
    socialMediaLinks.value.splice(index, 1)
  }
  
  // Handle form submission
  const onSubmit = handleSubmit((values) => {
    const data = { ...values, image: imageFile.value }
    console.log('Operating Hours:', operatingHours.value)
    emit('submit', data)
  })
  </script>
  
  