<script setup>
import { Input } from '@/components/ui/input'
import { Search } from 'lucide-vue-next';

const authToken = useCookie('authToken')

function debounce(func, delay) {
  let timeout = null
  return (...args) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), delay)
  }
}

const searchQuery = ref('')
const suggestions = ref([])
const isLoading = ref(false)
const router = useRouter()

const fetchSuggestions = async () => {
  if (!searchQuery.value.trim()) {
    suggestions.value = []
    return
  }

  isLoading.value = true
  try {
    const { data } = await useFetch(`/api/search?query=${searchQuery.value}`, {
      headers: {
        Authorization: `Bearer ${authToken.value}`,
      },
    })

    suggestions.value = data.value || []
  } catch (error) {
    console.error('Error fetching suggestions:', error)
  } finally {
    isLoading.value = false
  }
}

const debouncedFetchSuggestions = debounce(fetchSuggestions, 500)

watch(searchQuery, debouncedFetchSuggestions)

const handleSuggestionClick = (suggestion) => {
  searchQuery.value = ''
  router.push(`/${suggestion.type}s/${suggestion.id}`)
}
</script>

<template>
  <div class="relative">
     <div class="relative">
      <Search class="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
      <Input
        v-model="searchQuery"
        type="search"
        placeholder="Search..."
        class="w-full rounded-lg bg-background pl-8 md:w-[200px] lg:w-[336px]"
      />
     </div>
    
    <div
      v-if="suggestions.length > 0 && searchQuery"
      class="absolute bg-white border border-gray-300 rounded-md shadow-lg mt-1 z-10 w-full max-h-60 overflow-auto text-sm"
    >
      <ul>
        <li
          v-for="suggestion in suggestions"
          :key="`${suggestion.type}-${suggestion.id}`"
          @click="handleSuggestionClick(suggestion)"
          class="p-2 hover:bg-gray-100 cursor-pointer capitalize"
        >
          {{ suggestion.name }} - {{ suggestion.type }}
        </li>
      </ul>
    </div>

    <!-- Loading Indicator -->
    <div
      v-if="isLoading && searchQuery"
      class="absolute bg-white border border-gray-300 rounded-md shadow-lg mt-1 z-10 w-full p-2 text-gray-500"
    >
      Loading suggestions...
    </div>
  </div>
</template>
