export function useApiEndpoints() {
  const config = useRuntimeConfig()
  const baseUrl = config.public.apiBaseUrl
  const authToken = useCookie('authToken')

  const headers = {
    Authorization: `Bearer ${authToken.value}`,
  }

  // --- Restaurant Endpoints ---
  const createRestaurant = async (restaurantData) => {
    const { data, error } = await useFetch(`${baseUrl}restaurants/`, {
      method: 'POST',
      headers,
      body: restaurantData,
    })
    if (error.value) throw error.value
    return data.value
  }

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

  const createStripeOnboardingLink = async (restaurantId) => {
    try {
      const { data, error } = await useFetch(`${baseUrl}create-onboarding-link/${restaurantId}/`, {
        method: 'GET',
      });
  
      if (error.value) {
        console.error('Error creating Stripe onboarding link:', error.value);
        return { success: false, error: error.value };
      }
  
      return { success: true, onboardingUrl: data.value.onboarding_url };
    } catch (err) {
      console.error('Unexpected error:', err);
      return { success: false, error: err.message };
    }
  };

  const createCustomerPortalSession = async () => {
    try {
      const { data, error } = await useFetch(`${baseUrl}create-customer-portal-session/`, {
        method: 'POST',
        headers
      });
  
      if (error.value) {
        console.error('Error creating customer portal session:', error.value);
        return { success: false, error: error.value };
      }
  
      window.location.href = data.value.url;
      return { success: true };
    } catch (err) {
      console.error('Unexpected error:', err);
      return { success: false, error: err.message };
    }
  };

  const createDashboardLink = async (restaurantId) => {
    try {
      const response = await fetch(`${baseUrl}create-dashboard-link/${restaurantId}/`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
  
      const result = await response.json();
      console.log("API Response:", result);
  
      if (!response.ok) {
        if (result.onboarding_url) {
          return { success: false, onboardingUrl: result.onboarding_url };
        }
        throw new Error(result.error || 'Failed to create dashboard link.');
      }
  
      return { success: true, dashboardUrl: result.dashboard_url };
    } catch (err) {
      console.error('Error creating dashboard link:', err);
      return { success: false, error: err.message };
    }
  };

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

  const fetchPromosByRestaurant = async (restaurantId, promoType = null) => {
    const url = promoType
      ? `${baseUrl}promos/restaurant/${restaurantId}/?promo_type=${promoType}`
      : `${baseUrl}promos/restaurant/${restaurantId}/`
  
    const { data, error } = await useFetch(url, {
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

    console.log("HJEADER", headers)
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
    createRestaurant,
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
    fetchPromosByRestaurant,
    createStripeOnboardingLink,
    createCustomerPortalSession,
    createDashboardLink,
  }
}
