<template>
  <div class="card">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <p class="text-sm text-gray-600">{{ label }}</p>
        <p class="text-2xl font-bold text-gray-900 mt-1">{{ value }}</p>
        <p v-if="subtitle" class="text-xs text-gray-500 mt-1">{{ subtitle }}</p>
      </div>
      <div
        v-if="icon"
        class="w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0"
        :class="iconColor"
      >
        <component :is="icon" class="w-6 h-6" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: null
  },
  iconColor: {
    type: String,
    default: 'bg-primary-100 text-primary-600'
  }
})
</script>
