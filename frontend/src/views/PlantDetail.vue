<template>
  <div>
    <!-- Success/Error Messages -->
    <div v-if="successMessage" class="card bg-green-50 border-green-200 mb-4">
      <div class="flex items-center gap-2 text-green-800">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
        {{ successMessage }}
      </div>
    </div>

    <div v-if="errorMessage" class="card bg-red-50 border-red-200 mb-4">
      <div class="flex items-center gap-2 text-red-800">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
        {{ errorMessage }}
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Lade Pflanze...</p>
    </div>

    <div v-else-if="plant">
      <!-- Header -->
      <div class="mb-6">
        <button @click="$router.back()" class="text-primary-600 hover:text-primary-700 mb-2 inline-flex items-center">
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
          Zurück
        </button>
        <h1 class="text-3xl font-bold text-gray-900">
          {{ plant.name }}
          <span v-if="plant.variety" class="text-gray-500 text-2xl">
            ({{ plant.variety }})
          </span>
        </h1>
        <p v-if="plant.seed_source" class="text-gray-600 mt-2">
          Samen: {{ plant.seed_source }}
        </p>
      </div>

      <!-- Info Card -->
      <div class="card mb-6">
        <div class="grid md:grid-cols-3 gap-4">
          <div>
            <span class="text-sm text-gray-600">Anbau-Zyklen</span>
            <p class="text-2xl font-bold text-gray-900">{{ plant.cycle_count }}</p>
          </div>
          <div v-if="plant.latest_cycle">
            <span class="text-sm text-gray-600">Aktueller Status</span>
            <p class="text-lg font-semibold text-gray-900">{{ plant.latest_cycle.status_display }}</p>
          </div>
          <div v-if="plant.latest_cycle">
            <span class="text-sm text-gray-600">Jahr</span>
            <p class="text-2xl font-bold text-gray-900">{{ plant.latest_cycle.year }}</p>
          </div>
        </div>

        <div v-if="plant.notes" class="mt-4 pt-4 border-t border-gray-100">
          <span class="text-sm text-gray-600">Notizen</span>
          <p class="text-gray-700 mt-1">{{ plant.notes }}</p>
        </div>
      </div>

      <!-- Tabs -->
      <div class="mb-6 border-b border-gray-200">
        <nav class="-mb-px flex space-x-8">
          <button
            @click="activeTab = 'current'"
            class="tab-button"
            :class="activeTab === 'current' ? 'tab-active' : 'tab-inactive'"
          >
            Aktueller Zyklus
          </button>
          <button
            @click="activeTab = 'history'"
            class="tab-button"
            :class="activeTab === 'history' ? 'tab-active' : 'tab-inactive'"
          >
            Historie
          </button>
        </nav>
      </div>

      <!-- Current Cycle Tab -->
      <div v-if="activeTab === 'current' && plant.latest_cycle">
        <div class="grid md:grid-cols-2 gap-6">
          <!-- Events Timeline -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold text-gray-900">Ereignisse</h2>
              <button @click="showEventModal = true" class="btn btn-primary text-sm">
                + Event
              </button>
            </div>

            <div v-if="plant.latest_cycle.events.length > 0" class="card">
              <EventTimeline :events="plant.latest_cycle.events" />
            </div>
            <div v-else class="card text-center py-8 text-gray-500">
              Noch keine Ereignisse
            </div>
          </div>

          <!-- Tasks -->
          <div>
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-xl font-semibold text-gray-900">Aufgaben</h2>
              <button @click="showTaskModal = true" class="btn btn-primary text-sm">
                + Aufgabe
              </button>
            </div>

            <div v-if="plant.latest_cycle.tasks.length > 0" class="space-y-2">
              <TaskItem
                v-for="task in plant.latest_cycle.tasks"
                :key="task.id"
                :task="task"
                @toggle="toggleTask"
                @delete="deleteTask"
              />
            </div>
            <div v-else class="card text-center py-8 text-gray-500">
              Keine Aufgaben
            </div>
          </div>
        </div>

        <!-- Seed Saving Info -->
        <div class="card mt-6 bg-green-50 border-green-200">
          <label class="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              :checked="plant.latest_cycle.seed_saved"
              @change="toggleSeedSaved"
              class="w-5 h-5 text-primary-600 rounded focus:ring-primary-500"
            />
            <span class="font-medium text-gray-900">Samen für nächstes Jahr gewonnen</span>
          </label>
          <textarea
            v-if="plant.latest_cycle.seed_saved"
            v-model="seedNotes"
            @blur="updateSeedNotes"
            class="input mt-3"
            rows="2"
            placeholder="Notizen zur Saatgutgewinnung..."
          />
        </div>
      </div>

      <!-- No Current Cycle -->
      <div v-else-if="activeTab === 'current'" class="card text-center py-12">
        <p class="text-gray-500 mb-4">Kein aktiver Anbau-Zyklus für dieses Jahr</p>
        <button @click="createNewCycle" class="btn btn-primary">
          Neuen Zyklus anlegen
        </button>
      </div>

      <!-- History Tab -->
      <div v-if="activeTab === 'history'">
        <div v-if="plant.cycles && plant.cycles.length > 0" class="space-y-4">
          <div
            v-for="cycle in plant.cycles"
            :key="cycle.id"
            class="card"
          >
            <div class="flex justify-between items-start mb-3">
              <div>
                <h3 class="text-lg font-semibold text-gray-900">{{ cycle.year }}</h3>
                <p class="text-sm text-gray-600">{{ cycle.status_display }}</p>
              </div>
              <span v-if="cycle.seed_saved" class="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">
                Samen gewonnen
              </span>
            </div>

            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span class="text-gray-600">Ereignisse:</span>
                <span class="font-medium text-gray-900 ml-1">{{ cycle.event_count }}</span>
              </div>
              <div>
                <span class="text-gray-600">Aufgaben:</span>
                <span class="font-medium text-gray-900 ml-1">{{ cycle.task_count }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="card text-center py-12 text-gray-500">
          Keine Anbau-Historie
        </div>
      </div>
    </div>

    <!-- Add Event Modal -->
    <div v-if="showEventModal" class="modal-overlay" @click.self="showEventModal = false">
      <div class="modal-content">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Ereignis erfassen</h2>
        <form @submit.prevent="addEvent">
          <div class="space-y-4">
            <div>
              <label class="label">Ereignistyp *</label>
              <select v-model="newEvent.event_type" required class="input">
                <option value="sowing">Aussaat</option>
                <option value="germination">Keimung</option>
                <option value="transplanting">Umpflanzen</option>
                <option value="watering">Gießen</option>
                <option value="fertilizing">Düngen</option>
                <option value="planting_out">Ins Beet pflanzen</option>
                <option value="harvest">Ernte</option>
                <option value="pruning">Schneiden</option>
                <option value="other">Sonstiges</option>
              </select>
            </div>

            <div>
              <label class="label">Datum *</label>
              <input v-model="newEvent.event_date" type="date" required class="input" />
            </div>

            <div>
              <label class="label">Ort</label>
              <input v-model="newEvent.location" type="text" class="input" placeholder="z.B. Topf 5cm, Beet A" />
            </div>

            <div>
              <label class="label">Menge</label>
              <input v-model="newEvent.quantity" type="number" step="0.1" class="input" placeholder="Liter / kg" />
            </div>

            <div>
              <label class="label">Notizen</label>
              <textarea v-model="newEvent.notes" class="input" rows="3" />
            </div>
          </div>

          <div class="flex gap-2 mt-6">
            <button type="submit" class="btn btn-primary flex-1" :disabled="savingEvent">
              {{ savingEvent ? 'Speichern...' : 'Speichern' }}
            </button>
            <button type="button" @click="showEventModal = false" class="btn btn-secondary" :disabled="savingEvent">
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Task Modal -->
    <div v-if="showTaskModal" class="modal-overlay" @click.self="showTaskModal = false">
      <div class="modal-content">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Aufgabe anlegen</h2>
        <form @submit.prevent="addTask">
          <div class="space-y-4">
            <div>
              <label class="label">Titel *</label>
              <input v-model="newTask.title" type="text" required class="input" />
            </div>

            <div>
              <label class="label">Beschreibung</label>
              <textarea v-model="newTask.description" class="input" rows="3" />
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
          </div>

          <div class="flex gap-2 mt-6">
            <button type="submit" class="btn btn-primary flex-1" :disabled="savingTask">
              {{ savingTask ? 'Speichern...' : 'Speichern' }}
            </button>
            <button type="button" @click="showTaskModal = false" class="btn btn-secondary" :disabled="savingTask">
              Abbrechen
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { plantAPI, cycleAPI, taskAPI } from '../services/api'
import EventTimeline from '../components/EventTimeline.vue'
import TaskItem from '../components/TaskItem.vue'

const route = useRoute()
const plant = ref(null)
const loading = ref(true)
const activeTab = ref('current')
const showEventModal = ref(false)
const showTaskModal = ref(false)
const seedNotes = ref('')
const successMessage = ref('')
const errorMessage = ref('')
const savingEvent = ref(false)
const savingTask = ref(false)

const newEvent = ref({
  event_type: 'sowing',
  event_date: new Date().toISOString().split('T')[0],
  location: '',
  quantity: null,
  notes: ''
})

const newTask = ref({
  title: '',
  description: '',
  due_date: '',
  priority: 'medium'
})

const loadPlant = async () => {
  try {
    loading.value = true
    const response = await plantAPI.get(route.params.id)
    plant.value = response.data
    if (plant.value.latest_cycle) {
      seedNotes.value = plant.value.latest_cycle.seed_saved_notes || ''
    }
  } catch (err) {
    console.error('Load plant error:', err)
  } finally {
    loading.value = false
  }
}

const createNewCycle = async () => {
  try {
    loading.value = true
    errorMessage.value = ''
    successMessage.value = ''

    await cycleAPI.create({
      plant: plant.value.id,
      year: new Date().getFullYear(),
      status: 'planning'
    })

    successMessage.value = 'Neuer Anbau-Zyklus erfolgreich angelegt'
    setTimeout(() => successMessage.value = '', 3000)

    await loadPlant()
  } catch (err) {
    console.error('Create cycle error:', err)
    errorMessage.value = err.response?.data?.detail ||
                         err.response?.data?.message ||
                         'Fehler beim Anlegen des Zyklus'
    setTimeout(() => errorMessage.value = '', 5000)
  } finally {
    loading.value = false
  }
}

const addEvent = async () => {
  if (!plant.value.latest_cycle) {
    errorMessage.value = 'Kein aktiver Zyklus vorhanden'
    setTimeout(() => errorMessage.value = '', 5000)
    return
  }

  try {
    savingEvent.value = true
    errorMessage.value = ''
    successMessage.value = ''

    // Bereite Event-Daten vor - entferne leere/null Felder
    const eventPayload = { ...newEvent.value }
    if (!eventPayload.location) delete eventPayload.location
    if (!eventPayload.quantity) delete eventPayload.quantity
    if (!eventPayload.notes) delete eventPayload.notes

    await cycleAPI.addEvent(plant.value.latest_cycle.id, eventPayload)

    showEventModal.value = false
    newEvent.value = {
      event_type: 'sowing',
      event_date: new Date().toISOString().split('T')[0],
      location: '',
      quantity: null,
      notes: ''
    }

    successMessage.value = 'Ereignis erfolgreich gespeichert'
    setTimeout(() => successMessage.value = '', 3000)

    await loadPlant()
  } catch (err) {
    console.error('Add event error:', err)
    console.error('Response data:', err.response?.data)

    // Formatiere die Fehlermeldung
    let errorMsg = 'Fehler beim Speichern des Ereignisses'
    if (err.response?.data) {
      const data = err.response.data
      if (typeof data === 'string') {
        errorMsg = data
      } else if (data.detail) {
        errorMsg = data.detail
      } else if (data.message) {
        errorMsg = data.message
      } else {
        // Zeige alle Feldfehlermeldungen
        const errors = Object.entries(data).map(([key, value]) => {
          const msg = Array.isArray(value) ? value.join(', ') : value
          return `${key}: ${msg}`
        }).join('\n')
        errorMsg = errors || errorMsg
      }
    }

    errorMessage.value = errorMsg
    setTimeout(() => errorMessage.value = '', 10000)
  } finally {
    savingEvent.value = false
  }
}

const addTask = async () => {
  if (!plant.value.latest_cycle) {
    errorMessage.value = 'Kein aktiver Zyklus vorhanden'
    setTimeout(() => errorMessage.value = '', 5000)
    return
  }

  try {
    savingTask.value = true
    errorMessage.value = ''
    successMessage.value = ''

    await cycleAPI.addTask(plant.value.latest_cycle.id, newTask.value)

    showTaskModal.value = false
    newTask.value = { title: '', description: '', due_date: '', priority: 'medium' }

    successMessage.value = 'Aufgabe erfolgreich erstellt'
    setTimeout(() => successMessage.value = '', 3000)

    await loadPlant()
  } catch (err) {
    console.error('Add task error:', err)
    errorMessage.value = err.response?.data?.detail ||
                         err.response?.data?.message ||
                         'Fehler beim Erstellen der Aufgabe'
    setTimeout(() => errorMessage.value = '', 5000)
  } finally {
    savingTask.value = false
  }
}

const toggleTask = async (taskId) => {
  try {
    await taskAPI.toggleComplete(taskId)
    await loadPlant()
  } catch (err) {
    console.error('Toggle task error:', err)
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('Aufgabe wirklich löschen?')) return
  try {
    await taskAPI.delete(taskId)
    await loadPlant()
  } catch (err) {
    console.error('Delete task error:', err)
  }
}

const toggleSeedSaved = async () => {
  try {
    await cycleAPI.update(plant.value.latest_cycle.id, {
      ...plant.value.latest_cycle,
      seed_saved: !plant.value.latest_cycle.seed_saved
    })
    await loadPlant()
  } catch (err) {
    console.error('Toggle seed saved error:', err)
  }
}

const updateSeedNotes = async () => {
  try {
    await cycleAPI.update(plant.value.latest_cycle.id, {
      ...plant.value.latest_cycle,
      seed_saved_notes: seedNotes.value
    })
  } catch (err) {
    console.error('Update seed notes error:', err)
  }
}

onMounted(() => {
  loadPlant()
})
</script>

<style scoped>
.tab-button {
  @apply py-4 px-1 border-b-2 font-medium text-sm transition-colors;
}

.tab-active {
  @apply border-primary-600 text-primary-600;
}

.tab-inactive {
  @apply border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300;
}

.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto;
}
</style>
