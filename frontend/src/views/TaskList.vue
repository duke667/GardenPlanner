<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Aufgaben</h1>
      <button @click="showAddModal = true" class="btn btn-primary">
        + Neue Aufgabe
      </button>
    </div>

    <!-- Filter -->
    <div class="card mb-6">
      <div class="flex flex-wrap gap-2">
        <button
          @click="filter = 'all'"
          class="filter-btn"
          :class="filter === 'all' ? 'filter-active' : 'filter-inactive'"
        >
          Alle ({{ stats.total }})
        </button>
        <button
          @click="filter = 'open'"
          class="filter-btn"
          :class="filter === 'open' ? 'filter-active' : 'filter-inactive'"
        >
          Offen ({{ stats.open }})
        </button>
        <button
          @click="filter = 'overdue'"
          class="filter-btn"
          :class="filter === 'overdue' ? 'filter-active' : 'filter-inactive'"
        >
          Überfällig ({{ stats.overdue }})
        </button>
        <button
          @click="filter = 'completed'"
          class="filter-btn"
          :class="filter === 'completed' ? 'filter-active' : 'filter-inactive'"
        >
          Erledigt ({{ stats.completed }})
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Lade Aufgaben...</p>
    </div>

    <!-- Tasks List -->
    <div v-else-if="filteredTasks.length > 0" class="space-y-2">
      <TaskItem
        v-for="task in filteredTasks"
        :key="task.id"
        :task="task"
        @toggle="toggleTask"
        @delete="deleteTask"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="card text-center py-12">
      <p class="text-gray-500 mb-4">
        {{ getEmptyMessage() }}
      </p>
      <button v-if="filter === 'all'" @click="showAddModal = true" class="btn btn-primary">
        Erste Aufgabe anlegen
      </button>
    </div>

    <!-- Add Task Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-900">Neue Aufgabe</h2>
          <button @click="showAddModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="addTask">
          <div class="space-y-4">
            <div>
              <label class="label">Titel *</label>
              <input
                v-model="newTask.title"
                type="text"
                required
                class="input"
                placeholder="z.B. Tomaten gießen"
              />
            </div>

            <div>
              <label class="label">Beschreibung</label>
              <textarea
                v-model="newTask.description"
                class="input"
                rows="3"
                placeholder="Zusätzliche Informationen..."
              />
            </div>

            <div>
              <label class="label">Fälligkeitsdatum</label>
              <input v-model="newTask.due_date" type="date" class="input" />
            </div>

            <div>
              <label class="label">Priorität</label>
              <select v-model="newTask.priority" class="input">
                <option value="low">Niedrig</option>
                <option value="medium">Mittel</option>
                <option value="high">Hoch</option>
              </select>
            </div>

            <div>
              <label class="label">Pflanze (optional)</label>
              <select v-model="newTask.planting_cycle" class="input">
                <option value="">Keine Zuordnung</option>
                <option
                  v-for="cycle in activeCycles"
                  :key="cycle.id"
                  :value="cycle.id"
                >
                  {{ cycle.plant_name }}
                  <template v-if="cycle.plant_variety">({{ cycle.plant_variety }})</template>
                  - {{ cycle.year }}
                </option>
              </select>
            </div>
          </div>

          <div class="flex gap-2 mt-6">
            <button type="submit" class="btn btn-primary flex-1" :disabled="saving">
              {{ saving ? 'Speichern...' : 'Aufgabe anlegen' }}
            </button>
            <button type="button" @click="showAddModal = false" class="btn btn-secondary">
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { taskAPI, cycleAPI } from '../services/api'
import TaskItem from '../components/TaskItem.vue'

const tasks = ref([])
const activeCycles = ref([])
const loading = ref(true)
const filter = ref('open')
const showAddModal = ref(false)
const saving = ref(false)

const newTask = ref({
  title: '',
  description: '',
  due_date: '',
  priority: 'medium',
  planting_cycle: ''
})

const stats = computed(() => {
  return {
    total: tasks.value.length,
    open: tasks.value.filter(t => !t.completed).length,
    overdue: tasks.value.filter(t => !t.completed && isOverdue(t)).length,
    completed: tasks.value.filter(t => t.completed).length
  }
})

const filteredTasks = computed(() => {
  if (filter.value === 'all') return tasks.value
  if (filter.value === 'open') return tasks.value.filter(t => !t.completed)
  if (filter.value === 'overdue') return tasks.value.filter(t => !t.completed && isOverdue(t))
  if (filter.value === 'completed') return tasks.value.filter(t => t.completed)
  return tasks.value
})

const isOverdue = (task) => {
  if (!task.due_date || task.completed) return false
  const today = new Date()
  const dueDate = new Date(task.due_date)
  return dueDate < today
}

const getEmptyMessage = () => {
  if (filter.value === 'open') return 'Keine offenen Aufgaben'
  if (filter.value === 'overdue') return 'Keine überfälligen Aufgaben'
  if (filter.value === 'completed') return 'Keine erledigten Aufgaben'
  return 'Noch keine Aufgaben angelegt'
}

const loadTasks = async () => {
  try {
    loading.value = true
    const response = await taskAPI.getAll()
    tasks.value = response.data.results || response.data
  } catch (err) {
    console.error('Load tasks error:', err)
  } finally {
    loading.value = false
  }
}

const loadActiveCycles = async () => {
  try {
    const currentYear = new Date().getFullYear()
    const response = await cycleAPI.getAll({ year: currentYear })
    activeCycles.value = response.data.results || response.data
  } catch (err) {
    console.error('Load cycles error:', err)
  }
}

const addTask = async () => {
  try {
    saving.value = true
    const taskData = { ...newTask.value }
    if (!taskData.planting_cycle) delete taskData.planting_cycle
    if (!taskData.due_date) delete taskData.due_date

    await taskAPI.create(taskData)
    showAddModal.value = false
    newTask.value = {
      title: '',
      description: '',
      due_date: '',
      priority: 'medium',
      planting_cycle: ''
    }
    await loadTasks()
  } catch (err) {
    console.error('Add task error:', err)
    alert('Fehler beim Anlegen der Aufgabe')
  } finally {
    saving.value = false
  }
}

const toggleTask = async (taskId) => {
  try {
    await taskAPI.toggleComplete(taskId)
    await loadTasks()
  } catch (err) {
    console.error('Toggle task error:', err)
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('Aufgabe wirklich löschen?')) return
  try {
    await taskAPI.delete(taskId)
    await loadTasks()
  } catch (err) {
    console.error('Delete task error:', err)
  }
}

onMounted(() => {
  loadTasks()
  loadActiveCycles()
})
</script>

<style scoped>
.filter-btn {
  @apply px-4 py-2 rounded-lg font-medium text-sm transition-colors;
}

.filter-active {
  @apply bg-primary-600 text-white;
}

.filter-inactive {
  @apply bg-gray-100 text-gray-700 hover:bg-gray-200;
}

.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto;
}
</style>
