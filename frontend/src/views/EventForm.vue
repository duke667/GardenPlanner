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
              <select v-model="selectedPlant" required class="input" @change="onPlantChange">
                <option value="">Pflanze wählen...</option>
                <option
                  v-for="plant in allPlants"
                  :key="plant.id"
                  :value="plant.id"
                >
                  {{ plant.name }}
                  <template v-if="plant.variety">({{ plant.variety }})</template>
                  <template v-if="!plant.has_current_cycle"> - ⚠️ Kein Zyklus für {{ currentYear }}</template>
                </option>
              </select>
              <p v-if="selectedPlant && needsNewCycle" class="text-sm text-orange-600 mt-1">
                ℹ️ Ein neuer Anbau-Zyklus wird automatisch erstellt
              </p>
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
import { cycleAPI, plantAPI } from '../services/api'

const allPlants = ref([])
const activeCycles = ref({})
const selectedPlant = ref('')
const selectedCycleId = ref(null)
const needsNewCycle = ref(false)
const saving = ref(false)
const recentEvents = ref([])
const successMessage = ref('')
const errorMessage = ref('')
const currentYear = new Date().getFullYear()

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

const loadPlants = async () => {
  try {
    // Lade alle Pflanzen
    const plantsResponse = await plantAPI.getAll()
    const plants = plantsResponse.data.results || plantsResponse.data

    // Lade aktuelle Zyklen
    const cyclesResponse = await cycleAPI.getAll({ year: currentYear })
    const cycles = cyclesResponse.data.results || cyclesResponse.data

    // Erstelle Mapping von plant_id zu cycle
    const cycleMap = {}
    cycles.forEach(cycle => {
      cycleMap[cycle.plant] = cycle
    })
    activeCycles.value = cycleMap

    // Markiere Pflanzen, die Zyklen haben
    allPlants.value = plants.map(plant => ({
      ...plant,
      has_current_cycle: !!cycleMap[plant.id]
    }))
  } catch (err) {
    console.error('Load plants error:', err)
    errorMessage.value = 'Fehler beim Laden der Pflanzen'
  }
}

const onPlantChange = () => {
  const plantId = selectedPlant.value
  if (!plantId) {
    needsNewCycle.value = false
    selectedCycleId.value = null
    return
  }

  const cycle = activeCycles.value[plantId]
  if (cycle) {
    selectedCycleId.value = cycle.id
    needsNewCycle.value = false
  } else {
    selectedCycleId.value = null
    needsNewCycle.value = true
  }
}

const addEvent = async () => {
  if (!selectedPlant.value) {
    errorMessage.value = 'Bitte wähle eine Pflanze aus'
    setTimeout(() => errorMessage.value = '', 5000)
    return
  }

  try {
    saving.value = true
    errorMessage.value = ''
    successMessage.value = ''

    let cycleId = selectedCycleId.value

    // Erstelle neuen Zyklus, wenn keiner existiert
    if (!cycleId) {
      const cycleResponse = await cycleAPI.create({
        plant: selectedPlant.value,
        year: currentYear,
        status: 'planning'
      })
      cycleId = cycleResponse.data.id
    }

    // Bereite Event-Daten vor - entferne leere/null Felder
    const eventPayload = { ...eventData.value }
    if (!eventPayload.location) delete eventPayload.location
    if (!eventPayload.quantity) delete eventPayload.quantity
    if (!eventPayload.notes) delete eventPayload.notes

    // Füge Event zum Zyklus hinzu
    const response = await cycleAPI.addEvent(cycleId, eventPayload)
    recentEvents.value.unshift(response.data)

    successMessage.value = needsNewCycle.value
      ? 'Zyklus angelegt und Ereignis gespeichert'
      : 'Ereignis erfolgreich gespeichert'
    setTimeout(() => successMessage.value = '', 3000)

    // Lade Pflanzen neu, um aktualisierten Zyklus-Status zu zeigen
    await loadPlants()
    resetForm()
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
  loadPlants()
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
