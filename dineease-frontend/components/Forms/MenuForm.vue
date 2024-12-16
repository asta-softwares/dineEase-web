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
            <Input
              type="number"
              step="0.01"
              placeholder="Menu cost"
              v-bind="componentField"
              @input="menuPrice = parseFloat($event.target.value) || 0"
            />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
    </div>

    <div v-if="promos.length" class="flex flex-col gap-4 mt-4">
      <h3 class="text-lg font-semibold flex items-center justify-between">
        Select a Promo
        <span v-if="totalDiscount" class="text-primary text-sm">
          Expected Discount: ${{ totalDiscount }} (Final Price: ${{ discountedPrice }})
        </span>
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="promo in promos"
          :key="promo.id"
          class="flex flex-col gap-2 p-4 border rounded-lg shadow-sm cursor-pointer"
          @click="togglePromoSelection(promo)"
          :class="{ 'border-primary': selectedPromoIds.includes(promo.id) }"
        >
          <!-- Promo Name -->
          <div class="flex items-center justify-between">
            <h3 class="text-lg font-semibold">{{ promo.name }}</h3>
          </div>
    
          <!-- Promo Description -->
          <p class="text-sm text-gray-600">{{ promo.description }}</p>
    
          <!-- Discount -->
          <p class="text-sm font-medium">
            Discount:
            <span class="text-primary">
              {{ promo.discount_type === 'percentage' ? `${promo.discount}%` : `$${promo.discount}` }}
            </span>
          </p>
    
          <!-- Selected Indicator -->
          <div v-if="selectedPromoIds.includes(promo.id)" class="text-sm text-primary mt-2">
            Selected Promo
          </div>
        </div>
      </div>
          
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
import { Badge } from '@/components/ui/badge'
import { useCategories } from '@/composables/useCategory'
import { useApiEndpoints } from '@/composables/useApiRestaurants.js'

const { fetchRestaurantsMini, fetchPromosByRestaurant, deleteMenu } = useApiEndpoints()
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
const { handleSubmit, setFieldValue, values } = useForm({
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
const promos = ref([])
const selectedPromoIds = ref(props.initialData?.promos || [])
const selectedPromos = ref([])
const menuPrice = ref(props.initialData?.cost ? parseFloat(props.initialData.cost) : 0)
const imageFile = ref(null)
const imagePreview = ref(props.initialData?.image || props.initialData?.images[0]?.image || null)
const fileInput = ref(null)

onMounted(async () => {
  try {
    menuCategories.value = await fetchMenuCategories()
    restaurants.value = await fetchRestaurantsMini()

    // If there's an initial restaurant, fetch promos for that restaurant
    if (values.restaurant) {
      await loadPromos(values.restaurant)
    }
  } catch (error) {
    console.error('Error fetching data:', error)
  }
})

const triggerFileInput = () => fileInput.value.click()

const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    imageFile.value = file
    imagePreview.value = URL.createObjectURL(file)
    setFieldValue('image', file)
  }
}

// Fetch promos when a restaurant is selected
const loadPromos = async (restaurantId) => {
  try {
    promos.value = await fetchPromosByRestaurant(restaurantId, 'menu')
    console.log("promos", promos.value)
  } catch (error) {
    console.error('Error fetching promos:', error)
  }
}

// Watch for restaurant selection change
watch(() => values.restaurant, (newRestaurantId) => {
  if (newRestaurantId) {
    loadPromos(newRestaurantId)
  } else {
    promos.value = []
    selectedPromoIds.value = null
  }
})

// Toggle promo selection
const togglePromoSelection = (promo) => {
  const index = selectedPromoIds.value.indexOf(promo.id)
  if (index === -1) {
    selectedPromoIds.value.push(promo.id)
    selectedPromos.value.push(promo)
  } else {
    selectedPromoIds.value.splice(index, 1)
    selectedPromos.value.splice(index, 1)
  }
}

// Calculate total discount relative to menu price
const totalDiscount = computed(() => {
  let discountAmount = 0

  selectedPromos.value.forEach((promo) => {
    if (promo.discount_type === 'percentage') {
      discountAmount += (menuPrice.value * parseFloat(promo.discount)) / 100
    } else if (promo.discount_type === 'fixed') {
      discountAmount += parseFloat(promo.discount)
    }
  })

  return discountAmount.toFixed(2)
})

// Calculate the final discounted price
const discountedPrice = computed(() => {
  const finalPrice = menuPrice.value - parseFloat(totalDiscount.value)
  return finalPrice > 0 ? finalPrice.toFixed(2) : '0.00'
})

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

// Handle form submission
const onSubmit = handleSubmit((values) => {
  const formData = new FormData();
  formData.append('name', values.name);
  formData.append('description', values.description);
  formData.append('cost', values.cost);
  formData.append('category', values.category);
  formData.append('restaurant', values.restaurant);
  formData.append('status', values.status);

  if (selectedPromoIds.value.length > 0) {
    selectedPromoIds.value.forEach(promoId => {
      formData.append('promos', promoId);
    });
  }

  if (imageFile.value) {
    formData.append('image', imageFile.value);
  }

  console.log('FINAL FormData Contents:');
  for (const [key, value] of formData.entries()) {
    console.log(`${key}:`, value);
  }

  emit('submit', formData);
});
</script>


