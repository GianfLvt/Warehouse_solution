<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Lotti & Seriali</h1>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 dark:border-gray-700 mb-6">
      <button @click="activeTab = 'lots'" class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="activeTab === 'lots' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500'">
        Lotti
      </button>
      <button @click="activeTab = 'serials'" class="px-4 py-2 text-sm font-medium border-b-2 transition-colors"
        :class="activeTab === 'serials' ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500'">
        Numeri seriali
      </button>
    </div>

    <!-- Lots -->
    <div v-if="activeTab === 'lots'">
      <div class="flex justify-between items-center mb-4">
        <input v-model="lotSearch" class="input-field w-full max-w-xs" placeholder="Cerca lotto..." />
        <button @click="showLotForm = true" class="btn-primary text-sm">+ Nuovo Lotto</button>
      </div>
      <div class="card overflow-x-auto">
        <table class="w-full text-sm min-w-[800px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-4 py-3 text-left font-medium">Num. Lotto</th>
              <th class="px-4 py-3 text-left font-medium">Prodotto</th>
              <th class="px-4 py-3 text-right font-medium">Qtà iniziale</th>
              <th class="px-4 py-3 text-right font-medium">Qtà attuale</th>
              <th class="px-4 py-3 text-left font-medium">Produzione</th>
              <th class="px-4 py-3 text-left font-medium">Scadenza</th>
              <th class="px-4 py-3 text-left font-medium">Stato</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="l in filteredLots" :key="l.id" :class="isExpiringSoon(l) ? 'bg-amber-50 dark:bg-amber-900/10' : ''">
              <td class="px-4 py-3 font-mono font-medium">{{ l.lot_number }}</td>
              <td class="px-4 py-3">Prod #{{ l.product_id }}</td>
              <td class="px-4 py-3 text-right">{{ l.initial_quantity }}</td>
              <td class="px-4 py-3 text-right">{{ l.current_quantity }}</td>
              <td class="px-4 py-3 text-xs">{{ l.production_date ? formatDate(l.production_date) : '-' }}</td>
              <td class="px-4 py-3 text-xs" :class="isExpiringSoon(l) ? 'text-red-600 font-bold' : ''">{{ l.expiry_date ? formatDate(l.expiry_date) : '-' }}</td>
              <td class="px-4 py-3"><span class="badge text-xs" :class="lotStatusClass(l.status)">{{ l.status }}</span></td>
            </tr>
          </tbody>
        </table>
        <div v-if="filteredLots.length === 0" class="text-center text-gray-400 py-8">Nessun lotto trovato</div>
      </div>
    </div>

    <!-- Serials -->
    <div v-if="activeTab === 'serials'">
      <div class="flex justify-between items-center mb-4">
        <input v-model="serialSearch" class="input-field w-full max-w-xs" placeholder="Cerca seriale..." />
        <button @click="showSerialForm = true" class="btn-primary text-sm">+ Nuovo Seriale</button>
      </div>
      <div class="card overflow-x-auto">
        <table class="w-full text-sm min-w-[700px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-4 py-3 text-left font-medium">Numero seriale</th>
              <th class="px-4 py-3 text-left font-medium">Prodotto</th>
              <th class="px-4 py-3 text-left font-medium">Lotto</th>
              <th class="px-4 py-3 text-left font-medium">Stato</th>
              <th class="px-4 py-3 text-left font-medium">Ubicazione</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="s in filteredSerials" :key="s.id">
              <td class="px-4 py-3 font-mono font-medium">{{ s.serial_number }}</td>
              <td class="px-4 py-3">Prod #{{ s.product_id }}</td>
              <td class="px-4 py-3">{{ s.lot_id || '-' }}</td>
              <td class="px-4 py-3"><span class="badge text-xs" :class="serialStatusClass(s.status)">{{ s.status }}</span></td>
              <td class="px-4 py-3">{{ s.current_location_id || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="filteredSerials.length === 0" class="text-center text-gray-400 py-8">Nessun seriale trovato</div>
      </div>
    </div>

    <!-- Lot form modal -->
    <div v-if="showLotForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showLotForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuovo Lotto</h3>
        <form @submit.prevent="createLot" class="space-y-4">
          <div><label class="label">Num. Lotto *</label><input v-model="lotForm.lot_number" class="input-field w-full" required /></div>
          <div><label class="label">Prodotto ID *</label><input v-model.number="lotForm.product_id" class="input-field w-full" type="number" required /></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Qtà iniziale</label><input v-model.number="lotForm.initial_quantity" class="input-field w-full" type="number" /></div>
            <div><label class="label">Qtà attuale</label><input v-model.number="lotForm.current_quantity" class="input-field w-full" type="number" /></div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Data produzione</label><input v-model="lotForm.production_date" class="input-field w-full" type="date" /></div>
            <div><label class="label">Data scadenza</label><input v-model="lotForm.expiry_date" class="input-field w-full" type="date" /></div>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showLotForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Crea</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Serial form modal -->
    <div v-if="showSerialForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showSerialForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuovo Seriale</h3>
        <form @submit.prevent="createSerial" class="space-y-4">
          <div><label class="label">Numero seriale *</label><input v-model="serialForm.serial_number" class="input-field w-full" required /></div>
          <div><label class="label">Prodotto ID *</label><input v-model.number="serialForm.product_id" class="input-field w-full" type="number" required /></div>
          <div><label class="label">Lotto ID</label><input v-model.number="serialForm.lot_id" class="input-field w-full" type="number" /></div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showSerialForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Crea</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/api'

const activeTab = ref('lots')
const lots = ref([])
const serials = ref([])
const lotSearch = ref('')
const serialSearch = ref('')
const showLotForm = ref(false)
const showSerialForm = ref(false)

const lotForm = ref({ lot_number: '', product_id: null, initial_quantity: 0, current_quantity: 0, production_date: '', expiry_date: '' })
const serialForm = ref({ serial_number: '', product_id: null, lot_id: null })

const filteredLots = computed(() => {
  if (!lotSearch.value) return lots.value
  return lots.value.filter(l => l.lot_number.toLowerCase().includes(lotSearch.value.toLowerCase()))
})

const filteredSerials = computed(() => {
  if (!serialSearch.value) return serials.value
  return serials.value.filter(s => s.serial_number.toLowerCase().includes(serialSearch.value.toLowerCase()))
})

function isExpiringSoon(l) {
  if (!l.expiry_date) return false
  const days = (new Date(l.expiry_date) - new Date()) / (1000 * 60 * 60 * 24)
  return days < 30 && days > 0
}

async function load() {
  const [l, s] = await Promise.all([
    api.get('/lots'),
    api.get('/lots/serials'),
  ])
  lots.value = l.data
  serials.value = s.data
}

async function createLot() {
  const payload = { ...lotForm.value }
  if (!payload.production_date) delete payload.production_date
  if (!payload.expiry_date) delete payload.expiry_date
  await api.post('/lots', payload)
  showLotForm.value = false
  lotForm.value = { lot_number: '', product_id: null, initial_quantity: 0, current_quantity: 0, production_date: '', expiry_date: '' }
  await load()
}

async function createSerial() {
  const payload = { ...serialForm.value }
  if (!payload.lot_id) delete payload.lot_id
  await api.post('/lots/serials', payload)
  showSerialForm.value = false
  serialForm.value = { serial_number: '', product_id: null, lot_id: null }
  await load()
}

function lotStatusClass(s) {
  const m = { active: 'bg-green-100 text-green-700', quarantine: 'bg-yellow-100 text-yellow-700', expired: 'bg-red-100 text-red-700', consumed: 'bg-gray-100 text-gray-600' }
  return m[s] || 'bg-gray-100 text-gray-600'
}

function serialStatusClass(s) {
  const m = { available: 'bg-green-100 text-green-700', reserved: 'bg-blue-100 text-blue-700', sold: 'bg-gray-100 text-gray-600', defective: 'bg-red-100 text-red-700' }
  return m[s] || 'bg-gray-100 text-gray-600'
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('it-IT') : '-' }

onMounted(load)
</script>
