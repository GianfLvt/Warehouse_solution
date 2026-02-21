<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Ordini Clienti</h1>
      <router-link to="/orders/new" class="btn-primary text-center">+ Nuovo Ordine</router-link>
    </div>

    <div class="card mb-4">
      <div class="p-4 flex flex-wrap gap-3">
        <select v-model="statusFilter" class="input-field w-full sm:max-w-[200px]">
          <option value="">Tutti gli stati</option>
          <option value="in_lavorazione">In lavorazione</option>
          <option value="in_preparazione">In preparazione</option>
          <option value="pronto">Pronto</option>
          <option value="spedito">Spedito</option>
          <option value="consegnato">Consegnato</option>
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
          <tr v-for="o in orders" :key="o.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3 font-medium">{{ o.id }}</td>
            <td class="px-4 py-3">{{ o.customer?.contact_name || '-' }}</td>
            <td class="px-4 py-3 text-center">{{ o.items?.length || 0 }}</td>
            <td class="px-4 py-3 text-right">€ {{ orderTotal(o).toFixed(2) }}</td>
            <td class="px-4 py-3 text-center">
              <span :class="statusClass(o.status)" class="badge">{{ statusLabel(o.status) }}</span>
            </td>
            <td class="px-4 py-3">{{ formatDate(o.created_at) }}</td>
            <td class="px-4 py-3 text-center">
              <router-link :to="`/orders/${o.id}`" class="text-primary-600 hover:underline text-xs font-medium">Dettaglio</router-link>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="orders.length === 0" class="text-center text-gray-400 py-8">Nessun ordine trovato</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '@/composables/api'

const orders = ref([])
const statusFilter = ref('')

async function load() {
  const params = {}
  if (statusFilter.value) params.status = statusFilter.value
  const { data } = await api.get('/orders', { params })
  orders.value = data
}

function orderTotal(o) {
  return (o.items || []).reduce((sum, i) => sum + i.quantity * i.unit_price, 0)
}

const statusMap = {
  in_lavorazione: { label: 'In lavorazione', class: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' },
  in_preparazione: { label: 'In preparazione', class: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' },
  pronto: { label: 'Pronto', class: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400' },
  spedito: { label: 'Spedito', class: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' },
  consegnato: { label: 'Consegnato', class: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300' },
}
function statusLabel(s) { return statusMap[s]?.label || s }
function statusClass(s) { return statusMap[s]?.class || '' }
function formatDate(d) { return new Date(d).toLocaleDateString('it-IT') }

watch(statusFilter, load)
onMounted(load)
</script>
