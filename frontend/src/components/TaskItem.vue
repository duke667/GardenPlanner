<template>
  <div class="card flex items-start gap-3 hover:shadow-md transition-shadow">
    <!-- Checkbox -->
    <input
      type="checkbox"
      :checked="task.completed"
      @change="$emit('toggle', task.id)"
      class="mt-1 w-5 h-5 text-primary-600 rounded focus:ring-primary-500 cursor-pointer"
    />

    <!-- Content -->
    <div class="flex-1 min-w-0">
      <div class="flex items-start justify-between gap-2">
        <h3
          class="font-medium"
          :class="task.completed ? 'text-gray-400 line-through' : 'text-gray-900'"
        >
          {{ task.title }}
        </h3>
        <span
          class="priority-badge flex-shrink-0"
          :class="getPriorityColor(task.priority)"
        >
          {{ task.priority_display }}
        </span>
      </div>

      <p
        v-if="task.description"
        class="text-sm mt-1"
        :class="task.completed ? 'text-gray-400' : 'text-gray-600'"
      >
        {{ task.description }}
      </p>

      <div class="flex items-center gap-4 mt-2 text-sm text-gray-500">
        <span v-if="task.due_date" class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
          {{ formatDate(task.due_date) }}
          <span v-if="isOverdue(task)" class="text-red-600 font-medium">
            (überfällig)
          </span>
        </span>

        <span v-if="task.planting_cycle" class="flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
          Pflanze zugeordnet
        </span>
      </div>
    </div>

    <!-- Actions -->
    <button
      @click="$emit('delete', task.id)"
      class="text-gray-400 hover:text-red-600 transition-colors"
    >
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
      </svg>
    </button>
  </div>
</template>

<script setup>
defineProps({
  task: {
    type: Object,
    required: true
  }
})

defineEmits(['toggle', 'delete'])

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const isOverdue = (task) => {
  if (!task.due_date || task.completed) return false
  const today = new Date()
  const dueDate = new Date(task.due_date)
  return dueDate < today
}

const getPriorityColor = (priority) => {
  const colors = {
    low: 'bg-gray-100 text-gray-600',
    medium: 'bg-yellow-100 text-yellow-700',
    high: 'bg-red-100 text-red-700'
  }
  return colors[priority] || 'bg-gray-100 text-gray-600'
}
</script>

<style scoped>
.priority-badge {
  @apply px-2 py-1 rounded text-xs font-medium;
}
</style>
