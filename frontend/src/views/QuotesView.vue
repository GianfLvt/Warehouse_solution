<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Preventivi</h1>
      <router-link to="/quotes/new" class="btn-primary text-center">+ Nuovo Preventivo</router-link>
    </div>

    <div class="card mb-4">
      <div class="p-4">
        <select v-model="statusFilter" class="input-field w-full sm:max-w-[200px]">
          <option value="">Tutti gli stati</option>
          <option value="bozza">Bozza</option>
          <option value="inviato">Inviato</option>
          <option value="accettato">Accettato</option>
          <option value="rifiutato">Rifiutato</option>
        </select>
      </div>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm min-w-[600px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">#</th>
            <th class="px-4 py-3 text-left font-medium">Cliente</th>
            <th class="px-4 py-3 text-center font-medium">Articoli</th>
            <th class="px-4 py-3 text-right font-medium">Totale</th>
            <th class="px-4 py-3 text-center font-medium">Stato</th>
            <th class="px-4 py-3 text-left font-medium">Data</th>
            <th class="px-4 py-3 text-center font-medium">Azioni</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="q in quotes" :key="q.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3 font-medium">{{ q.id }}</td>
            <td class="px-4 py-3">{{ q.customer?.contact_name || '-' }}</td>
            <td class="px-4 py-3 text-center">{{ q.items?.length || 0 }}</td>
            <td class="px-4 py-3 text-right">€ {{ quoteTotal(q).toFixed(2) }}</td>
            <td class="px-4 py-3 text-center">
              <span :class="statusClass(q.status)" class="badge">{{ q.status }}</span>
            </td>
            <td class="px-4 py-3">{{ formatDate(q.created_at) }}</td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <button v-if="q.status !== 'accettato'" @click="convertToOrder(q)" class="text-primary-600 hover:underline text-xs">→ Ordine</button>
                <button @click="deleteQuote(q)" class="text-red-500 hover:underline text-xs">Elimina</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="quotes.length === 0" class="text-center text-gray-400 py-8">Nessun preventivo</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/composables/api'

const router = useRouter()
const quotes = ref([])
const statusFilter = ref('')

async function load() {
  const params = {}
  if (statusFilter.value) params.status = statusFilter.value
  const { data } = await api.get('/quotes', { params })
  quotes.value = data
}

function quoteTotal(q) {
  return (q.items || []).reduce((s, i) => s + i.quantity * i.unit_price, 0)
}

async function convertToOrder(q) {
  if (!confirm(`Convertire preventivo #${q.id} in ordine?`)) return
  const { data } = await api.post(`/quotes/${q.id}/convert`)
  router.push(`/orders/${data.order_id}`)
}

async function deleteQuote(q) {
  if (!confirm(`Eliminare preventivo #${q.id}?`)) return
  await api.delete(`/quotes/${q.id}`)
  await load()
}

const statusClasses = {
  bozza: 'bg-gray-100 dark:bg-gray-700 text-gray-600',
  inviato: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700',
  accettato: 'bg-green-100 dark:bg-green-900/30 text-green-700',
  rifiutato: 'bg-red-100 dark:bg-red-900/30 text-red-700',
}
function statusClass(s) { return statusClasses[s] || '' }
function formatDate(d) { return new Date(d).toLocaleDateString('it-IT') }

watch(statusFilter, load)
onMounted(load)
</script>
