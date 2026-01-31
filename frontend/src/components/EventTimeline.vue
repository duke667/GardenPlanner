<template>
  <div class="space-y-4">
    <div
      v-for="event in events"
      :key="event.id"
      class="flex gap-4"
    >
      <div class="flex flex-col items-center">
        <div class="event-icon" :class="getEventColor(event.event_type)">
          <component :is="getEventIcon(event.event_type)" class="w-4 h-4" />
        </div>
        <div class="w-0.5 flex-1 bg-gray-200 min-h-4"></div>
      </div>

      <div class="flex-1 pb-6">
        <div class="flex justify-between items-start mb-1">
          <h4 class="font-medium text-gray-900">{{ event.event_type_display }}</h4>
          <span class="text-sm text-gray-500">{{ formatDate(event.event_date) }}</span>
        </div>

        <div class="text-sm text-gray-600 space-y-1">
          <p v-if="event.location" class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            {{ event.location }}
          </p>

          <p v-if="event.quantity" class="flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
            </svg>
            {{ event.quantity }} {{ getQuantityUnit(event.event_type) }}
          </p>

          <p v-if="event.notes" class="mt-2 text-gray-700">{{ event.notes }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { h } from 'vue'

defineProps({
  events: {
    type: Array,
    default: () => []
  }
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const getEventColor = (type) => {
  const colors = {
    sowing: 'bg-blue-100 text-blue-600',
    germination: 'bg-green-100 text-green-600',
    transplanting: 'bg-purple-100 text-purple-600',
    watering: 'bg-cyan-100 text-cyan-600',
    fertilizing: 'bg-yellow-100 text-yellow-600',
    planting_out: 'bg-primary-100 text-primary-600',
    harvest: 'bg-orange-100 text-orange-600',
    pruning: 'bg-red-100 text-red-600',
    other: 'bg-gray-100 text-gray-600'
  }
  return colors[type] || 'bg-gray-100 text-gray-600'
}

const getEventIcon = (type) => {
  // Simple SVG icons as components
  const icons = {
    sowing: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' })
    ]),
    default: () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
      h('circle', { cx: '12', cy: '12', r: '3', 'stroke-width': '2' })
    ])
  }
  return icons[type] || icons.default
}

const getQuantityUnit = (type) => {
  if (type === 'watering') return 'Liter'
  if (type === 'harvest') return 'kg'
  return ''
}
</script>

<style scoped>
.event-icon {
  @apply w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0;
}
</style>
