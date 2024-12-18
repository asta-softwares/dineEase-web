<template>
  <div
    id="map"
    ref="mapContainer"
    class="w-full h-[500px]"
  ></div>
</template>

<script setup>
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { useApi } from '@/composables/useApi'

const props = defineProps({
  coordinates: {
    type: Array,
    default: null,
  },
  address: {
    type: String,
    default: null,
  },
  isEditMode: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['update:modelValue'])

const mapContainer = ref(null)
let map = null
let marker = null

const {
  public: { MAPBOX_API_KEY },
} = useRuntimeConfig()
const { get } = useApi()

onMounted(() => {
  initializeMap()
  if (props.coordinates) {
    initMarker(props.coordinates)
  } else if (props.address) {
    geocodeAddress(props.address)
  }

  if (props.isEditMode) {
    map.on('click', handleMapClick)
  }
})

const initializeMap = () => {
  mapboxgl.accessToken = MAPBOX_API_KEY
  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/streets-v11',
    center: props.coordinates.length ? props.coordinates : [-120.091998, 51.515618],
    zoom: props.coordinates.length ? 14 : 6,
  })

  // Add Zoom and Rotation Controls
  map.addControl(new mapboxgl.NavigationControl(), 'top-right')

  // Add Geolocate Control
  map.addControl(
    new mapboxgl.GeolocateControl({
      positionOptions: {
        enableHighAccuracy: true,
      },
      trackUserLocation: true,
    }),
    'top-right'
  )
}

const initMarker = (coordinates) => {
  const getMarker = props.coordinates.length ? props.coordinates : [-120.091998, 51.515618]
  if (marker) {
    marker.remove()
  }
  const el = document.createElement('div')
  el.className = 'marker'
  marker = new mapboxgl.Marker(el).setLngLat(getMarker).addTo(map)
  map.setCenter(getMarker)
}

const geocodeAddress = async (address) => {
  try {
    const response = await get(
      `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(
        address
      )}.json?access_token=${MAPBOX_API_KEY}&limit=1`
    )
    const coordinates = response.data.features[0].geometry.coordinates
    map.setCenter(coordinates)
    initMarker(coordinates)
  } catch (error) {
    console.error('Error geocoding address:', error)
  }
}

const handleMapClick = (event) => {
  const coordinates = event.lngLat.toArray()
  initMarker(coordinates)
  emit('update:modelValue', coordinates)
}
</script>

<style>
.marker {
  background-color: #007bff;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  border: 2px solid #fff;
  position: relative;
  z-index: 1;
}

/* Pulsing Effect */
.marker::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 123, 255, 0.4);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  z-index: -1;
  animation: pulse 1.5s infinite ease-out;
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(1);
    opacity: 0.8;
  }
  100% {
    transform: translate(-50%, -50%) scale(2);
    opacity: 0;
  }
}
</style>
