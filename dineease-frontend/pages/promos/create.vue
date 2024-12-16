<template>
    <div>
      <h2 class="text-2xl font-bold mb-4">Create Promo</h2>
      <BreadcrumbNav :items="breadcrumbItems" />
      <PromoForm class="mt-4" @submit="savePromo" />
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants'
  import PromoForm from '@/components/Forms/PromoForm.vue'
  import BreadcrumbNav from '@/components/BreadcrumbNav.vue'
  import { toast } from '@/components/ui/toast'
  import { useRouter } from 'vue-router'
  
  // Initialize API endpoints and router
  const { createPromo } = useApiEndpoints()
  const router = useRouter()
  
  // Breadcrumb items for creating a new promo
  const breadcrumbItems = ref([
    { label: 'Dashboard', href: '/' },
    { label: 'Promo List', href: '/promos/' },
    { label: 'Create Promo', href: '/promos/create' },
  ])
  
  // Function to handle creating a new promo
  const savePromo = async (formData) => {
    try {
      // Create the promo via API
      const response = await createPromo(formData)
  
      // Extract the promo name and restaurant name from the response
      const promoName = response.name || 'New Promo'
      const restaurantName = response.restaurant_details?.name || 'Unknown Restaurant'
  
      // Display the toast notification
      toast({
        title: 'Promo Created Successfully',
        description: `The promo "${promoName}" has been created for the restaurant "${restaurantName}".`,
        variant: 'success',
        position: 'center',
      })
  
      // Redirect to the promo list page
      router.push('/promos')
    } catch (error) {
      console.error('Error creating promo:', error)
  
      // Display an error toast notification
      toast({
        title: 'Promo Creation Failed',
        description: 'There was an error creating the promo. Please try again.',
        variant: 'destructive',
        position: 'center',
      })
    }
  }
  </script>
  