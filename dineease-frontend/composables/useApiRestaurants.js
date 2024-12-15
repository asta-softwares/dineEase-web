export function useApiEndpoints() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl
  const authToken = useCookie('authToken')

  const headers = {
    Authorization: `Bearer ${authToken.value}`,
  }

  // --- Restaurant Endpoints ---
  const fetchRestaurants = async () => {
    const { data, error } = await useFetch(`${baseUrl}restaurants/`, {
      method: 'GET',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchRestaurantsMini = async () => {
    const { data, error } = await useFetch(`${baseUrl}restaurants-mini/`, {
      method: 'GET',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchRestaurantById = async (id) => {
    const { data, error } = await useFetch(`${baseUrl}restaurants/${id}/`, {
      method: 'GET',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  const editRestaurant = async (id, updateData) => {
    const { data, error } = await useFetch(`${baseUrl}restaurants/${id}/`, {
      method: 'PATCH',
      headers,
      body: updateData,
    })
    if (error.value) throw error.value
    return data.value
  }

  const deleteRestaurant = async (id) => {
    const { data, error } = await useFetch(`${baseUrl}restaurants/${id}/`, {
      method: 'DELETE',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  // --- Promo Endpoints ---
  const fetchPromos = async () => {
    const { data, error } = await useFetch(`${baseUrl}promos/`, {
      method: 'GET',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchPromoById = async (id) => {
    const { data, error } = await useFetch(`${baseUrl}promos/${id}/`, {
      method: 'GET',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  const createPromo = async (promoData) => {
    const { data, error } = await useFetch(`${baseUrl}promos/`, {
      method: 'POST',
      headers,
      body: promoData,
    })
    if (error.value) throw error.value
    return data.value
  }

  const editPromo = async (id, updateData) => {
    const { data, error } = await useFetch(`${baseUrl}promos/${id}/`, {
      method: 'PATCH',
      headers,
      body: updateData,
    })
    if (error.value) throw error.value
    return data.value
  }

  const deletePromo = async (id) => {
    const { data, error } = await useFetch(`${baseUrl}promos/${id}/`, {
      method: 'DELETE',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  // --- Menu Endpoints ---
  const fetchMenus = async () => {
    const { data, error } = await useFetch(`${baseUrl}menus/`, {
      method: 'GET',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  const fetchMenuById = async (id) => {
    const { data, error } = await useFetch(`${baseUrl}menus/${id}/`, {
      method: 'GET',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }

  const createMenu = async (menuData) => {
    const { data, error } = await useFetch(`${baseUrl}menus/`, {
      method: 'POST',
      headers,
      body: menuData,
    })
    if (error.value) throw error.value
    return data.value
  }

  const editMenu = async (id, updateData) => {
    const { data, error } = await useFetch(`${baseUrl}menus/${id}/`, {
      method: 'PATCH',
      headers,
      body: updateData,
    })
    if (error.value) throw error.value
    return data.value
  }

  const deleteMenu = async (id) => {
    const { data, error } = await useFetch(`${baseUrl}menus/${id}/`, {
      method: 'DELETE',
      headers,
    })
    if (error.value) throw error.value
    return data.value
  }
  
  return {
    fetchRestaurants,
    fetchRestaurantById,
    editRestaurant,
    deleteRestaurant,
    fetchPromos,
    fetchPromoById,
    createPromo,
    editPromo,
    deletePromo,
    fetchMenus,
    fetchMenuById,
    createMenu,
    editMenu,
    deleteMenu,
    fetchRestaurantsMini,
  }
}
