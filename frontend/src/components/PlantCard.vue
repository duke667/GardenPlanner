<template>
  <div class="card hover:shadow-md transition-shadow cursor-pointer" @click="$emit('click')">
    <div class="flex justify-between items-start mb-2">
      <div class="flex-1">
        <h3 class="text-lg font-semibold text-gray-900">
          {{ plant.name }}
          <span v-if="plant.variety" class="text-sm text-gray-500 font-normal">
            ({{ plant.variety }})
          </span>
        </h3>
        <p v-if="plant.seed_source" class="text-sm text-gray-600 mt-1">
          Samen: {{ plant.seed_source }}
        </p>
      </div>
      <span
        v-if="plant.latest_cycle_status"
        class="status-badge"
        :class="getStatusColor(plant.latest_cycle_status)"
      >
        {{ plant.latest_cycle_status }}
      </span>
    </div>

    <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
      <div class="text-sm text-gray-500">
        <span class="font-medium">{{ plant.cycle_count }}</span>
        {{ plant.cycle_count === 1 ? 'Zyklus' : 'Zyklen' }}
      </div>
      <div v-if="plant.latest_cycle_year" class="text-sm text-gray-500">
        {{ plant.latest_cycle_year }}
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  plant: {
    type: Object,
    required: true
  }
})

defineEmits(['click'])

const getStatusColor = (status) => {
  const colors = {
    'Planung': 'bg-gray-100 text-gray-700',
    'Säen': 'bg-blue-100 text-blue-700',
    'Keimung': 'bg-green-100 text-green-700',
    'Wachstum': 'bg-green-100 text-green-700',
    'Ausgepflanzt': 'bg-primary-100 text-primary-700',
    'Ernte': 'bg-orange-100 text-orange-700',
    'Abgeschlossen': 'bg-gray-100 text-gray-600'
  }
  return colors[status] || 'bg-gray-100 text-gray-700'
}
</script>

<style scoped>
.status-badge {
  @apply px-2 py-1 rounded text-xs font-medium;
}
</style>
