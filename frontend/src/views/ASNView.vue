<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Ricezione Merce (ASN)</h1>
      <router-link to="/asn/new" class="btn-primary text-center">+ Nuovo ASN</router-link>
    </div>

    <div class="card mb-4">
      <div class="p-4 flex flex-wrap gap-3 items-center">
        <input v-model="search" class="input-field w-full sm:max-w-xs" placeholder="Cerca per numero ASN..." />
        <select v-model="statusFilter" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutti gli stati</option>
          <option value="atteso">Atteso</option>
          <option value="in_arrivo">In arrivo</option>
          <option value="in_ricezione">In ricezione</option>
          <option value="completato">Completato</option>
          <option value="annullato">Annullato</option>
        </select>
      </div>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm min-w-[900px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">Numero ASN</th>
            <th class="px-4 py-3 text-left font-medium">Fornitore</th>
            <th class="px-4 py-3 text-left font-medium">Magazzino</th>
            <th class="px-4 py-3 text-left font-medium">Stato</th>
            <th class="px-4 py-3 text-left font-medium">Arrivo previsto</th>
            <th class="px-4 py-3 text-right font-medium">Righe</th>
            <th class="px-4 py-3 text-center font-medium">Azioni</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="a in filteredAsns" :key="a.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3 font-mono text-xs font-medium">{{ a.asn_number }}</td>
            <td class="px-4 py-3">{{ a.supplier_name || '-' }}</td>
            <td class="px-4 py-3">{{ a.warehouse_id }}</td>
            <td class="px-4 py-3">
              <span class="badge text-xs" :class="asnStatusClass(a.status)">{{ asnStatusLabel(a.status) }}</span>
            </td>
            <td class="px-4 py-3">{{ a.expected_arrival ? formatDate(a.expected_arrival) : '-' }}</td>
            <td class="px-4 py-3 text-right">{{ a.items?.length || 0 }}</td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <button v-if="a.status === 'atteso' || a.status === 'in_arrivo'" @click="startReceiving(a)" class="text-xs text-blue-600 hover:underline">Ricevi</button>
                <button v-if="a.status === 'in_ricezione'" @click="completeAsn(a)" class="text-xs text-green-600 hover:underline">Completa</button>
                <button @click="deleteAsn(a)" class="text-xs text-red-500 hover:underline">Elimina</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredAsns.length === 0" class="text-center text-gray-400 py-8">Nessun ASN trovato</div>
    </div>

    <!-- Receive modal -->
    <div v-if="receivingAsn" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="receivingAsn = null">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-2xl mx-4 max-h-[80vh] overflow-y-auto">
        <h3 class="text-lg font-semibold mb-4">Ricezione ASN {{ receivingAsn.asn_number }}</h3>
        <div class="space-y-3">
          <div v-for="item in receivingAsn.items" :key="item.id" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-sm">Prodotto #{{ item.product_id }}</span>
              <span class="text-xs text-gray-400">Attesi: {{ item.expected_quantity }}</span>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="label text-xs">Quantità ricevuta</label>
                <input v-model.number="item._received" class="input-field w-full" type="number" min="0" />
              </div>
              <div>
                <label class="label text-xs">Note</label>
                <input v-model="item._notes" class="input-field w-full" />
              </div>
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-4">
          <button @click="receivingAsn = null" class="btn-secondary">Annulla</button>
          <button @click="submitReceive" class="btn-primary">Conferma ricezione</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/api'

const asns = ref([])
const search = ref('')
const statusFilter = ref('')
const receivingAsn = ref(null)

const filteredAsns = computed(() => {
  return asns.value.filter(a => {
    if (statusFilter.value && a.status !== statusFilter.value) return false
    if (search.value && !a.asn_number?.toLowerCase().includes(search.value.toLowerCase())) return false
    return true
  })
})

async function load() {
  const params = {}
  if (statusFilter.value) params.status = statusFilter.value
  const { data } = await api.get('/asn', { params })
  asns.value = data
}

function startReceiving(a) {
  receivingAsn.value = {
    ...a,
    items: (a.items || []).map(i => ({ ...i, _received: i.expected_quantity, _notes: '' }))
  }
}

async function submitReceive() {
  for (const item of receivingAsn.value.items) {
    if (item._received > 0) {
      await api.post(`/asn/${receivingAsn.value.id}/items/${item.id}/receive`, {
        received_quantity: item._received,
        notes: item._notes || undefined,
      })
    }
  }
  receivingAsn.value = null
  await load()
}

async function completeAsn(a) {
  if (!confirm(`Completare ASN ${a.asn_number}?`)) return
  await api.post(`/asn/${a.id}/complete`)
  await load()
}

async function deleteAsn(a) {
  if (!confirm(`Eliminare ASN ${a.asn_number}?`)) return
  await api.delete(`/asn/${a.id}`)
  await load()
}

const statusMap = {
  atteso: { label: 'Atteso', class: 'bg-gray-100 text-gray-700' },
  in_arrivo: { label: 'In arrivo', class: 'bg-blue-100 text-blue-700' },
  in_ricezione: { label: 'In ricezione', class: 'bg-yellow-100 text-yellow-700' },
  completato: { label: 'Completato', class: 'bg-green-100 text-green-700' },
  annullato: { label: 'Annullato', class: 'bg-red-100 text-red-700' },
}
function asnStatusLabel(s) { return statusMap[s]?.label || s }
function asnStatusClass(s) { return statusMap[s]?.class || '' }
function formatDate(d) { return new Date(d).toLocaleDateString('it-IT') }

onMounted(load)
</script>
