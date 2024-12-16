<!-- pages/menus/edit/[id].vue -->
<template>
    <div>
      <div v-if="pending" class="loading-container">Loading...</div>
      <div v-else-if="error" class="error-container">Error loading menu: {{ error }}</div>
      <div v-else>
        <h2 class="text-2xl font-bold mb-4">{{ isEditMode ? 'Edit Menu' : 'Create Menu' }}</h2>
        <BreadcrumbNav :items="breadcrumbItems" />
        <MenuForm class="mt-4" :initial-data="menu" :is-edit-mode="true" @submit="saveMenu" />
      </div>
    </div>
  </template>
  
  <script setup>
  import { useApiEndpoints } from '@/composables/useApiRestaurants'
  import MenuForm from '@/components/Forms/MenuForm.vue'
  import BreadcrumbNav from '@/components/BreadcrumbNav.vue'
  import { useCategories } from '~/composables/useCategory'
  import { toast } from '@/components/ui/toast'
  
  // Fetch menu data
  const { fetchMenuById, editMenu, createMenu } = useApiEndpoints()
  const route = useRoute()
  const router = useRouter()
  
  const isEditMode = !!route.params.menu
  const { data: menu, pending, error } = await useAsyncData(
    `menu-${route.params.menu}`,
    () => fetchMenuById(route.params.menu)
  )

  console.log("MENU: ", menu)
  
  // Breadcrumb items
  const breadcrumbItems = ref([
    { label: 'Dashboard', href: '/' },
    { label: 'Loading...', href: '#' },
    { label: 'Edit Menu Details'},
  ])

  watchEffect(() => {
  if (menu.value) {
    breadcrumbItems.value = [
      { label: 'Dashboard', href: '/' },
      { label: menu.value?.restaurant_details.name || 'Name', href: `/restaurants/${menu.value?.restaurant_details.id}` },
      { label: menu.value?.name || 'Name', href: `/menus/` },
      { label: 'Edit Restaurant Details' },
    ]
  }
})
  
  const saveMenu = async (formData) => {
  try {
    let action = 'created'
    let menuName = formData.get('name') || 'Menu'

    if (isEditMode) {
      await editMenu(route.params.menu, formData)
      action = 'updated'
    } else {
      await createMenu(formData)
    }

    // Redirect to the menus page
    router.push('/menus')

    // Show success toast notification
    toast({
      title: `Menu ${action.charAt(0).toUpperCase() + action.slice(1)} Successfully`,
      description: `The menu "${menuName}" has been ${action}.`,
      variant: 'success',
      position: 'center',
    })
  } catch (error) {
    console.error('Error saving menu:', error)

    // Show error toast notification
    toast({
      title: 'Error Saving Menu',
      description: 'An error occurred while saving the menu. Please try again.',
      variant: 'destructive',
      position: 'center',
    })
  }
}

  </script>
  