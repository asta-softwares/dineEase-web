<template>
    <form class="flex flex-col gap-y-4" @submit="onSubmit" enctype="multipart/form-data">
      <!-- Promo Name -->
      <FormField v-slot="{ componentField }" name="name">
        <FormItem>
          <FormLabel>Name</FormLabel>
          <FormControl>
            <Input type="text" placeholder="Promo name" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Description -->
      <FormField v-slot="{ componentField }" name="description">
        <FormItem>
          <FormLabel>Description</FormLabel>
          <FormControl>
            <Textarea rows="3" placeholder="Promo description" v-bind="componentField" />
          </FormControl>
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
  
      <!-- Discount and Discount Type -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField }" name="discount">
          <FormItem>
            <FormLabel>Discount</FormLabel>
            <FormControl>
              <Input type="number" step="0.01" placeholder="Discount" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
  
        <FormField v-slot="{ componentField }" name="discount_type">
          <FormItem>
            <FormLabel>Discount Type</FormLabel>
            <Select v-bind="componentField">
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Select discount type" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value="percentage">Percentage</SelectItem>
                <SelectItem value="fixed">Fixed Amount</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField }" name="promo_type">
            <FormItem>
            <FormLabel>Promo Type</FormLabel>
            <Select v-bind="componentField">
                <FormControl>
                <SelectTrigger>
                    <SelectValue placeholder="Select promo type" />
                </SelectTrigger>
                </FormControl>
                <SelectContent>
                <SelectItem value="menu">Menu</SelectItem>
                <SelectItem value="restaurant">Restaurant</SelectItem>
                </SelectContent>
            </Select>
            <FormMessage />
            </FormItem>
        </FormField>

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
    </div>
  
      <!-- Priority Index -->
      <FormField v-slot="{ componentField }" name="priority_index">
        <FormItem>
          <FormLabel>Priority Index</FormLabel>
          <FormControl>
            <Input type="number" placeholder="Priority Index" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Start Date and End Date -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField }" name="start_date">
          <FormItem>
            <FormLabel>Start Date</FormLabel>
            <FormControl>
              <Input type="date" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
  
        <FormField v-slot="{ componentField }" name="end_date">
          <FormItem>
            <FormLabel>End Date</FormLabel>
            <FormControl>
              <Input type="date" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>
  
      <!-- Minimum Order -->
      <FormField v-slot="{ componentField }" name="minimum_order">
        <FormItem>
          <FormLabel>Minimum Order</FormLabel>
          <FormControl>
            <Input type="number" step="0.01" placeholder="Minimum Order" v-bind="componentField" />
          </FormControl>
          <FormMessage />
        </FormItem>
      </FormField>
  
      <!-- Code and Usage Limit -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <FormField v-slot="{ componentField }" name="code">
          <FormItem>
            <FormLabel>Promo Code</FormLabel>
            <FormControl>
              <Input type="text" placeholder="Promo Code" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
  
        <FormField v-slot="{ componentField }" name="usage_limit">
          <FormItem>
            <FormLabel>Usage Limit</FormLabel>
            <FormControl>
              <Input type="number" placeholder="Usage Limit" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <OperatingHours v-model="timeOffer" :data="initialData?.time_offer" title="Time Offer" />
  
      <div class="mt-6 flex gap-4 items-start">
        <Button type="submit">{{ isEditMode ? 'Update Promo' : 'Create Promo' }}</Button>
    
        <div class="flex items-start gap-4 relative">
          <!-- Delete Button -->
          <Button
            v-if="isEditMode"
            type="button"
            variant="destructive"
            @click="toggleDeleteConfirmation"
          >
            Delete Promo
          </Button>
    
          <!-- Confirmation Prompt -->
          <div v-if="showDeleteConfirmation" class="flex flex-col gap-y-4 ml-4">
            <span>Are you sure you want to delete this promo?</span>
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
  import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from '@/components/ui/form'
  import { Input } from '@/components/ui/input'
  import { Textarea } from '@/components/ui/textarea'
  import { Button } from '@/components/ui/button'
  import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
  import { useApiEndpoints } from '@/composables/useApiRestaurants'
  import OperatingHours from '../Time/OperatingHours'
  import { toast } from '@/components/ui/toast'
  
  const { fetchRestaurantsMini, deletePromo  } = useApiEndpoints()
  const router = useRouter()
    const route = useRoute()
  const restaurants = ref([])
  const showDeleteConfirmation = ref(false)
    const isDeleting = ref(false)
    const timeOffer = ref({})

// Toggle delete confirmation
const toggleDeleteConfirmation = () => {
  showDeleteConfirmation.value = !showDeleteConfirmation.value
}

// Handle delete action
const handleDelete = async () => {
  try {
    isDeleting.value = true
    await deletePromo(route.params.promo)

    toast({
      title: 'Promo Deleted Successfully',
      description: 'The promo has been deleted.',
      variant: 'success',
      position: 'center',
    })

    router.push('/promos') // Redirect to the promo list after deletion
  } catch (error) {
    console.error('Error deleting promo:', error)

    toast({
      title: 'Error Deleting Promo',
      description: 'An error occurred while deleting the promo. Please try again.',
      variant: 'destructive',
      position: 'center',
    })
  } finally {
    isDeleting.value = false
    showDeleteConfirmation.value = false
  }
}
  
  onMounted(async () => {
    try {
      restaurants.value = await fetchRestaurantsMini()
    } catch (error) {
      console.error('Error fetching restaurants:', error)
    }
  })
  
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
  const promoFormSchema = toTypedSchema(
    z.object({
      name: z.string().min(2, 'Name is required'),
      description: z.string().min(10, 'Description is required'),
      discount: z.number().min(0.01, 'Discount is required'),
      discount_type: z.enum(['percentage', 'fixed']),
      restaurant: z.any({ required_error: 'Please select a restaurant.' }),
      priority_index: z.number().optional(),
      start_date: z.string().optional(),
      end_date: z.string().optional(),
      minimum_order: z.number().optional(),
      code: z.any().optional(),
      usage_limit: z.number().optional(),
      promo_type: z.enum(['menu', 'restaurant']),
      status: z.enum(['active', 'inactive'], { required_error: 'Please select a status.' }),
    })
  )
  
  const { handleSubmit, setFieldValue, values } = useForm({
  validationSchema: promoFormSchema,
  initialValues: {
    name: props.initialData?.name || '',
    description: props.initialData?.description || '',
    discount: props.initialData?.discount ? parseFloat(props.initialData.discount) : 0,
    discount_type: props.initialData?.discount_type || 'percentage',
    restaurant: props.initialData?.restaurant_details?.id || '',
    priority_index: props.initialData?.priority_index || 0,
    start_date: props.initialData?.start_date || '',
    end_date: props.initialData?.end_date || '',
    minimum_order: props.initialData?.minimum_order ? parseFloat(props.initialData.minimum_order) : 0,
    code: props.initialData?.code || null,
    usage_limit: props.initialData?.usage_limit || 0,
    promo_type: props.initialData?.promo_type || '',
    status: props.initialData?.status || '',
  },
})
  
// Handle form submission
const onSubmit = handleSubmit((values) => {
  const formData = new FormData();

  console.log(values)

  // Append basic fields
  formData.append('name', values.name);
  formData.append('description', values.description);
  formData.append('discount', values.discount);
  formData.append('discount_type', values.discount_type);
  formData.append('restaurant', values.restaurant);
  formData.append('priority_index', values.priority_index ?? '');
  formData.append('start_date', values.start_date ?? '');
  formData.append('end_date', values.end_date ?? '');
  formData.append('minimum_order', values.minimum_order ?? '');
  formData.append('code', values.code ?? '');
  formData.append('usage_limit', values.usage_limit ?? '');
  formData.append('promo_type', values.promo_type);
  formData.append('status', values.status);

  // Append time_offer field (if applicable)
  if (timeOffer.value) {
    formData.append('time_offer', JSON.stringify(timeOffer.value));
  }
  console.log("TIME OFFER", timeOffer.value)
  // Log the contents of FormData for debugging
//   console.log('FINAL FormData Contents:');
//   for (const [key, value] of formData.entries()) {
//     console.log(`${key}:`, value);
//   }

  emit('submit', formData);
});

  </script>
  