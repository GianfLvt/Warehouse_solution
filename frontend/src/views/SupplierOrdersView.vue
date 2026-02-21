<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Ordini Fornitori</h1>
      <router-link to="/supplier-orders/new" class="btn-primary text-center">+ Nuovo Ordine</router-link>
    </div>

    <div class="card mb-4">
      <div class="p-4">
        <select v-model="statusFilter" class="input-field w-full sm:max-w-[200px]">
          <option value="">Tutti gli stati</option>
          <option value="inviato">Inviato</option>
          <option value="ricevuto">Ricevuto</option>
          <option value="parziale">Parziale</option>
        </select>
      </div>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm min-w-[600px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">#</th>
            <th class="px-4 py-3 text-left font-medium">Fornitore</th>
            <th class="px-4 py-3 text-center font-medium">Articoli</th>
            <th class="px-4 py-3 text-center font-medium">Stato</th>
            <th class="px-4 py-3 text-left font-medium">Data</th>
            <th class="px-4 py-3 text-center font-medium">Azioni</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="o in orders" :key="o.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3 font-medium">{{ o.id }}</td>
            <td class="px-4 py-3">{{ o.supplier }}</td>
            <td class="px-4 py-3 text-center">{{ o.items?.length || 0 }}</td>
            <td class="px-4 py-3 text-center">
              <select v-model="o._status" @change="updateStatus(o)" class="input-field text-xs max-w-[140px]">
                <option value="inviato">Inviato</option>
                <option value="ricevuto">Ricevuto</option>
                <option value="parziale">Parziale</option>
              </select>
            </td>
            <td class="px-4 py-3">{{ formatDate(o.created_at) }}</td>
            <td class="px-4 py-3 text-center">
              <button @click="deleteOrder(o)" class="text-red-500 hover:underline text-xs">Elimina</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="orders.length === 0" class="text-center text-gray-400 py-8">Nessun ordine fornitore</div>
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
  const { data } = await api.get('/supplier-orders', { params })
  orders.value = data.map(o => ({ ...o, _status: o.status }))
}

async function updateStatus(o) {
  await api.patch(`/supplier-orders/${o.id}/status`, { status: o._status })
  await load()
}

async function deleteOrder(o) {
  if (!confirm(`Eliminare ordine fornitore #${o.id}?`)) return
  await api.delete(`/supplier-orders/${o.id}`)
  await load()
}

function formatDate(d) { return new Date(d).toLocaleDateString('it-IT') }

watch(statusFilter, load)
onMounted(load)
</script>
