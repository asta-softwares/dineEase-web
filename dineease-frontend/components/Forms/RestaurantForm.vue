<template>
  <form class="flex flex-col gap-y-4" enctype="multipart/form-data" @submit="onSubmit">
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

    <!-- Two-Column Layout for Smaller Fields -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
      
      <!-- Status Field -->
      <FormField v-slot="{ componentField }" name="status">
        <FormItem>
          <FormLabel>Status</FormLabel>
          <Select v-bind="componentField">
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      </FormField>

      
    <!-- Category Field -->
    <FormField v-slot="{ componentField }" name="category">
      <FormItem>
        <FormLabel>Category</FormLabel>
        <FormControl>
          <Select v-bind="componentField">
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectGroup>
                <SelectItem v-for="category in restaurantCategories" :key="category.id" :value="category.id">
                  {{ category.name }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    </div>
    <!-- Operating Hours Component -->
    <OperatingHours v-model="operatingHours" :data="initialData?.operating_hours" />

    <!-- Submit Button -->
    <div class="mt-6 flex gap-4 items-start">
      <Button type="submit">{{ isEditMode ? 'Update Restaurant' : 'Create Restaurant' }}</Button>
    
      <div class="flex items-start gap-4 relative">
        <!-- Delete Button -->
        <Button 
          v-if="isEditMode" 
          type="button" 
          variant="destructive" 
          @click="toggleDeleteConfirmation"
        >
          Delete Restaurant
        </Button>
    
        <!-- Confirmation Prompt -->
        <div v-if="showDeleteConfirmation" class="flex flex-col gap-y-4 ml-4">
          <span>Are you sure you want to delete this restaurant?</span>
          <div class="flex items-center gap-2">
            <Button 
              type="button" 
              variant="destructive" 
              size="sm" 
              @click="handleDelete"
              :disabled="isDeleting"
            >
              {{ isDeleting ? 'Deleting...' : 'Confirm Delete' }}
            </Button>
            <Button 
              type="button" 
              variant="outline" 
              size="sm" 
              @click="toggleDeleteConfirmation"
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  </form>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem, SelectGroup } from '@/components/ui/select'
import { useCategories } from '@/composables/useCategory'
import OperatingHours from '../Time/OperatingHours'
import { useApiEndpoints } from '@/composables/useApiRestaurants'
import { toast } from '@/components/ui/toast'

const { deleteRestaurant } = useApiEndpoints()
const router = useRouter()
const route = useRoute()
const isDeleting = ref(false)
const showDeleteConfirmation = ref(false)

const props = defineProps({
  initialData: {
    type: Object,
    default: null,
  },
  isEditMode: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['submit'])
const imageFile = ref(null)
const imagePreview = ref(props.initialData?.image || null)
const fileInput = ref(null)
const operatingHours = ref({})
const restaurantCategories = ref([])
const { fetchRestaurantCategories } = useCategories()

onMounted(async () => {
  restaurantCategories.value = await fetchRestaurantCategories()
})

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
    status: z.string().optional(),
    category: z.string().optional(),
  })
)

// Initialize the form with `useForm`
const { handleSubmit, resetForm, setFieldValue } = useForm({
  validationSchema: restaurantFormSchema,
  initialValues: {
    name: props.initialData?.name || '',
    description: props.initialData?.description || '',
    location: props.initialData?.location || '',
    service_type: props.initialData?.service_type || 'both',
    email: props.initialData?.email || '',
    telephone: props.initialData?.telephone || '',
    ratings: props.initialData?.ratings || 0,
    status: props.initialData?.status || 'active',
    category: props.initialData?.category || '',
  },
})

const toggleDeleteConfirmation = () => {
  showDeleteConfirmation.value = !showDeleteConfirmation.value
}

// Function to handle delete action
const handleDelete = async () => {
  try {
    isDeleting.value = true
    await deleteRestaurant(route.params.restaurant)

    // Show success toast notification
    toast({
      title: 'Restaurant Deleted Successfully',
      description: 'The restaurant has been deleted.',
      variant: 'success',
      position: 'center',
    })

    // Redirect to the restaurants page
    router.push('/restaurants')
  } catch (error) {
    console.error('Error deleting restaurant:', error)

    // Show error toast notification
    toast({
      title: 'Error Deleting Restaurant',
      description: 'An error occurred while deleting the restaurant. Please try again.',
      variant: 'destructive',
      position: 'center',
    })
  } finally {
    isDeleting.value = false
    showDeleteConfirmation.value = false
  }
}

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
    setFieldValue('image', file)
  }
}

const onSubmit = handleSubmit((values) => {
  const formData = new FormData();

  formData.append('name', values.name);
  formData.append('description', values.description);
  formData.append('location', values.location);
  formData.append('service_type', values.service_type);
  formData.append('email', values.email ?? '');
  formData.append('telephone', values.telephone);
  formData.append('ratings', values.ratings ?? '');
  formData.append('status', values.status);
  formData.append('category', values.category ?? '');

  if (operatingHours.value) {
    formData.append('operating_hours', JSON.stringify(operatingHours.value));
  }

  // if (socialMediaLinks.value.length > 0) {
  //   socialMediaLinks.value.forEach((link, index) => {
  //     formData.append(`social_media_links[${index}][platform]`, link.platform);
  //     formData.append(`social_media_links[${index}][link]`, link.link);
  //   });
  // }

  // Append image if it exists
  if (imageFile.value) {
    formData.append('image', imageFile.value);
  }

  // Log the contents of FormData for debugging
  console.log('FINAL FormData Contents:');
  for (const [key, value] of formData.entries()) {
    console.log(`${key}:`, value);
  }

  emit('submit', formData);
});

</script>
