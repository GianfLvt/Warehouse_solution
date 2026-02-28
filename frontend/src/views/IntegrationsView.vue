<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Integrazioni</h1>

    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <p class="text-sm text-gray-500">Gestisci connessioni ERP, TMS, e-commerce e webhook.</p>
      <button @click="showForm = true" class="btn-primary text-center">+ Nuova Integrazione</button>
    </div>

    <!-- Integration cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
      <div v-for="i in integrations" :key="i.id" class="card p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-2">
            <span class="w-10 h-10 rounded-lg flex items-center justify-center text-white text-sm font-bold" :class="typeColor(i.integration_type)">
              {{ i.integration_type?.charAt(0).toUpperCase() }}
            </span>
            <div>
              <h3 class="font-semibold">{{ i.name }}</h3>
              <p class="text-xs text-gray-400">{{ i.integration_type }}</p>
            </div>
          </div>
          <span class="w-2 h-2 rounded-full" :class="i.is_active ? 'bg-green-500' : 'bg-red-500'"></span>
        </div>
        <p v-if="i.base_url" class="text-xs text-gray-400 truncate mb-2">{{ i.base_url }}</p>
        <p v-if="i.last_sync_at" class="text-xs text-gray-400">Ultimo sync: {{ formatDateTime(i.last_sync_at) }}</p>
        <div class="mt-3 flex gap-2">
          <button @click="viewLogs(i)" class="text-xs text-blue-600 hover:underline">Log</button>
          <button @click="toggleActive(i)" class="text-xs hover:underline" :class="i.is_active ? 'text-amber-600' : 'text-green-600'">
            {{ i.is_active ? 'Disattiva' : 'Attiva' }}
          </button>
          <button @click="deleteIntegration(i)" class="text-xs text-red-500 hover:underline">Elimina</button>
        </div>
      </div>
    </div>

    <div v-if="integrations.length === 0" class="text-center text-gray-400 py-8 card mb-8">Nessuna integrazione configurata</div>

    <!-- Logs -->
    <div v-if="selectedIntegration" class="card p-5 mb-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-lg font-semibold">Log — {{ selectedIntegration.name }}</h2>
        <button @click="selectedIntegration = null" class="text-sm text-gray-400 hover:text-gray-600">Chiudi</button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[600px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-3 py-2 text-left font-medium">Data/Ora</th>
              <th class="px-3 py-2 text-left font-medium">Evento</th>
              <th class="px-3 py-2 text-left font-medium">Direzione</th>
              <th class="px-3 py-2 text-left font-medium">Stato</th>
              <th class="px-3 py-2 text-left font-medium">Messaggio</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="l in logs" :key="l.id" :class="l.status === 'error' ? 'bg-red-50 dark:bg-red-900/10' : ''">
              <td class="px-3 py-2 text-xs">{{ formatDateTime(l.created_at) }}</td>
              <td class="px-3 py-2">{{ l.event_type }}</td>
              <td class="px-3 py-2"><span class="badge text-xs" :class="l.direction === 'inbound' ? 'bg-blue-100 text-blue-700' : 'bg-green-100 text-green-700'">{{ l.direction }}</span></td>
              <td class="px-3 py-2">
                <span class="badge text-xs" :class="l.status === 'success' ? 'bg-green-100 text-green-700' : l.status === 'error' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-600'">{{ l.status }}</span>
              </td>
              <td class="px-3 py-2 text-xs text-gray-500 truncate max-w-xs">{{ l.error_message || '-' }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="logs.length === 0" class="text-center text-gray-400 py-4 text-sm">Nessun log</div>
      </div>
    </div>

    <!-- Webhook events -->
    <div class="card p-5">
      <h2 class="text-lg font-semibold mb-4">Webhook Events</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-sm min-w-[600px]">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-3 py-2 text-left font-medium">Data/Ora</th>
              <th class="px-3 py-2 text-left font-medium">Evento</th>
              <th class="px-3 py-2 text-left font-medium">Risorsa</th>
              <th class="px-3 py-2 text-left font-medium">Stato</th>
              <th class="px-3 py-2 text-right font-medium">Tentativi</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="w in webhooks" :key="w.id">
              <td class="px-3 py-2 text-xs">{{ formatDateTime(w.created_at) }}</td>
              <td class="px-3 py-2">{{ w.event_type }}</td>
              <td class="px-3 py-2 text-xs">{{ w.resource_type }} #{{ w.resource_id }}</td>
              <td class="px-3 py-2">
                <span class="badge text-xs" :class="w.status === 'delivered' ? 'bg-green-100 text-green-700' : w.status === 'failed' ? 'bg-red-100 text-red-700' : 'bg-yellow-100 text-yellow-700'">{{ w.status }}</span>
              </td>
              <td class="px-3 py-2 text-right">{{ w.retry_count }}</td>
            </tr>
          </tbody>
        </table>
        <div v-if="webhooks.length === 0" class="text-center text-gray-400 py-4 text-sm">Nessun webhook</div>
      </div>
    </div>

    <!-- Add integration modal -->
    <div v-if="showForm" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50" @click.self="showForm = false">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-full max-w-lg mx-4">
        <h3 class="text-lg font-semibold mb-4">Nuova Integrazione</h3>
        <form @submit.prevent="createIntegration" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div><label class="label">Nome *</label><input v-model="form.name" class="input-field w-full" required /></div>
            <div><label class="label">Tipo *</label>
              <select v-model="form.integration_type" class="input-field w-full" required>
                <option value="erp">ERP</option>
                <option value="tms">TMS</option>
                <option value="ecommerce">E-Commerce</option>
                <option value="crm">CRM</option>
                <option value="accounting">Contabilità</option>
                <option value="custom">Custom</option>
              </select>
            </div>
          </div>
          <div><label class="label">Base URL</label><input v-model="form.base_url" class="input-field w-full" placeholder="https://..." /></div>
          <div><label class="label">API Key</label><input v-model="form.api_key" class="input-field w-full" type="password" /></div>
          <div class="flex justify-end gap-3">
            <button type="button" @click="showForm = false" class="btn-secondary">Annulla</button>
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

const integrations = ref([])
const logs = ref([])
const webhooks = ref([])
const selectedIntegration = ref(null)
const showForm = ref(false)
const form = ref({ name: '', integration_type: 'erp', base_url: '', api_key: '' })

async function load() {
  const { data } = await api.get('/integrations')
  integrations.value = data

  try {
    const { data: wh } = await api.get('/integrations/webhooks')
    webhooks.value = wh
  } catch { webhooks.value = [] }
}

async function viewLogs(i) {
  selectedIntegration.value = i
  try {
    const { data } = await api.get(`/integrations/${i.id}/logs`)
    logs.value = data
  } catch { logs.value = [] }
}

async function createIntegration() {
  await api.post('/integrations', form.value)
  showForm.value = false
  form.value = { name: '', integration_type: 'erp', base_url: '', api_key: '' }
  await load()
}

async function toggleActive(i) {
  await api.put(`/integrations/${i.id}`, { is_active: !i.is_active })
  await load()
}

async function deleteIntegration(i) {
  if (!confirm(`Eliminare integrazione "${i.name}"?`)) return
  await api.delete(`/integrations/${i.id}`)
  await load()
}

function typeColor(t) {
  const m = { erp: 'bg-blue-600', tms: 'bg-amber-600', ecommerce: 'bg-purple-600', crm: 'bg-green-600', accounting: 'bg-indigo-600', custom: 'bg-gray-600' }
  return m[t] || 'bg-gray-600'
}

function formatDateTime(d) { return d ? new Date(d).toLocaleString('it-IT') : '-' }

onMounted(load)
</script>
