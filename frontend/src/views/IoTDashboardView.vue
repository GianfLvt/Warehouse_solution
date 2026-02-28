<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">IoT Dashboard</h1>

    <!-- Device stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <div class="card p-4">
        <p class="text-xs text-gray-500">Dispositivi attivi</p>
        <p class="text-2xl font-bold text-green-600">{{ devices.filter(d => d.is_active).length }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Totale dispositivi</p>
        <p class="text-2xl font-bold text-blue-600">{{ devices.length }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Letture ultime 24h</p>
        <p class="text-2xl font-bold text-purple-600">{{ recentReadings.length }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Scansioni RFID</p>
        <p class="text-2xl font-bold text-amber-600">{{ rfidScans.length }}</p>
      </div>
    </div>

    <!-- Devices -->
    <div class="card p-5 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Dispositivi IoT</h2>
        <button @click="showDeviceForm = true" class="btn-primary text-sm">+ Nuovo Dispositivo</button>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <div v-for="d in devices" :key="d.id" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="font-medium">{{ d.name }}</span>
            <span class="w-2 h-2 rounded-full" :class="d.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
          </div>
          <p class="text-xs text-gray-400">{{ d.device_type }} — {{ d.device_code }}</p>
          <p v-if="d.zone_id" class="text-xs text-gray-400">Zona: {{ d.zone_id }}</p>
          <p v-if="d.last_seen" class="text-xs text-gray-400 mt-1">Ultimo: {{ formatDateTime(d.last_seen) }}</p>
          <div class="flex gap-2 mt-3">
            <button @click="viewReadings(d)" class="text-xs text-blue-600 hover:underline">Letture</button>
            <button @click="deleteDevice(d)" class="text-xs text-red-500 hover:underline">Elimina</button>
          </div>
        </div>
      </div>
      <div v-if="devices.length === 0" class="text-center text-gray-400 py-4 text-sm">Nessun dispositivo IoT configurato</div>
    </div>

    <!-- Sensor readings chart area / table -->
    <div v-if="selectedDevice" class="card p-5 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Letture — {{ selectedDevice.name }}</h2>
        <button @click="selectedDevice = null" class="text-sm text-gray-400 hover:text-gray-600">Chiudi</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[600px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-3 py-2 text-left font-medium">Data/Ora</th>
              <th class="px-3 py-2 text-left font-medium">Tipo</th>
              <th class="px-3 py-2 text-right font-medium">Valore</th>
              <th class="px-3 py-2 text-left font-medium">Unità</th>
              <th class="px-3 py-2 text-center font-medium">Allarme</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="r in deviceReadings" :key="r.id" :class="r.is_alert ? 'bg-red-50 dark:bg-red-900/10' : ''">
              <td class="px-3 py-2 text-xs">{{ formatDateTime(r.reading_at || r.created_at) }}</td>
              <td class="px-3 py-2">{{ r.reading_type }}</td>
              <td class="px-3 py-2 text-right font-mono">{{ r.value?.toFixed(2) }}</td>
              <td class="px-3 py-2 text-xs">{{ r.unit || '-' }}</td>
              <td class="px-3 py-2 text-center">
                <span v-if="r.is_alert" class="badge bg-red-100 text-red-700 text-xs">Allarme</span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="deviceReadings.length === 0" class="text-center text-gray-400 py-4 text-sm">Nessuna lettura</div>
      </div>
    </div>

    <!-- RFID Scans -->
    <div class="card p-5">
      <h2 class="text-lg font-semibold mb-4">Scansioni RFID recenti</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[600px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-3 py-2 text-left font-medium">Tag EPC</th>
              <th class="px-3 py-2 text-left font-medium">Dispositivo</th>
              <th class="px-3 py-2 text-left font-medium">Ubicazione</th>
              <th class="px-3 py-2 text-left font-medium">Evento</th>
              <th class="px-3 py-2 text-left font-medium">Data/Ora</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="s in rfidScans" :key="s.id">
              <td class="px-3 py-2 font-mono text-xs">{{ s.tag_epc }}</td>
              <td class="px-3 py-2">{{ s.device_id }}</td>
              <td class="px-3 py-2">{{ s.location_id || '-' }}</td>
              <td class="px-3 py-2"><span class="badge text-xs bg-blue-100 text-blue-700">{{ s.event_type }}</span></td>
              <td class="px-3 py-2 text-xs">{{ formatDateTime(s.scanned_at || s.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="rfidScans.length === 0" class="text-center text-gray-400 py-4 text-sm">Nessuna scansione RFID</div>
      </div>
    </div>

    <!-- Real-time events -->
    <div v-if="wsMessages.length > 0" class="card p-5 mt-6">
      <h2 class="text-lg font-semibold mb-3">
        Eventi IoT in tempo reale
        <span class="ml-2 w-2 h-2 rounded-full inline-block" :class="wsConnected ? 'bg-green-500' : 'bg-red-500'"></span>
      </h2>
      <div class="space-y-1 max-h-48 overflow-y-auto">
        <div v-for="(msg, idx) in wsMessages.slice(-15).reverse()" :key="idx" class="text-xs text-gray-500 py-1">
          {{ JSON.stringify(msg) }}
        </div>
      </div>
    </div>

    <!-- Add device modal -->
    <div v-if="showDeviceForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showDeviceForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuovo Dispositivo IoT</h3>
        <form @submit.prevent="createDevice" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Codice *</label><input v-model="deviceForm.device_code" class="input-field w-full" required /></div>
            <div><label class="label">Nome *</label><input v-model="deviceForm.name" class="input-field w-full" required /></div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Tipo</label>
              <select v-model="deviceForm.device_type" class="input-field w-full">
                <option value="temperature_sensor">Sensore temperatura</option>
                <option value="humidity_sensor">Sensore umidità</option>
                <option value="rfid_reader">Lettore RFID</option>
                <option value="barcode_scanner">Scanner barcode</option>
                <option value="weight_sensor">Bilancia</option>
                <option value="camera">Camera</option>
                <option value="gateway">Gateway</option>
              </select>
            </div>
            <div><label class="label">Magazzino</label><input v-model.number="deviceForm.warehouse_id" class="input-field w-full" type="number" /></div>
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showDeviceForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Crea</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/api'
import { useWebSocket } from '@/composables/useWebSocket'

const devices = ref([])
const recentReadings = ref([])
const rfidScans = ref([])
const selectedDevice = ref(null)
const deviceReadings = ref([])
const showDeviceForm = ref(false)

const deviceForm = ref({ device_code: '', name: '', device_type: 'temperature_sensor', warehouse_id: null })

const { messages: wsMessages, connected: wsConnected } = useWebSocket('iot')

async function load() {
  const { data } = await api.get('/iot/devices')
  devices.value = data

  try {
    const { data: scans } = await api.get('/iot/rfid-scans', { params: { limit: 50 } })
    rfidScans.value = scans
  } catch { rfidScans.value = [] }
}

async function viewReadings(d) {
  selectedDevice.value = d
  try {
    const { data } = await api.get(`/iot/devices/${d.id}/readings`, { params: { limit: 50 } })
    deviceReadings.value = data
  } catch { deviceReadings.value = [] }
}

async function createDevice() {
  await api.post('/iot/devices', deviceForm.value)
  showDeviceForm.value = false
  deviceForm.value = { device_code: '', name: '', device_type: 'temperature_sensor', warehouse_id: null }
  await load()
}

async function deleteDevice(d) {
  if (!confirm(`Eliminare dispositivo "${d.name}"?`)) return
  await api.delete(`/iot/devices/${d.id}`)
  await load()
}

function formatDateTime(d) {
  if (!d) return '-'
  return new Date(d).toLocaleString('it-IT')
}

onMounted(load)
</script>
