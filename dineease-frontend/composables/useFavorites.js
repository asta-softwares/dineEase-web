export function useFavoritesEndpoints() {
  const config = useRuntimeConfig();
  const baseUrl = config.public.apiBaseUrl;
  const authToken = useCookie('authToken');

  const headers = {
    Authorization: `Bearer ${authToken.value}`,
    'Content-Type': 'application/json',
  };

  const getFavorites = async () => {
    const { data, error } = await useFetch(`${baseUrl}favorites/`, {
      method: 'GET',
      headers,
    });
    if (error.value) throw error.value;
    return data.value;
  };

  const getFavoriteRestaurants = async () => {
    const { data, error } = await useFetch(`${baseUrl}favorites/restaurants/`, {
      method: 'GET',
      headers,
    });
    if (error.value) throw error.value;
    return data.value;
  };

  const getFavoriteMenus = async () => {
    const { data, error } = await useFetch(`${baseUrl}favorites/menus/`, {
      method: 'GET',
      headers,
    });
    if (error.value) throw error.value;
    return data.value;
  };

  const addFavorite = async (favoriteData) => {
    const { data, error } = await useFetch(`${baseUrl}favorites/`, {
      method: 'POST',
      headers,
      body: favoriteData, // { restaurant_id: 1 } or { menu_id: 5 }
    });
    if (error.value) throw error.value;
    return data.value;
  };

  const deleteFavoriteById = async (favoriteId) => {
    const url = `${baseUrl}favorites/${favoriteId}/remove/`;
    const { data, error } = await useFetch(url, {
      method: 'DELETE',
      headers,
    });
    if (error.value) throw error.value;
    return data.value;
  };

  const deleteFavoriteByReference = async ({ restaurantId, menuId }) => {
    let query = '';
    if (restaurantId) query = `restaurant_id=${restaurantId}`;
    if (menuId) query = `menu_id=${menuId}`;

    const url = `${baseUrl}favorites/remove/?${query}`;
    const { data, error } = await useFetch(url, {
      method: 'DELETE',
      headers,
    });
    if (error.value) throw error.value;
    return data.value;
  };

  return {
    getFavorites,
    getFavoriteRestaurants,
    getFavoriteMenus,
    addFavorite,
    deleteFavoriteById,
    deleteFavoriteByReference,
  };
}
