<template>
    <div>
      <h2 class="text-2xl font-bold mb-4">Create Menu</h2>
      <BreadcrumbNav :items="breadcrumbItems" />
      <MenuForm class="mt-4" @submit="saveMenu" />
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants'
  import MenuForm from '@/components/Forms/MenuForm.vue'
  import BreadcrumbNav from '@/components/BreadcrumbNav.vue'
  import { toast } from '@/components/ui/toast'
  
  const { createMenu } = useApiEndpoints()
  const router = useRouter()
  
  // Breadcrumb items for creating a new menu
  const breadcrumbItems = ref([
    { label: 'Dashboard', href: '/' },
    { label: 'Menu List', href: '/menus/' },
    { label: 'Create Menu', href: '/menus/create' },
  ])
  
  // Function to handle creating a new menu
  // Save menu (create or update)
  const saveMenu = async (formData) => {
  try {
    // Create the menu via API
    const response = await createMenu(formData)

    // Extract the menu name and restaurant name from the response
    const menuName = response.name || 'New Menu'
    const restaurantName = response.restaurant_details?.name || 'Unknown Restaurant'

    // Display the toast notification
    toast({
      title: 'Menu Created Successfully',
      description: `The menu "${menuName}" has been created for the restaurant "${restaurantName}".`,
      variant: 'success',
      position: 'center',
    })

    // Redirect after successful creation
    // router.push('/menus')
  } catch (error) {
    console.error('Error saving menu:', error)

    // Display an error toast notification
    toast({
      title: 'Menu Creation Failed',
      description: 'There was an error creating the menu. Please try again.',
      variant: 'destructive',
      position: 'center',
    })
  }
}

  </script>
  