<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Magazzini</h1>
      <button @click="showForm = true" class="btn-primary text-center">+ Nuovo Magazzino</button>
    </div>

    <!-- Warehouse list -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div v-for="w in warehouses" :key="w.id" class="card p-5 hover:shadow-md transition-shadow cursor-pointer" @click="selectWarehouse(w)">
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold text-lg">{{ w.name }}</h3>
          <span class="badge" :class="w.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'">
            {{ w.is_active ? 'Attivo' : 'Inattivo' }}
          </span>
        </div>
        <p class="text-sm text-gray-500">{{ w.code }}</p>
        <p v-if="w.address" class="text-sm text-gray-400 mt-1">{{ w.address }}, {{ w.city }}</p>
        <p v-if="w.warehouse_type" class="text-xs text-gray-400 mt-1">Tipo: {{ w.warehouse_type }}</p>
        <div class="mt-3 flex gap-2">
          <button @click.stop="editWarehouse(w)" class="text-xs text-primary-600 hover:underline">Modifica</button>
          <button @click.stop="deleteWarehouse(w)" class="text-xs text-red-500 hover:underline">Elimina</button>
        </div>
      </div>
    </div>

    <!-- Selected warehouse zones + locations -->
    <div v-if="selected" class="space-y-6">
      <div class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">Zone di "{{ selected.name }}"</h2>
          <button @click="showZoneForm = true" class="btn-primary text-sm">+ Nuova Zona</button>
        </div>
        <div v-if="zones.length === 0" class="text-gray-400 text-sm text-center py-4">Nessuna zona configurata</div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div v-for="z in zones" :key="z.id" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4" :class="selectedZone?.id === z.id ? 'ring-2 ring-primary-500' : ''" @click="selectZone(z)">
            <div class="flex items-center justify-between">
              <span class="font-medium">{{ z.name }}</span>
              <span class="text-xs badge bg-blue-100 text-blue-700">{{ z.zone_type || 'storage' }}</span>
            </div>
            <p class="text-xs text-gray-400 mt-1">Codice: {{ z.code }}</p>
            <p v-if="z.temperature_min != null" class="text-xs text-gray-400">Temp: {{ z.temperature_min }}°C - {{ z.temperature_max }}°C</p>
          </div>
        </div>
      </div>

      <!-- Locations -->
      <div v-if="selectedZone" class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">Ubicazioni — {{ selectedZone.name }}</h2>
          <button @click="showLocationForm = true" class="btn-primary text-sm">+ Nuova Ubicazione</button>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-sm min-w-[700px]">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-3 py-2 text-left font-medium">Barcode</th>
                <th class="px-3 py-2 text-left font-medium">Tipo</th>
                <th class="px-3 py-2 text-left font-medium">Corsia</th>
                <th class="px-3 py-2 text-left font-medium">Scaffale</th>
                <th class="px-3 py-2 text-left font-medium">Livello</th>
                <th class="px-3 py-2 text-left font-medium">Posizione</th>
                <th class="px-3 py-2 text-right font-medium">Capacità (kg)</th>
                <th class="px-3 py-2 text-center font-medium">Attiva</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="loc in locations" :key="loc.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
                <td class="px-3 py-2 font-mono text-xs">{{ loc.barcode }}</td>
                <td class="px-3 py-2">{{ loc.location_type }}</td>
                <td class="px-3 py-2">{{ loc.aisle }}</td>
                <td class="px-3 py-2">{{ loc.rack }}</td>
                <td class="px-3 py-2">{{ loc.level }}</td>
                <td class="px-3 py-2">{{ loc.position }}</td>
                <td class="px-3 py-2 text-right">{{ loc.max_weight_kg || '-' }}</td>
                <td class="px-3 py-2 text-center">
                  <span class="w-2 h-2 rounded-full inline-block" :class="loc.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="locations.length === 0" class="text-center text-gray-400 py-6 text-sm">Nessuna ubicazione</div>
        </div>
      </div>
    </div>

    <!-- Warehouse form modal -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">{{ editingWarehouse ? 'Modifica' : 'Nuovo' }} Magazzino</h3>
        <form @submit.prevent="saveWarehouse" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Codice *</label><input v-model="form.code" class="input-field w-full" required /></div>
            <div><label class="label">Nome *</label><input v-model="form.name" class="input-field w-full" required /></div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Tipo</label>
              <select v-model="form.warehouse_type" class="input-field w-full">
                <option value="standard">Standard</option><option value="cold_storage">Cella frigo</option><option value="hazmat">Pericoloso</option><option value="cross_dock">Cross-dock</option>
              </select>
            </div>
            <div><label class="label">Capacità m³</label><input v-model.number="form.total_capacity_m3" class="input-field w-full" type="number" step="0.01" /></div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Indirizzo</label><input v-model="form.address" class="input-field w-full" /></div>
            <div><label class="label">Città</label><input v-model="form.city" class="input-field w-full" /></div>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Salva</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Zone form modal -->
    <div v-if="showZoneForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showZoneForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuova Zona</h3>
        <form @submit.prevent="saveZone" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Codice *</label><input v-model="zoneForm.code" class="input-field w-full" required /></div>
            <div><label class="label">Nome *</label><input v-model="zoneForm.name" class="input-field w-full" required /></div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Tipo Zona</label>
              <select v-model="zoneForm.zone_type" class="input-field w-full">
                <option value="storage">Stoccaggio</option><option value="receiving">Ricezione</option><option value="shipping">Spedizione</option><option value="staging">Staging</option><option value="picking">Picking</option><option value="packing">Imballaggio</option>
              </select>
            </div>
            <div><label class="label">Picking</label>
              <select v-model="zoneForm.picking_strategy" class="input-field w-full">
                <option value="">-</option><option value="single">Single</option><option value="batch">Batch</option><option value="zone">Zone</option>
              </select>
            </div>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showZoneForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Salva</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Location form modal -->
    <div v-if="showLocationForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showLocationForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuova Ubicazione</h3>
        <form @submit.prevent="saveLocation" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Barcode *</label><input v-model="locationForm.barcode" class="input-field w-full" required /></div>
            <div><label class="label">Tipo</label>
              <select v-model="locationForm.location_type" class="input-field w-full">
                <option value="shelf">Scaffale</option><option value="bin">Bin</option><option value="floor">Pavimento</option><option value="pallet">Pallet</option><option value="bulk">Bulk</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-3">
            <div><label class="label">Corsia</label><input v-model="locationForm.aisle" class="input-field w-full" /></div>
            <div><label class="label">Scaffale</label><input v-model="locationForm.rack" class="input-field w-full" /></div>
            <div><label class="label">Livello</label><input v-model="locationForm.level" class="input-field w-full" /></div>
            <div><label class="label">Posizione</label><input v-model="locationForm.position" class="input-field w-full" /></div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Capacità kg</label><input v-model.number="locationForm.max_weight_kg" class="input-field w-full" type="number" step="0.01" /></div>
            <div><label class="label">Volume m³</label><input v-model.number="locationForm.max_volume_m3" class="input-field w-full" type="number" step="0.01" /></div>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showLocationForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Salva</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/api'

const warehouses = ref([])
const selected = ref(null)
const zones = ref([])
const selectedZone = ref(null)
const locations = ref([])

const showForm = ref(false)
const showZoneForm = ref(false)
const showLocationForm = ref(false)
const editingWarehouse = ref(null)

const form = ref({ code: '', name: '', warehouse_type: 'standard', total_capacity_m3: null, address: '', city: '' })
const zoneForm = ref({ code: '', name: '', zone_type: 'storage', picking_strategy: '' })
const locationForm = ref({ barcode: '', location_type: 'shelf', aisle: '', rack: '', level: '', position: '', max_weight_kg: null, max_volume_m3: null })

async function load() {
  const { data } = await api.get('/warehouses')
  warehouses.value = data
}

async function selectWarehouse(w) {
  selected.value = w
  selectedZone.value = null
  locations.value = []
  const { data } = await api.get(`/warehouses/${w.id}/zones`)
  zones.value = data
}

async function selectZone(z) {
  selectedZone.value = z
  const { data } = await api.get(`/warehouses/${selected.value.id}/zones/${z.id}/locations`)
  locations.value = data
}

function editWarehouse(w) {
  editingWarehouse.value = w
  form.value = { code: w.code, name: w.name, warehouse_type: w.warehouse_type || 'standard', total_capacity_m3: w.total_capacity_m3, address: w.address || '', city: w.city || '' }
  showForm.value = true
}

async function saveWarehouse() {
  if (editingWarehouse.value) {
    await api.put(`/warehouses/${editingWarehouse.value.id}`, form.value)
  } else {
    await api.post('/warehouses', form.value)
  }
  showForm.value = false
  editingWarehouse.value = null
  form.value = { code: '', name: '', warehouse_type: 'standard', total_capacity_m3: null, address: '', city: '' }
  await load()
}

async function deleteWarehouse(w) {
  if (!confirm(`Eliminare magazzino "${w.name}"?`)) return
  await api.delete(`/warehouses/${w.id}`)
  if (selected.value?.id === w.id) { selected.value = null; zones.value = [] }
  await load()
}

async function saveZone() {
  await api.post(`/warehouses/${selected.value.id}/zones`, zoneForm.value)
  showZoneForm.value = false
  zoneForm.value = { code: '', name: '', zone_type: 'storage', picking_strategy: '' }
  await selectWarehouse(selected.value)
}

async function saveLocation() {
  await api.post(`/warehouses/${selected.value.id}/zones/${selectedZone.value.id}/locations`, locationForm.value)
  showLocationForm.value = false
  locationForm.value = { barcode: '', location_type: 'shelf', aisle: '', rack: '', level: '', position: '', max_weight_kg: null, max_volume_m3: null }
  await selectZone(selectedZone.value)
}

onMounted(load)
</script>
