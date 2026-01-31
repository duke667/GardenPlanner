<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Pflanzen</h1>
      <button @click="showAddModal = true" class="btn btn-primary">
        + Neue Pflanze
      </button>
    </div>

    <!-- Search and Filter -->
    <div class="card mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <input
          v-model="searchQuery"
          @input="searchPlants"
          type="text"
          placeholder="Suche nach Name, Sorte oder Herkunft..."
          class="input flex-1"
        />
        <select v-model="filterYear" @change="searchPlants" class="input md:w-48">
          <option value="">Alle Jahre</option>
          <option v-for="year in years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500">Lade Pflanzen...</p>
    </div>

    <!-- Plants Grid -->
    <div v-else-if="plants.length > 0" class="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
      <PlantCard
        v-for="plant in plants"
        :key="plant.id"
        :plant="plant"
        @click="goToPlant(plant.id)"
      />
    </div>

    <!-- Empty State -->
    <div v-else class="card text-center py-12">
      <p class="text-gray-500 mb-4">Noch keine Pflanzen angelegt</p>
      <button @click="showAddModal = true" class="btn btn-primary">
        Erste Pflanze anlegen
      </button>
    </div>

    <!-- Add Plant Modal -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal-content">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-900">Neue Pflanze anlegen</h2>
          <button @click="showAddModal = false" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="addPlant">
          <div class="space-y-4">
            <div>
              <label class="label">Pflanzenname *</label>
              <input
                v-model="newPlant.name"
                type="text"
                required
                class="input"
                placeholder="z.B. Tomate"
              />
            </div>

            <div>
              <label class="label">Sorte/Varietät</label>
              <input
                v-model="newPlant.variety"
                type="text"
                class="input"
                placeholder="z.B. Ochsenherz"
              />
            </div>

            <div>
              <label class="label">Samenherkunft</label>
              <textarea
                v-model="newPlant.seed_source"
                class="input"
                rows="2"
                placeholder="Wo wurden die Samen gekauft oder gewonnen?"
              />
            </div>

            <div>
              <label class="label">Notizen</label>
              <textarea
                v-model="newPlant.notes"
                class="input"
                rows="3"
                placeholder="Zusätzliche Informationen..."
              />
            </div>
          </div>

          <div class="flex gap-2 mt-6">
            <button type="submit" class="btn btn-primary flex-1" :disabled="saving">
              {{ saving ? 'Speichern...' : 'Pflanze anlegen' }}
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { plantAPI } from '../services/api'
import PlantCard from '../components/PlantCard.vue'

const router = useRouter()
const plants = ref([])
const loading = ref(true)
const searchQuery = ref('')
const filterYear = ref('')
const showAddModal = ref(false)
const saving = ref(false)

const newPlant = ref({
  name: '',
  variety: '',
  seed_source: '',
  notes: ''
})

const years = ref([])

const loadPlants = async () => {
  try {
    loading.value = true
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (filterYear.value) params.year = filterYear.value

    const response = await plantAPI.getAll(params)
    plants.value = response.data.results || response.data
  } catch (err) {
    console.error('Load plants error:', err)
  } finally {
    loading.value = false
  }
}

const searchPlants = () => {
  loadPlants()
}

const addPlant = async () => {
  try {
    saving.value = true
    await plantAPI.create(newPlant.value)
    showAddModal.value = false
    newPlant.value = { name: '', variety: '', seed_source: '', notes: '' }
    await loadPlants()
  } catch (err) {
    console.error('Add plant error:', err)
    alert('Fehler beim Anlegen der Pflanze')
  } finally {
    saving.value = false
  }
}

const goToPlant = (id) => {
  router.push(`/plants/${id}`)
}

onMounted(() => {
  loadPlants()
  // Generate years for filter
  const currentYear = new Date().getFullYear()
  years.value = Array.from({ length: 5 }, (_, i) => currentYear - i)
})
</script>

<style scoped>
.modal-overlay {
  @apply fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4;
}

.modal-content {
  @apply bg-white rounded-lg shadow-xl max-w-md w-full p-6 max-h-[90vh] overflow-y-auto;
}
</style>
