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
        <FormDescription>Upload an image representing your restaurant. Recommended size: 300x300 pixels.</FormDescription>
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
          <FormDescription>Enter the official name of your restaurant.</FormDescription>
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Service Type Field -->
      <FormField v-slot="{ componentField }" name="service_type">
        <FormItem>
          <FormLabel>Service Type</FormLabel>
          <Select v-bind="componentField">
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select service type" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectGroup>
                <SelectItem value="dine-in">Dine-in</SelectItem>
                <SelectItem value="takeout">Takeout</SelectItem>
                <SelectItem value="both">Both</SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
          <FormDescription>Specify if your restaurant offers dine-in, takeout, or both.</FormDescription>
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
          <FormDescription>Provide the full address of your restaurant.</FormDescription>
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
          <FormDescription>Enter a valid email address for customer inquiries.</FormDescription>
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
          <FormDescription>Provide a contact number for customers to reach your restaurant.</FormDescription>
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Ratings Field -->
      <FormField v-slot="{ componentField }" name="ratings">
        <FormItem>
          <FormLabel>Ratings</FormLabel>
          <FormControl>
            <Input type="number" step="0.1" min="0" max="5" placeholder="Ratings (0.0 - 5.0)" v-bind="componentField" />
          </FormControl>
          <FormDescription>Provide a rating between 0 and 5 for your restaurant.</FormDescription>
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
          <FormDescription>Set the current status of your restaurant (Active or Inactive).</FormDescription>
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
          <FormDescription>Select a category that best describes your restaurant.</FormDescription>
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <OperatingHours v-model="operatingHours" :data="initialData?.operating_hours" />

    <!-- Coordinates Field -->
    <FormField v-slot="{ componentField }" name="coordinates">
      <FormItem>
        <FormLabel>Coordinates</FormLabel>
        <FormControl>
          <Input type="text" placeholder="Coordinates (e.g., 125.404, 7.316)" v-bind="componentField" disabled />
        </FormControl>
        <FormDescription>Your location coordinates in [longitude, latitude] format. Click on the map to set your location.</FormDescription>
        <FormMessage />
      </FormItem>
    </FormField>

    <MiniMap class="h-[500px] my-4" v-model="selectedCoordinates" :coordinates="selectedCoordinates" :is-edit-mode="true" />

    <!-- Stripe Account Field -->
    <FormField v-slot="{ componentField }" name="stripe_account_id">
      <FormItem>
        <FormLabel>Stripe Account</FormLabel>
        <FormControl>
          <Input type="text" v-bind="componentField" disabled />
        </FormControl>
        <FormDescription>Your Stripe account ID for receiving payments.</FormDescription>
        <p v-if="!stripeAccountId" class="text-red-500">
          You have not set up your Stripe account. 
          <a href="#" @click.prevent="handleStripeOnboarding" class="text-blue-500 underline">
            Click here to register.
          </a>
        </p>
      </FormItem>
    </FormField>

    <!-- Submit Button -->
    <div class="mt-6 flex gap-4 items-start">
      <Button type="submit">{{ isEditMode ? 'Update Restaurant' : 'Create Restaurant' }}</Button>
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
import MiniMap from '@/components/Maps/MiniMap.vue'

const { deleteRestaurant, createStripeOnboardingLink } = useApiEndpoints()
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

console.log(props.initialData)

const emit = defineEmits(['submit'])
const imageFile = ref(null)
const imagePreview = ref(props.initialData?.image || null)
const fileInput = ref(null)
const operatingHours = ref({})
const restaurantCategories = ref([])
const { fetchRestaurantCategories } = useCategories()
const selectedCoordinates = ref(props.initialData?.coordinates || [])
const stripeAccountId = ref(props.initialData?.stripe_account_id || '');

onMounted(async () => {
  restaurantCategories.value = await fetchRestaurantCategories()
})

const handleStripeOnboarding = async () => {
  const restaurantId = props.initialData?.id;
  if (!restaurantId) return;

  const { success, onboardingUrl } = await createStripeOnboardingLink(restaurantId);

  if (success && onboardingUrl) {
    window.location.href = onboardingUrl;
  }
};

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
    category: z.any().optional(),
    coordinates: z.string().optional(),
    coordinates: z.string().optional(),
    stripe_account_id: z.string().optional(),
  })
)

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
    coordinates: props.initialData?.coordinates?.join(', ') || '0, 0',
    stripe_account_id: props.initialData?.stripe_account_id || ''
  },
})

const toggleDeleteConfirmation = () => {
  showDeleteConfirmation.value = !showDeleteConfirmation.value
}

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

watch(selectedCoordinates, (newCoordinates) => {
  setFieldValue('coordinates', newCoordinates.join(', '))
})

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
  formData.append('coordinates', JSON.stringify(selectedCoordinates.value) || undefined);

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

  emit('submit', formData);
});

</script>
