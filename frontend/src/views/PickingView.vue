<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Picking</h1>
      <button @click="showCreateWave = true" class="btn-primary text-center">+ Crea Wave</button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <div class="card p-4">
        <p class="text-xs text-gray-500">Waves attive</p>
        <p class="text-2xl font-bold text-blue-600">{{ wavesActive }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Task in corso</p>
        <p class="text-2xl font-bold text-amber-600">{{ tasksInProgress }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Task completati oggi</p>
        <p class="text-2xl font-bold text-green-600">{{ tasksCompletedToday }}</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500">Task in attesa</p>
        <p class="text-2xl font-bold text-gray-600">{{ tasksPending }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card mb-4">
      <div class="p-4 flex flex-wrap gap-3 items-center">
        <select v-model="waveFilter" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutte le waves</option>
          <option value="creato">Create</option>
          <option value="in_corso">In corso</option>
          <option value="completato">Completate</option>
        </select>
        <select v-model="typeFilter" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutti i tipi</option>
          <option value="single">Single</option>
          <option value="batch">Batch</option>
          <option value="wave">Wave</option>
          <option value="zone">Zone</option>
        </select>
      </div>
    </div>

    <!-- Waves list -->
    <div class="space-y-4">
      <div v-for="wave in filteredWaves" :key="wave.id" class="card overflow-hidden">
        <div class="p-4 flex items-center justify-between cursor-pointer" @click="toggleWave(wave.id)">
          <div class="flex items-center gap-3">
            <span class="badge text-xs" :class="waveStatusClass(wave.status)">{{ waveStatusLabel(wave.status) }}</span>
            <span class="font-semibold">Wave #{{ wave.id }}</span>
            <span class="badge text-xs bg-gray-100 dark:bg-gray-700 text-gray-600">{{ wave.wave_type }}</span>
            <span class="badge text-xs" :class="priorityClass(wave.priority)">P{{ wave.priority }}</span>
          </div>
          <div class="flex items-center gap-4 text-sm text-gray-500">
            <span>{{ wave.tasks?.length || 0 }} task</span>
            <svg class="w-4 h-4 transition-transform" :class="expandedWaves.has(wave.id) ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </div>
        </div>

        <!-- Tasks -->
        <div v-if="expandedWaves.has(wave.id)" class="border-t border-gray-200 dark:border-gray-700">
          <div class="p-4 flex gap-2 items-center">
            <button v-if="wave.status === 'creato'" @click="startWave(wave)" class="text-xs btn-primary">Avvia Wave</button>
            <button v-if="wave.status === 'in_corso'" @click="completeWave(wave)" class="text-xs btn-primary bg-green-600 hover:bg-green-700">Completa Wave</button>
          </div>
          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-2 text-left font-medium">Task</th>
                <th class="px-4 py-2 text-left font-medium">Prodotto</th>
                <th class="px-4 py-2 text-left font-medium">Ubicazione</th>
                <th class="px-4 py-2 text-right font-medium">Qtà</th>
                <th class="px-4 py-2 text-left font-medium">Stato</th>
                <th class="px-4 py-2 text-center font-medium">Azioni</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="task in wave.tasks" :key="task.id">
                <td class="px-4 py-2">#{{ task.sequence }}</td>
                <td class="px-4 py-2">Prodotto #{{ task.product_id }}</td>
                <td class="px-4 py-2 font-mono text-xs">Loc #{{ task.source_location_id || '-' }}</td>
                <td class="px-4 py-2 text-right">{{ task.quantity }}</td>
                <td class="px-4 py-2">
                  <span class="badge text-xs" :class="taskStatusClass(task.status)">{{ task.status }}</span>
                </td>
                <td class="px-4 py-2 text-center">
                  <button v-if="task.status === 'assegnato'" @click="startTask(wave, task)" class="text-xs text-blue-600 hover:underline mr-2">Inizia</button>
                  <button v-if="task.status === 'in_corso'" @click="confirmTask(wave, task)" class="text-xs text-green-600 hover:underline">Conferma</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="!wave.tasks?.length" class="text-center text-gray-400 text-sm py-4">Nessun task generato</div>
        </div>
      </div>
    </div>

    <div v-if="filteredWaves.length === 0" class="text-center text-gray-400 py-8 card">Nessuna picking wave trovata</div>

    <!-- Create wave modal -->
    <div v-if="showCreateWave" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showCreateWave = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Crea Picking Wave</h3>
        <form @submit.prevent="createWave" class="space-y-4">
          <div>
            <label class="label">Tipo di picking</label>
            <select v-model="waveForm.wave_type" class="input-field w-full">
              <option value="single">Single pick</option>
              <option value="batch">Batch pick</option>
              <option value="wave">Wave pick</option>
              <option value="zone">Zone pick</option>
            </select>
          </div>
          <div>
            <label class="label">Priorità</label>
            <select v-model.number="waveForm.priority" class="input-field w-full">
              <option :value="1">1 - Bassa</option>
              <option :value="2">2 - Media</option>
              <option :value="3">3 - Alta</option>
              <option :value="4">4 - Urgente</option>
              <option :value="5">5 - Critica</option>
            </select>
          </div>
          <div>
            <label class="label">ID Ordini (separati da virgola)</label>
            <input v-model="waveForm.order_ids_str" class="input-field w-full" placeholder="1, 2, 3" />
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showCreateWave = false" class="btn-secondary">Annulla</button>
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

const waves = ref([])
const waveFilter = ref('')
const typeFilter = ref('')
const expandedWaves = ref(new Set())
const showCreateWave = ref(false)
const waveForm = ref({ wave_type: 'single', priority: 2, order_ids_str: '' })

const filteredWaves = computed(() => {
  return waves.value.filter(w => {
    if (waveFilter.value && w.status !== waveFilter.value) return false
    if (typeFilter.value && w.wave_type !== typeFilter.value) return false
    return true
  })
})

const wavesActive = computed(() => waves.value.filter(w => w.status === 'in_corso').length)
const tasksInProgress = computed(() => waves.value.flatMap(w => w.tasks || []).filter(t => t.status === 'in_corso').length)
const tasksCompletedToday = computed(() => waves.value.flatMap(w => w.tasks || []).filter(t => t.status === 'completato').length)
const tasksPending = computed(() => waves.value.flatMap(w => w.tasks || []).filter(t => t.status === 'assegnato').length)

function toggleWave(id) {
  if (expandedWaves.value.has(id)) expandedWaves.value.delete(id)
  else expandedWaves.value.add(id)
}

async function load() {
  const params = {}
  if (waveFilter.value) params.status = waveFilter.value
  const { data } = await api.get('/picking/waves', { params })
  waves.value = data
}

async function createWave() {
  const order_ids = waveForm.value.order_ids_str.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))
  await api.post('/picking/waves', {
    wave_type: waveForm.value.wave_type,
    priority: waveForm.value.priority,
    order_ids: order_ids,
  })
  showCreateWave.value = false
  waveForm.value = { wave_type: 'single', priority: 2, order_ids_str: '' }
  await load()
}

async function startWave(wave) {
  // Start all assigned tasks -> status change
  for (const task of (wave.tasks || []).filter(t => t.status === 'assegnato')) {
    await api.post(`/picking/waves/${wave.id}/tasks/${task.id}/start`)
  }
  await load()
}

async function completeWave(wave) {
  if (!confirm('Completare questa wave?')) return
  // Confirm remaining in_corso tasks
  for (const task of (wave.tasks || []).filter(t => t.status === 'in_corso')) {
    await api.post(`/picking/waves/${wave.id}/tasks/${task.id}/confirm`, { picked_quantity: task.quantity })
  }
  await load()
}

async function startTask(wave, task) {
  await api.post(`/picking/waves/${wave.id}/tasks/${task.id}/start`)
  await load()
}

async function confirmTask(wave, task) {
  const qty = prompt(`Quantità prelevata (attesa: ${task.quantity}):`, task.quantity)
  if (qty === null) return
  await api.post(`/picking/waves/${wave.id}/tasks/${task.id}/confirm`, { picked_quantity: parseInt(qty) })
  await load()
}

const waveStatusMap = {
  creato: { label: 'Creato', class: 'bg-gray-100 text-gray-700' },
  in_corso: { label: 'In corso', class: 'bg-blue-100 text-blue-700' },
  completato: { label: 'Completato', class: 'bg-green-100 text-green-700' },
  annullato: { label: 'Annullato', class: 'bg-red-100 text-red-700' },
}
function waveStatusLabel(s) { return waveStatusMap[s]?.label || s }
function waveStatusClass(s) { return waveStatusMap[s]?.class || '' }

function taskStatusClass(s) {
  const m = { assegnato: 'bg-gray-100 text-gray-700', in_corso: 'bg-blue-100 text-blue-700', completato: 'bg-green-100 text-green-700', errore: 'bg-red-100 text-red-700' }
  return m[s] || ''
}

function priorityClass(p) {
  if (p >= 4) return 'bg-red-100 text-red-700'
  if (p >= 3) return 'bg-amber-100 text-amber-700'
  return 'bg-gray-100 text-gray-600'
}

onMounted(load)
</script>
