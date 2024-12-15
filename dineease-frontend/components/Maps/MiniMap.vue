<template>
  <div
    id="map"
    ref="mapContainer"
    class="w-full"
    :class="{ rounded: rounded }"
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
  })
  
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
      console.log(props.coordinates)
      initMarker(props.coordinates)
    } else if (props.address) {
      geocodeAddress(props.address)
    }
  })
  
  const initializeMap = () => {
    mapboxgl.accessToken = MAPBOX_API_KEY
    map = new mapboxgl.Map({
      container: mapContainer.value,
      style: 'mapbox://styles/mapbox/streets-v11',
      center: props.coordinates ? [props.coordinates[0], props.coordinates[1]] : [0, 0],
      zoom: 16,
    })
  }
  
  const initMarker = (coordinates) => {
    const el = document.createElement('div')
    el.className = 'marker'
    marker = new mapboxgl.Marker(el).setLngLat(coordinates).addTo(map)
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
  </script>
  
  <style>
  .marker {
    background-color: #007bff;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    border: 2px solid #fff;
    z-index: 1;
  }
  </style>
  