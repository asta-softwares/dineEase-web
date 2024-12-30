<template>
    <div>
      <h2 class="text-2xl font-bold mb-4">Create Promo</h2>
      <PromoForm class="mt-4" @submit="savePromo" />
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants'
  import PromoForm from '@/components/Forms/PromoForm.vue'
  import { toast } from '@/components/ui/toast'
  import { useBreadcrumb } from '@/composables/useBreadcrumb';
const { setBreadcrumbs } = useBreadcrumb();
  
  // Initialize API endpoints and router
  const { createPromo } = useApiEndpoints()
  const router = useRouter()
  
  
  setBreadcrumbs([
    { label: 'Dashboard', path: '/' },
    { label: 'Promos', path: '/promos/' },
    { label: 'Create Promo', path: '/promos/create' },
  ])
  
  const savePromo = async (formData) => {
    try {
      const response = await createPromo(formData)
  
      const promoName = response.name || 'New Promo'
      const restaurantName = response.restaurant_details?.name || 'Unknown Restaurant'
  
      toast({
        title: 'Promo Created Successfully',
        description: `The promo "${promoName}" has been created for the restaurant "${restaurantName}".`,
        variant: 'success',
        position: 'center',
      })
  
      router.push('/promos')
    } catch (error) {
      console.error('Error creating promo:', error)
  
      toast({
        title: 'Promo Creation Failed',
        description: 'There was an error creating the promo. Please try again.',
        variant: 'destructive',
        position: 'center',
      })
    }
  }
  </script>
  