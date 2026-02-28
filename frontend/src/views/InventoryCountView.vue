<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Inventario & Conteggi</h1>
      <button @click="showCreateForm = true" class="btn-primary text-center">+ Nuovo Conteggio</button>
    </div>

    <div class="card mb-4">
      <div class="p-4 flex flex-wrap gap-3 items-center">
        <select v-model="statusFilter" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutti gli stati</option>
          <option value="pianificato">Pianificato</option>
          <option value="in_corso">In corso</option>
          <option value="completato">Completato</option>
          <option value="annullato">Annullato</option>
        </select>
        <select v-model="typeFilter" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutti i tipi</option>
          <option value="full">Completo</option>
          <option value="cycle">Ciclico</option>
          <option value="spot">Spot</option>
        </select>
      </div>
    </div>

    <!-- Cycle counts list -->
    <div class="space-y-4 mb-8">
      <div v-for="cc in filteredCounts" :key="cc.id" class="card overflow-hidden">
        <div class="p-4 flex items-center justify-between cursor-pointer" @click="toggleCount(cc.id)">
          <div class="flex items-center gap-3">
            <span class="badge text-xs" :class="ccStatusClass(cc.status)">{{ ccStatusLabel(cc.status) }}</span>
            <span class="font-semibold">Conteggio #{{ cc.id }}</span>
            <span class="badge text-xs bg-gray-100 dark:bg-gray-700 text-gray-600">{{ cc.count_type }}</span>
          </div>
          <div class="flex items-center gap-4 text-sm text-gray-500">
            <span>{{ cc.items?.length || 0 }} righe</span>
            <span>{{ formatDate(cc.created_at) }}</span>
            <svg class="w-4 h-4 transition-transform" :class="expanded.has(cc.id) ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
          </div>
        </div>

        <div v-if="expanded.has(cc.id)" class="border-t border-gray-200 dark:border-gray-700">
          <div class="p-4 flex gap-2">
            <button v-if="cc.status === 'pianificato'" @click="startCount(cc)" class="text-xs btn-primary">Inizia</button>
            <button v-if="cc.status === 'in_corso'" @click="openSubmitModal(cc)" class="text-xs btn-primary bg-green-600 hover:bg-green-700">Invia Conteggi</button>
          </div>

          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-2 text-left font-medium">Ubicazione</th>
                <th class="px-4 py-2 text-left font-medium">Prodotto</th>
                <th class="px-4 py-2 text-right font-medium">Qtà sistema</th>
                <th class="px-4 py-2 text-right font-medium">Qtà contata</th>
                <th class="px-4 py-2 text-right font-medium">Diff</th>
                <th class="px-4 py-2 text-left font-medium">Stato</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="it in cc.items" :key="it.id" :class="it.discrepancy && it.discrepancy !== 0 ? 'bg-yellow-50 dark:bg-yellow-900/10' : ''">
                <td class="px-4 py-2">Loc #{{ it.location_id }}</td>
                <td class="px-4 py-2">Prod #{{ it.product_id }}</td>
                <td class="px-4 py-2 text-right">{{ it.system_quantity }}</td>
                <td class="px-4 py-2 text-right font-mono">{{ it.counted_quantity ?? '-' }}</td>
                <td class="px-4 py-2 text-right font-mono" :class="it.discrepancy > 0 ? 'text-green-600' : it.discrepancy < 0 ? 'text-red-600' : ''">
                  {{ it.discrepancy != null ? (it.discrepancy > 0 ? '+' : '') + it.discrepancy : '-' }}
                </td>
                <td class="px-4 py-2"><span class="badge text-xs" :class="itemStatusClass(it.status)">{{ it.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-if="filteredCounts.length === 0" class="text-center text-gray-400 py-8 card">Nessun conteggio trovato</div>

    <!-- Quality checks -->
    <div class="card p-5">
      <h2 class="text-lg font-semibold mb-4">Controlli Qualità</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[600px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-3 py-2 text-left font-medium">ID</th>
              <th class="px-3 py-2 text-left font-medium">Prodotto</th>
              <th class="px-3 py-2 text-left font-medium">Tipo</th>
              <th class="px-3 py-2 text-left font-medium">Risultato</th>
              <th class="px-3 py-2 text-left font-medium">Note</th>
              <th class="px-3 py-2 text-left font-medium">Data</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="qc in qualityChecks" :key="qc.id">
              <td class="px-3 py-2">#{{ qc.id }}</td>
              <td class="px-3 py-2">Prod #{{ qc.product_id }}</td>
              <td class="px-3 py-2">{{ qc.check_type }}</td>
              <td class="px-3 py-2">
                <span class="badge text-xs" :class="qc.result === 'pass' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">{{ qc.result }}</span>
              </td>
              <td class="px-3 py-2 text-xs text-gray-500">{{ qc.notes || '-' }}</td>
              <td class="px-3 py-2 text-xs">{{ formatDate(qc.created_at) }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="qualityChecks.length === 0" class="text-center text-gray-400 py-4 text-sm">Nessun controllo qualità</div>
      </div>
    </div>

    <!-- Create count modal -->
    <div v-if="showCreateForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showCreateForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuovo Conteggio</h3>
        <form @submit.prevent="createCount" class="space-y-4">
          <div>
            <label class="label">Magazzino *</label>
            <input v-model.number="createForm.warehouse_id" class="input-field w-full" type="number" required />
          </div>
          <div>
            <label class="label">Tipo</label>
            <select v-model="createForm.count_type" class="input-field w-full">
              <option value="cycle">Ciclico</option>
              <option value="full">Completo</option>
              <option value="spot">Spot</option>
            </select>
          </div>
          <div>
            <label class="label">ID Zona (opzionale)</label>
            <input v-model.number="createForm.zone_id" class="input-field w-full" type="number" />
          </div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showCreateForm = false" class="btn-secondary">Annulla</button>
            <button type="submit" class="btn-primary">Crea</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Submit counts modal -->
    <div v-if="submitModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="submitModal = null">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">Invia Conteggi — #{{ submitModal.id }}</h3>
        <div class="space-y-3">
          <div v-for="it in submitModal.items" :key="it.id" class="border border-gray-200 dark:border-gray-700 rounded p-3">
            <p class="text-sm mb-2">Loc #{{ it.location_id }} • Prod #{{ it.product_id }} • Sistema: {{ it.system_quantity }}</p>
            <input v-model.number="it._counted" class="input-field w-full" type="number" :placeholder="`Contati (sistema: ${it.system_quantity})`" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-4">
          <button @click="submitModal = null" class="btn-secondary">Annulla</button>
          <button @click="submitCounts" class="btn-primary">Conferma</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/api'

const cycleCounts = ref([])
const qualityChecks = ref([])
const statusFilter = ref('')
const typeFilter = ref('')
const expanded = ref(new Set())
const showCreateForm = ref(false)
const submitModal = ref(null)

const createForm = ref({ warehouse_id: null, count_type: 'cycle', zone_id: null })

const filteredCounts = computed(() => {
  return cycleCounts.value.filter(c => {
    if (statusFilter.value && c.status !== statusFilter.value) return false
    if (typeFilter.value && c.count_type !== typeFilter.value) return false
    return true
  })
})

function toggleCount(id) {
  if (expanded.value.has(id)) expanded.value.delete(id)
  else expanded.value.add(id)
}

async function load() {
  const { data } = await api.get('/inventory/cycle-counts')
  cycleCounts.value = data

  try {
    const { data: qc } = await api.get('/inventory/quality-checks')
    qualityChecks.value = qc
  } catch { qualityChecks.value = [] }
}

async function createCount() {
  await api.post('/inventory/cycle-counts', createForm.value)
  showCreateForm.value = false
  createForm.value = { warehouse_id: null, count_type: 'cycle', zone_id: null }
  await load()
}

async function startCount(cc) {
  await api.post(`/inventory/cycle-counts/${cc.id}/start`)
  await load()
}

function openSubmitModal(cc) {
  submitModal.value = {
    ...cc,
    items: (cc.items || []).map(i => ({ ...i, _counted: i.counted_quantity ?? i.system_quantity }))
  }
}

async function submitCounts() {
  const items_data = submitModal.value.items.map(i => ({
    item_id: i.id,
    counted_quantity: i._counted,
  }))
  await api.post(`/inventory/cycle-counts/${submitModal.value.id}/submit`, { items: items_data })
  submitModal.value = null
  await load()
}

const ccStatusMap = {
  pianificato: { label: 'Pianificato', class: 'bg-gray-100 text-gray-700' },
  in_corso: { label: 'In corso', class: 'bg-blue-100 text-blue-700' },
  completato: { label: 'Completato', class: 'bg-green-100 text-green-700' },
  annullato: { label: 'Annullato', class: 'bg-red-100 text-red-700' },
}
function ccStatusLabel(s) { return ccStatusMap[s]?.label || s }
function ccStatusClass(s) { return ccStatusMap[s]?.class || '' }

function itemStatusClass(s) {
  const m = { pending: 'bg-gray-100 text-gray-600', counted: 'bg-blue-100 text-blue-700', verified: 'bg-green-100 text-green-700' }
  return m[s] || ''
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('it-IT') : '-' }

onMounted(load)
</script>
