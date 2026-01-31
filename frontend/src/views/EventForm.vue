<template>
  <div>
    <h1 class="text-3xl font-bold text-gray-900 mb-6">Schnelleingabe</h1>

    <div class="max-w-2xl">
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

      <div class="card">
        <form @submit.prevent="addEvent">
          <div class="space-y-4">
            <!-- Pflanze auswählen -->
            <div>
              <label class="label">Pflanze *</label>
              <select v-model="selectedCycle" required class="input">
                <option value="">Pflanze wählen...</option>
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

            <!-- Event Type -->
            <div>
              <label class="label">Was möchtest du dokumentieren? *</label>
              <div class="grid grid-cols-2 md:grid-cols-3 gap-2">
                <button
                  v-for="type in eventTypes"
                  :key="type.value"
                  type="button"
                  @click="eventData.event_type = type.value"
                  class="event-type-btn"
                  :class="eventData.event_type === type.value ? 'event-type-active' : 'event-type-inactive'"
                >
                  {{ type.label }}
                </button>
              </div>
            </div>

            <!-- Date -->
            <div>
              <label class="label">Datum *</label>
              <input v-model="eventData.event_date" type="date" required class="input" />
            </div>

            <!-- Location (conditional) -->
            <div v-if="needsLocation">
              <label class="label">Ort</label>
              <input
                v-model="eventData.location"
                type="text"
                class="input"
                placeholder="z.B. Topf 5cm, Beet A, Gewächshaus"
              />
            </div>

            <!-- Quantity (conditional) -->
            <div v-if="needsQuantity">
              <label class="label">{{ quantityLabel }}</label>
              <div class="flex gap-2">
                <input
                  v-model="eventData.quantity"
                  type="number"
                  step="0.1"
                  class="input"
                  :placeholder="quantityPlaceholder"
                />
                <span class="flex items-center px-3 bg-gray-100 rounded text-gray-600">
                  {{ quantityUnit }}
                </span>
              </div>
            </div>

            <!-- Notes -->
            <div>
              <label class="label">Notizen</label>
              <textarea
                v-model="eventData.notes"
                class="input"
                rows="3"
                placeholder="Zusätzliche Informationen..."
              />
            </div>
          </div>

          <!-- Submit -->
          <div class="flex gap-2 mt-6">
            <button type="submit" class="btn btn-primary flex-1" :disabled="saving">
              {{ saving ? 'Speichern...' : 'Ereignis speichern' }}
            </button>
            <button type="button" @click="resetForm" class="btn btn-secondary">
              Zurücksetzen
            </button>
          </div>
        </form>
      </div>

      <!-- Recent Events -->
      <div v-if="recentEvents.length > 0" class="mt-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-3">Zuletzt hinzugefügt</h2>
        <div class="space-y-2">
          <div
            v-for="event in recentEvents"
            :key="event.id"
            class="card text-sm"
          >
            <div class="flex justify-between items-start">
              <div>
                <span class="font-medium">{{ event.event_type_display }}</span>
                <span class="text-gray-500 mx-2">·</span>
                <span class="text-gray-600">{{ formatDate(event.event_date) }}</span>
              </div>
              <span class="text-xs text-gray-500">Gerade eben</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { cycleAPI, eventAPI } from '../services/api'

const activeCycles = ref([])
const selectedCycle = ref('')
const saving = ref(false)
const recentEvents = ref([])
const successMessage = ref('')
const errorMessage = ref('')

const eventData = ref({
  event_type: 'watering',
  event_date: new Date().toISOString().split('T')[0],
  location: '',
  quantity: null,
  notes: ''
})

const eventTypes = [
  { value: 'sowing', label: 'Aussaat' },
  { value: 'germination', label: 'Keimung' },
  { value: 'transplanting', label: 'Umpflanzen' },
  { value: 'watering', label: 'Gießen' },
  { value: 'fertilizing', label: 'Düngen' },
  { value: 'planting_out', label: 'Auspflanzen' },
  { value: 'harvest', label: 'Ernte' },
  { value: 'pruning', label: 'Schneiden' },
  { value: 'other', label: 'Sonstiges' }
]

const needsLocation = computed(() => {
  return ['transplanting', 'planting_out'].includes(eventData.value.event_type)
})

const needsQuantity = computed(() => {
  return ['watering', 'fertilizing', 'harvest'].includes(eventData.value.event_type)
})

const quantityLabel = computed(() => {
  if (eventData.value.event_type === 'watering') return 'Wassermenge'
  if (eventData.value.event_type === 'fertilizing') return 'Düngermenge'
  if (eventData.value.event_type === 'harvest') return 'Ertrag'
  return 'Menge'
})

const quantityUnit = computed(() => {
  if (eventData.value.event_type === 'watering') return 'Liter'
  if (eventData.value.event_type === 'fertilizing') return 'ml'
  if (eventData.value.event_type === 'harvest') return 'kg'
  return ''
})

const quantityPlaceholder = computed(() => {
  if (eventData.value.event_type === 'watering') return 'z.B. 2.5'
  if (eventData.value.event_type === 'fertilizing') return 'z.B. 10'
  if (eventData.value.event_type === 'harvest') return 'z.B. 1.5'
  return ''
})

const loadActiveCycles = async () => {
  try {
    const currentYear = new Date().getFullYear()
    const response = await cycleAPI.getAll({ year: currentYear })
    activeCycles.value = response.data.results || response.data
  } catch (err) {
    console.error('Load cycles error:', err)
  }
}

const addEvent = async () => {
  if (!selectedCycle.value) {
    errorMessage.value = 'Bitte wähle eine Pflanze aus'
    setTimeout(() => errorMessage.value = '', 5000)
    return
  }

  try {
    saving.value = true
    errorMessage.value = ''
    successMessage.value = ''

    const response = await cycleAPI.addEvent(selectedCycle.value, eventData.value)
    recentEvents.value.unshift(response.data)

    successMessage.value = 'Ereignis erfolgreich gespeichert'
    setTimeout(() => successMessage.value = '', 3000)

    resetForm()
  } catch (err) {
    console.error('Add event error:', err)
    errorMessage.value = err.response?.data?.detail ||
                         err.response?.data?.message ||
                         'Fehler beim Speichern des Ereignisses'
    setTimeout(() => errorMessage.value = '', 5000)
  } finally {
    saving.value = false
  }
}

const resetForm = () => {
  eventData.value = {
    event_type: 'watering',
    event_date: new Date().toISOString().split('T')[0],
    location: '',
    quantity: null,
    notes: ''
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('de-DE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

onMounted(() => {
  loadActiveCycles()
})
</script>

<style scoped>
.event-type-btn {
  @apply px-4 py-3 rounded-lg border-2 transition-all font-medium text-sm;
}

.event-type-active {
  @apply border-primary-600 bg-primary-50 text-primary-700;
}

.event-type-inactive {
  @apply border-gray-200 bg-white text-gray-700 hover:border-gray-300 hover:bg-gray-50;
}
</style>
