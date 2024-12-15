<template>
  <form class="flex flex-col gap-y-4" @submit="onSubmit" enctype="multipart/form-data">
    <!-- Image Upload Field with Preview -->
    <FormField v-slot="{ componentField }" name="image">
      <FormItem>
        <FormLabel>Image</FormLabel>
        <FormControl>
          <div class="relative w-48 h-48">
            <input type="file" @change="handleImageUpload" class="hidden" ref="fileInput" />
            <div
              class="w-48 h-48 rounded-full border-2 border-dashed flex items-center justify-center cursor-pointer"
              @click="triggerFileInput"
            >
              <img
                v-if="imagePreview"
                :src="imagePreview"
                alt="Image Preview"
                class="w-48 h-48 rounded-full object-cover"
              />
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
          <Input type="text" placeholder="Menu name" v-bind="componentField" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Description Field -->
    <FormField v-slot="{ componentField }" name="description">
      <FormItem>
        <FormLabel>Description</FormLabel>
        <FormControl>
          <Textarea class="w-full border rounded-md p-2" rows="4" placeholder="Description" v-bind="componentField" />
        </FormControl>
        <FormMessage />
      </FormItem>
    </FormField>

    <!-- Two-Column Layout for Smaller Fields -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Menu Category Field -->
      <FormField v-slot="{ componentField }" name="category">
        <FormItem>
          <FormLabel>Menu Category</FormLabel>
          <Select v-bind="componentField">
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select a category" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectGroup>
                <SelectItem
                  v-for="category in menuCategories"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.name }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Restaurant Field -->
      <FormField v-slot="{ componentField }" name="restaurant">
        <FormItem>
          <FormLabel>Restaurant</FormLabel>
          <Select v-bind="componentField">
            <FormControl>
              <SelectTrigger>
                <SelectValue placeholder="Select a restaurant" />
              </SelectTrigger>
            </FormControl>
            <SelectContent>
              <SelectGroup>
                <SelectItem
                  v-for="restaurant in restaurants"
                  :key="restaurant.id"
                  :value="restaurant.id"
                >
                  {{ restaurant.name }}
                </SelectItem>
              </SelectGroup>
            </SelectContent>
          </Select>
          <FormMessage />
        </FormItem>
      </FormField>

      <!-- Dish Status Field -->
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

      <!-- Cost Field -->
      <FormField v-slot="{ componentField }" name="cost">
        <FormItem>
          <FormLabel>Cost</FormLabel>
          <FormControl>
            <Input type="number" step="0.01" placeholder="Menu cost" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <!-- Submit Button -->
    <div class="mt-6 flex gap-4 items-start">
      <Button type="submit">{{ isEditMode ? 'Update Menu' : 'Create Menu' }}</Button>

      <div class="flex items-start gap-4 relative">
        <!-- Delete Button -->
        <Button 
          v-if="isEditMode" 
          type="button" 
          variant="destructive" 
          @click="toggleDeleteConfirmation"
        >
          Delete Menu
        </Button>

        <!-- Confirmation Prompt -->
        <div v-if="showDeleteConfirmation" class="flex flex-col gap-y-4 ml-4">
          <span>Are you sure you want to delete this menu?</span>
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
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { toast } from '@/components/ui/toast'
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem, SelectGroup } from '@/components/ui/select'
import { useCategories } from '@/composables/useCategory'
import { useApiEndpoints } from '@/composables/useApiRestaurants.js'

const { fetchRestaurantsMini, deleteMenu } = useApiEndpoints()
const router = useRouter()
const route = useRoute()

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

// Validation schema
const menuFormSchema = toTypedSchema(
  z.object({
    name: z.string().min(2, 'Name is required'),
    description: z.string().min(10, 'Description is required'),
    cost: z.number().min(1, 'Cost is required'),
    category: z.any({ required_error: 'Please select a category.' }),
    restaurant: z.any({ required_error: 'Please select a restaurant.' }),
    status: z.enum(['active', 'inactive'], { required_error: 'Please select a status.' }),
  })
)

// Initialize form
const { handleSubmit, setFieldValue } = useForm({
  validationSchema: menuFormSchema,
  initialValues: {
    name: props.initialData?.name || '',
    description: props.initialData?.description || '',
    cost: props.initialData?.cost ? parseFloat(props.initialData.cost) : 0,
    status: props.initialData?.status || '',
    category: props.initialData?.category || '',
    restaurant: props.initialData?.restaurant_details?.id || '',
  },
})

// Fetch menu categories and restaurants
const { fetchMenuCategories } = useCategories()
const menuCategories = ref([])
const restaurants = ref([])

onMounted(async () => {
  try {
    menuCategories.value = await fetchMenuCategories()
    restaurants.value = await fetchRestaurantsMini()
  } catch (error) {
    console.error('Error fetching data:', error)
  }
})

// Handle form submission
const onSubmit = handleSubmit((values) => {
  const formData = new FormData()
  formData.append('name', values.name)
  formData.append('description', values.description)
  formData.append('cost', values.cost)
  formData.append('category', values.category)
  formData.append('restaurant', values.restaurant)
  formData.append('status', values.status)

  if (imageFile.value) {
    formData.append('image', imageFile.value)
  }

  emit('submit', formData)
})

// Image upload logic
const imageFile = ref(null)
const imagePreview = ref(props.initialData?.image || props.initialData?.images[0]?.image || null)
const fileInput = ref(null)

const triggerFileInput = () => fileInput.value.click()

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
    setFieldValue('image', file)
  }
}

// Delete confirmation logic
const showDeleteConfirmation = ref(false)
const isDeleting = ref(false)

const toggleDeleteConfirmation = () => {
  showDeleteConfirmation.value = !showDeleteConfirmation.value
}

const handleDelete = async () => {
  try {
    isDeleting.value = true
    await deleteMenu(route.params.menu)

    toast({
      title: 'Menu Deleted Successfully',
      description: 'The menu has been deleted.',
      variant: 'success',
      position: 'center',
    })

    router.push('/menus')
  } catch (error) {
    console.error('Error deleting menu:', error)

    toast({
      title: 'Error Deleting Menu',
      description: 'An error occurred while deleting the menu.',
      variant: 'destructive',
      position: 'center',
    })
  } finally {
    isDeleting.value = false
    showDeleteConfirmation.value = false
  }
}
</script>

