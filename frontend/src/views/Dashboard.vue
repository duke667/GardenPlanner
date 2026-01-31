<template>
  <div>
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
      <p class="text-gray-600 mt-1">Übersicht {{ currentYear }}</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Lade Dashboard...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card bg-red-50 border-red-200">
      <p class="text-red-600">{{ error }}</p>
    </div>

    <!-- Dashboard Content -->
    <div v-else>
      <!-- Stats Grid -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <StatsWidget
          label="Pflanzen"
          :value="stats.total_plants || 0"
          :icon="PlantIcon"
          icon-color="bg-green-100 text-green-600"
        />
        <StatsWidget
          label="Aktive Zyklen"
          :value="stats.current_cycles || 0"
          :icon="CycleIcon"
          icon-color="bg-blue-100 text-blue-600"
        />
        <StatsWidget
          label="Offene Aufgaben"
          :value="stats.open_tasks || 0"
          :icon="TaskIcon"
          icon-color="bg-yellow-100 text-yellow-600"
        />
        <StatsWidget
          label="Überfällig"
          :value="stats.overdue_tasks || 0"
          :icon="AlertIcon"
          icon-color="bg-red-100 text-red-600"
        />
      </div>

      <!-- Recent Harvests -->
      <div v-if="dashboardData.recent_harvests" class="card mb-6 bg-gradient-to-r from-orange-50 to-yellow-50">
        <h2 class="text-lg font-semibold text-gray-900 mb-2">Ernten (letzte 30 Tage)</h2>
        <div class="flex items-baseline gap-4">
          <div>
            <span class="text-3xl font-bold text-orange-600">
              {{ dashboardData.recent_harvests.count }}
            </span>
            <span class="text-gray-600 ml-2">Ernten</span>
          </div>
          <div v-if="dashboardData.recent_harvests.total_quantity > 0">
            <span class="text-3xl font-bold text-orange-600">
              {{ dashboardData.recent_harvests.total_quantity.toFixed(1) }}
            </span>
            <span class="text-gray-600 ml-2">kg gesamt</span>
          </div>
        </div>
      </div>

      <!-- Two Column Layout -->
      <div class="grid md:grid-cols-2 gap-6">
        <!-- Current Cycles -->
        <div>
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Aktuelle Anbau-Zyklen</h2>
          <div v-if="cycles.length === 0" class="card text-center py-8 text-gray-500">
            Keine aktiven Zyklen
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="cycle in cycles"
              :key="cycle.id"
              class="card hover:shadow-md transition-shadow cursor-pointer"
              @click="goToPlant(cycle.plant)"
            >
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="font-semibold text-gray-900">
                    {{ cycle.plant_name }}
                    <span v-if="cycle.plant_variety" class="text-gray-500 text-sm font-normal">
                      ({{ cycle.plant_variety }})
                    </span>
                  </h3>
                  <p class="text-sm text-gray-600 mt-1">
                    {{ cycle.event_count }} Ereignisse &middot; {{ cycle.task_count }} Aufgaben
                  </p>
                </div>
                <span
                  class="px-2 py-1 rounded text-xs font-medium"
                  :class="getStatusColor(cycle.status_display)"
                >
                  {{ cycle.status_display }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Tasks -->
        <div>
          <h2 class="text-xl font-semibold text-gray-900 mb-4">Aufgaben</h2>

          <!-- Overdue Tasks -->
          <div v-if="overdueTasks.length > 0" class="mb-4">
            <h3 class="text-sm font-medium text-red-600 mb-2">Überfällig</h3>
            <div class="space-y-2">
              <TaskItem
                v-for="task in overdueTasks"
                :key="task.id"
                :task="task"
                @toggle="toggleTask"
                @delete="deleteTask"
              />
            </div>
          </div>

          <!-- Upcoming Tasks -->
          <div v-if="upcomingTasks.length > 0">
            <h3 class="text-sm font-medium text-gray-700 mb-2">Nächste 7 Tage</h3>
            <div class="space-y-2">
              <TaskItem
                v-for="task in upcomingTasks"
                :key="task.id"
                :task="task"
                @toggle="toggleTask"
                @delete="deleteTask"
              />
            </div>
          </div>

          <div v-if="overdueTasks.length === 0 && upcomingTasks.length === 0" class="card text-center py-8 text-gray-500">
            Keine anstehenden Aufgaben
          </div>

          <router-link
            to="/tasks"
            class="block mt-4 text-center text-primary-600 hover:text-primary-700 font-medium text-sm"
          >
            Alle Aufgaben anzeigen →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { dashboardAPI, taskAPI } from '../services/api'
import StatsWidget from '../components/StatsWidget.vue'
import TaskItem from '../components/TaskItem.vue'

const router = useRouter()
const loading = ref(true)
const error = ref(null)
const dashboardData = ref({})
const stats = ref({})
const cycles = ref([])
const upcomingTasks = ref([])
const overdueTasks = ref([])
const currentYear = new Date().getFullYear()

// Icons as functional components
const PlantIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' })
])

const CycleIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15' })
])

const TaskIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2' })
])

const AlertIcon = () => h('svg', { fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
])

const loadDashboard = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await dashboardAPI.getStats()
    dashboardData.value = response.data
    stats.value = response.data.stats || {}
    cycles.value = response.data.cycles || []
    upcomingTasks.value = response.data.upcoming_tasks || []
    overdueTasks.value = response.data.overdue_tasks || []
  } catch (err) {
    error.value = 'Fehler beim Laden des Dashboards'
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
}

const toggleTask = async (taskId) => {
  try {
    await taskAPI.toggleComplete(taskId)
    await loadDashboard()
  } catch (err) {
    console.error('Toggle task error:', err)
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('Aufgabe wirklich löschen?')) return
  try {
    await taskAPI.delete(taskId)
    await loadDashboard()
  } catch (err) {
    console.error('Delete task error:', err)
  }
}

const goToPlant = (plantId) => {
  router.push(`/plants/${plantId}`)
}

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

onMounted(() => {
  loadDashboard()
})
</script>
