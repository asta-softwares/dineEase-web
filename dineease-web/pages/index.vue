<template>
  <div class="container">
  
    <!-- Restaurant Details -->
    <div v-if="restaurant" class="restaurant-details">
      <h1>{{ restaurant.name }}</h1>
      <img :src="restaurant.image" alt="Restaurant Image" />
      <p>{{ restaurant.description }}</p>
    </div>

    <!-- List of Promos -->
    <div v-if="promos.length">
      <h3>Promos</h3>
      <div v-for="promo in promos" :key="promo.id" class="promo-card">
        <div :title="promo.name">
          <img v-if="promo.image" :src="promo.image" :alt="promo.name" />
          <h2>{{ promo.name }}</h2>
          <p>{{ promo.description }}</p>
          <Button label="Edit Promo" icon="pi pi-pencil" @click="editPromo(promo)" />
        </div>
      </div>
    </div>

    <!-- List of Menu Items -->
    <div v-if="menu.length">
      <h3>Menu</h3>
      <div v-for="menuItem in menu" :key="menuItem.id" class="menu-card">
        <div :title="menuItem.name">
          <!-- Display first image from the menu images array -->
          <img v-if="menuItem.images.length" :src="menuItem.images[0].image" :alt="menuItem.name" />
          <h2>{{ menuItem.name }}</h2>
          <p>{{ menuItem.description }}</p>
          <p><strong>Price:</strong> ${{ menuItem.cost }}</p>
          <Button label="Edit Menu Item" icon="pi pi-pencil" @click="editMenuItem(menuItem)" />
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <Dialog v-if="selectedItem" header="Edit Item" v-model:visible="showEditModal">
      <InputText v-model="selectedItem.name" placeholder="Name" />
      <InputText v-model="selectedItem.description" placeholder="Description" />
      <Button label="Save" icon="pi pi-save" @click="saveEdit" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Dialog from 'primevue/dialog';

const restaurant = ref(null);
const promos = ref([]);
const menu = ref([]);
const showEditModal = ref(false);
const selectedItem = ref(null);

// Fetch restaurant details from Django API
async function fetchRestaurantData() {
  try {
    const response = await fetch('http://localhost:8000/api/restaurants/1/');
    if (response.ok) {
      restaurant.value = await response.json();
      promos.value = restaurant.value.promos || [];
      menu.value = restaurant.value.menus || [];
    } else {
      console.error('Failed to fetch restaurant data:', response.status);
    }
  } catch (error) {
    console.error('Error fetching restaurant data:', error);
  }
}

// Edit Promo or Menu Item
function editPromo(promo) {
  selectedItem.value = { ...promo };
  showEditModal.value = true;
}

function editMenuItem(menuItem) {
  selectedItem.value = { ...menuItem };
  showEditModal.value = true;
}

// Save edited changes
async function saveEdit() {
  try {
    const url = selectedItem.value.restaurant ? 
      `http://localhost:8000/api/promos/${selectedItem.value.id}/` : 
      `http://localhost:8000/api/menus/${selectedItem.value.id}/`;

    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(selectedItem.value)
    });

    if (response.ok) {
      // Update local data after saving
      if (selectedItem.value.restaurant) {
        const index = promos.value.findIndex(promo => promo.id === selectedItem.value.id);
        promos.value[index] = { ...selectedItem.value };
      } else {
        const index = menu.value.findIndex(item => item.id === selectedItem.value.id);
        menu.value[index] = { ...selectedItem.value };
      }
      showEditModal.value = false;
      selectedItem.value = null;
    } else {
      console.error('Failed to save changes:', response.status);
    }
  } catch (error) {
    console.error('Error saving changes:', error);
  }
}

onMounted(() => {
  fetchRestaurantData();
});
</script>

<style scoped>
.container {
  padding: 20px;
}
.restaurant-details img {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
}
.promo-card, .menu-card {
  margin-bottom: 20px;
}
</style>
