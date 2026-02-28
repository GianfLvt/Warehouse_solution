<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Spedizioni</h1>
      <button @click="showForm = true" class="btn-primary text-center">+ Nuova Spedizione</button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <div class="card p-4">
        <p class="text-xs text-gray-500">In preparazione</p>
        <p class="text-2xl font-bold text-amber-600">{{ shipments.filter(s => s.status === 'preparazione').length }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">In transito</p>
        <p class="text-2xl font-bold text-blue-600">{{ shipments.filter(s => s.status === 'in_transito').length }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Consegnate</p>
        <p class="text-2xl font-bold text-green-600">{{ shipments.filter(s => s.status === 'consegnato').length }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Totale camion caricati</p>
        <p class="text-2xl font-bold text-gray-600">{{ truckLoads.length }}</p>
      </div>
    </div>

    <div class="card mb-4">
      <div class="p-4 flex flex-wrap gap-3 items-center">
        <input v-model="search" class="input-field w-full sm:max-w-xs" placeholder="Cerca per tracking..." />
        <select v-model="statusFilter" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutti gli stati</option>
          <option value="preparazione">Preparazione</option>
          <option value="pronto_ritiro">Pronto ritiro</option>
          <option value="in_transito">In transito</option>
          <option value="consegnato">Consegnato</option>
        </select>
      </div>
    </div>

    <!-- Shipments table -->
    <div class="card overflow-x-auto mb-6">
      <table class="w-full text-sm min-w-[1000px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">ID</th>
            <th class="px-4 py-3 text-left font-medium">Ordine</th>
            <th class="px-4 py-3 text-left font-medium">Corriere</th>
            <th class="px-4 py-3 text-left font-medium">Tracking</th>
            <th class="px-4 py-3 text-left font-medium">Stato</th>
            <th class="px-4 py-3 text-right font-medium">Peso (kg)</th>
            <th class="px-4 py-3 text-right font-medium">Colli</th>
            <th class="px-4 py-3 text-right font-medium">Costo</th>
            <th class="px-4 py-3 text-left font-medium">Data spedizione</th>
            <th class="px-4 py-3 text-center font-medium">Azioni</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="s in filteredShipments" :key="s.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3">#{{ s.id }}</td>
            <td class="px-4 py-3">
              <router-link :to="`/orders/${s.order_id}`" class="text-primary-600 hover:underline">#{{ s.order_id }}</router-link>
            </td>
            <td class="px-4 py-3">{{ s.carrier_name || '-' }}</td>
            <td class="px-4 py-3 font-mono text-xs">{{ s.tracking_number || '-' }}</td>
            <td class="px-4 py-3"><span class="badge text-xs" :class="shipStatusClass(s.status)">{{ shipStatusLabel(s.status) }}</span></td>
            <td class="px-4 py-3 text-right">{{ s.total_weight_kg?.toFixed(1) || '-' }}</td>
            <td class="px-4 py-3 text-right">{{ s.total_packages || '-' }}</td>
            <td class="px-4 py-3 text-right">{{ s.shipping_cost ? '€ ' + s.shipping_cost.toFixed(2) : '-' }}</td>
            <td class="px-4 py-3">{{ s.shipped_at ? formatDate(s.shipped_at) : '-' }}</td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <button v-if="s.status === 'preparazione'" @click="updateStatus(s, 'pronto_ritiro')" class="text-xs text-blue-600 hover:underline">Pronto</button>
                <button v-if="s.status === 'pronto_ritiro'" @click="updateStatus(s, 'in_transito')" class="text-xs text-amber-600 hover:underline">Spedisci</button>
                <button v-if="s.status === 'in_transito'" @click="updateStatus(s, 'consegnato')" class="text-xs text-green-600 hover:underline">Consegnato</button>
                <button @click="deleteShipment(s)" class="text-xs text-red-500 hover:underline">Elimina</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredShipments.length === 0" class="text-center text-gray-400 py-8">Nessuna spedizione trovata</div>
    </div>

    <!-- Truck loads section -->
    <div class="card p-5">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Carichi Camion</h2>
        <button @click="showTruckForm = true" class="btn-primary text-sm">+ Nuovo Carico</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[800px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-3 py-2 text-left font-medium">Targa</th>
              <th class="px-3 py-2 text-left font-medium">Autista</th>
              <th class="px-3 py-2 text-left font-medium">Stato</th>
              <th class="px-3 py-2 text-left font-medium">Banchina</th>
              <th class="px-3 py-2 text-right font-medium">Peso/Max</th>
              <th class="px-3 py-2 text-right font-medium">Volume/Max</th>
              <th class="px-3 py-2 text-left font-medium">Partenza</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="t in truckLoads" :key="t.id">
              <td class="px-3 py-2 font-medium">{{ t.plate_number }}</td>
              <td class="px-3 py-2">{{ t.driver_name || '-' }}</td>
              <td class="px-3 py-2"><span class="badge text-xs" :class="truckStatusClass(t.status)">{{ t.status }}</span></td>
              <td class="px-3 py-2">{{ t.dock_slot_id || '-' }}</td>
              <td class="px-3 py-2 text-right">{{ t.current_weight_kg?.toFixed(0) || 0 }} / {{ t.max_weight_kg?.toFixed(0) || '-' }}</td>
              <td class="px-3 py-2 text-right">{{ t.current_volume_m3?.toFixed(1) || 0 }} / {{ t.max_volume_m3?.toFixed(1) || '-' }}</td>
              <td class="px-3 py-2">{{ t.departure_time ? formatDate(t.departure_time) : '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="truckLoads.length === 0" class="text-center text-gray-400 py-4 text-sm">Nessun carico</div>
      </div>
    </div>

    <!-- Create shipment modal -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuova Spedizione</h3>
        <form @submit.prevent="createShipment" class="space-y-4">
          <div>
            <label class="label">Ordine ID *</label>
            <input v-model.number="shipForm.order_id" class="input-field w-full" type="number" required />
          </div>
          <div>
            <label class="label">Corriere</label>
            <input v-model="shipForm.carrier_name" class="input-field w-full" />
          </div>
          <div>
            <label class="label">Tracking Number</label>
            <input v-model="shipForm.tracking_number" class="input-field w-full" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="label">Peso (kg)</label>
              <input v-model.number="shipForm.total_weight_kg" class="input-field w-full" type="number" step="0.01" />
            </div>
            <div>
              <label class="label">Colli</label>
              <input v-model.number="shipForm.total_packages" class="input-field w-full" type="number" />
            </div>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Crea</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create truck load modal -->
    <div v-if="showTruckForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showTruckForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuovo Carico Camion</h3>
        <form @submit.prevent="createTruckLoad" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Targa *</label><input v-model="truckForm.plate_number" class="input-field w-full" required /></div>
            <div><label class="label">Autista</label><input v-model="truckForm.driver_name" class="input-field w-full" /></div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Max Peso (kg)</label><input v-model.number="truckForm.max_weight_kg" class="input-field w-full" type="number" /></div>
            <div><label class="label">Max Volume (m³)</label><input v-model.number="truckForm.max_volume_m3" class="input-field w-full" type="number" step="0.01" /></div>
          </div>
          <div><label class="label">Partenza prevista</label><input v-model="truckForm.departure_time" class="input-field w-full" type="datetime-local" /></div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showTruckForm = false" class="btn-secondary">Annulla</button>
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

const shipments = ref([])
const truckLoads = ref([])
const search = ref('')
const statusFilter = ref('')
const showForm = ref(false)
const showTruckForm = ref(false)

const shipForm = ref({ order_id: null, carrier_name: '', tracking_number: '', total_weight_kg: null, total_packages: null })
const truckForm = ref({ plate_number: '', driver_name: '', max_weight_kg: null, max_volume_m3: null, departure_time: '' })

const filteredShipments = computed(() => {
  return shipments.value.filter(s => {
    if (statusFilter.value && s.status !== statusFilter.value) return false
    if (search.value && !s.tracking_number?.toLowerCase().includes(search.value.toLowerCase())) return false
    return true
  })
})

async function load() {
  const [s, t] = await Promise.all([
    api.get('/shipments'),
    api.get('/shipments/trucks'),
  ])
  shipments.value = s.data
  truckLoads.value = t.data
}

async function createShipment() {
  await api.post('/shipments', shipForm.value)
  showForm.value = false
  shipForm.value = { order_id: null, carrier_name: '', tracking_number: '', total_weight_kg: null, total_packages: null }
  await load()
}

async function createTruckLoad() {
  const payload = { ...truckForm.value, departure_time: truckForm.value.departure_time || undefined }
  await api.post('/shipments/trucks', payload)
  showTruckForm.value = false
  truckForm.value = { plate_number: '', driver_name: '', max_weight_kg: null, max_volume_m3: null, departure_time: '' }
  await load()
}

async function updateStatus(s, newStatus) {
  await api.put(`/shipments/${s.id}`, { status: newStatus })
  await load()
}

async function deleteShipment(s) {
  if (!confirm('Eliminare questa spedizione?')) return
  await api.delete(`/shipments/${s.id}`)
  await load()
}

const statusMap = {
  preparazione: { label: 'Preparazione', class: 'bg-gray-100 text-gray-700' },
  pronto_ritiro: { label: 'Pronto ritiro', class: 'bg-blue-100 text-blue-700' },
  in_transito: { label: 'In transito', class: 'bg-amber-100 text-amber-700' },
  consegnato: { label: 'Consegnato', class: 'bg-green-100 text-green-700' },
}
function shipStatusLabel(s) { return statusMap[s]?.label || s }
function shipStatusClass(s) { return statusMap[s]?.class || '' }
function truckStatusClass(s) {
  const m = { caricamento: 'bg-yellow-100 text-yellow-700', pronto: 'bg-blue-100 text-blue-700', partito: 'bg-green-100 text-green-700' }
  return m[s] || 'bg-gray-100 text-gray-600'
}
function formatDate(d) { return new Date(d).toLocaleDateString('it-IT') }

onMounted(load)
</script>
