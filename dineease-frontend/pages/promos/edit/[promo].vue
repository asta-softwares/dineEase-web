<!-- pages/promos/edit/[id].vue -->
<template>
  <div>
    <div v-if="pending" class="loading-container">Loading...</div>
    <div v-else-if="error" class="error-container">Error loading promo: {{ error }}</div>
    <div v-else>
      <h2 class="text-2xl font-bold mb-4">{{ isEditMode ? 'Edit Promo' : 'Create Promo' }}</h2>
      <BreadcrumbNav :items="breadcrumbItems" />
      <PromoForm class="mt-4" :initial-data="promo" :is-edit-mode="isEditMode" @submit="savePromo" />
    </div>
  </div>
</template>

<script setup>
import { useApiEndpoints } from '@/composables/useApiRestaurants'
import PromoForm from '@/components/Forms/PromoForm'
import BreadcrumbNav from '@/components/BreadcrumbNav'
import { toast } from '@/components/ui/toast'

const { fetchPromoById, editPromo, createPromo } = useApiEndpoints()
const route = useRoute()
const router = useRouter()

const isEditMode = !!route.params.promo
const { data: promo, pending, error } = await useAsyncData(
  `promo-${route.params.promo}`,
  () => fetchPromoById(route.params.promo)
)

console.log(promo)
// Breadcrumb items
const breadcrumbItems = ref([
  { label: 'Dashboard', href: '/' },
  { label: promo.value?.restaurant_details.name || 'Name', href: `/restaurants/${promo.value?.restaurant_details.id}` },
  { label: 'Promos', href: '/promos' },
  { label: promo.value?.name || 'Name' },
  { label: isEditMode ? 'Edit Promo' : 'Create Promo' },
])

// Save promo (create or update)
const savePromo = async (formData) => {
  try {
    let action = 'created'
    let promoName = formData.get('name') || 'Promo'

    if (isEditMode) {
      await editPromo(route.params.promo, formData)
      action = 'updated'
    } else {
      await createPromo(formData)
    }

    router.push('/promos')

    toast({
      title: `Promo ${action.charAt(0).toUpperCase() + action.slice(1)} Successfully`,
      description: `The promo "${promoName}" has been ${action}.`,
      variant: 'success',
      position: 'center',
    })
  } catch (error) {
    console.error('Error saving promo:', error)

    toast({
      title: 'Error Saving Promo',
      description: 'An error occurred while saving the promo. Please try again.',
      variant: 'destructive',
      position: 'center',
    })
  }
}
</script>