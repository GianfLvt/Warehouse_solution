<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Clienti</h1>
      <router-link to="/customers/new" class="btn-primary text-center">+ Nuovo Cliente</router-link>
    </div>

    <div class="card mb-4">
      <div class="p-4 flex flex-wrap gap-3">
        <input v-model="search" class="input-field w-full sm:max-w-xs" placeholder="Cerca cliente..." />
        <select v-model="typeFilter" class="input-field w-full sm:max-w-[150px]">
          <option value="">Tutti</option>
          <option value="B2B">B2B</option>
          <option value="B2C">B2C</option>
        </select>
      </div>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm min-w-[600px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">Nome contatto</th>
            <th class="px-4 py-3 text-left font-medium">Azienda</th>
            <th class="px-4 py-3 text-left font-medium">Email</th>
            <th class="px-4 py-3 text-left font-medium">Telefono</th>
            <th class="px-4 py-3 text-center font-medium">Tipo</th>
            <th class="px-4 py-3 text-center font-medium">Azioni</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="c in customers" :key="c.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3 font-medium">{{ c.contact_name }}</td>
            <td class="px-4 py-3">{{ c.company_name || '-' }}</td>
            <td class="px-4 py-3">{{ c.email || '-' }}</td>
            <td class="px-4 py-3">{{ c.phone || '-' }}</td>
            <td class="px-4 py-3 text-center">
              <span class="badge" :class="c.customer_type === 'B2B' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700' : 'bg-gray-100 dark:bg-gray-700 text-gray-600'">{{ c.customer_type }}</span>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-1">
                <router-link :to="`/customers/${c.id}/edit`" class="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                </router-link>
                <button @click="deleteCustomer(c)" class="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded text-red-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="customers.length === 0" class="text-center text-gray-400 py-8">Nessun cliente trovato</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '@/composables/api'

const customers = ref([])
const search = ref('')
const typeFilter = ref('')

async function load() {
  const params = {}
  if (search.value) params.search = search.value
  if (typeFilter.value) params.customer_type = typeFilter.value
  const { data } = await api.get('/customers', { params })
  customers.value = data
}

async function deleteCustomer(c) {
  if (!confirm(`Eliminare "${c.contact_name}"?`)) return
  await api.delete(`/customers/${c.id}`)
  await load()
}

let timer
watch([search, typeFilter], () => { clearTimeout(timer); timer = setTimeout(load, 300) })
onMounted(load)
</script>
