<template>
  <div v-if="order">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold">Ordine #{{ order.id }}</h1>
        <p class="text-sm text-gray-500 mt-1">{{ formatDate(order.created_at) }} - {{ order.customer?.contact_name }}</p>
      </div>
      <div class="flex gap-2">
        <select v-model="newStatus" class="input-field max-w-[200px]">
          <option v-for="s in statuses" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
        <button @click="updateStatus" class="btn-primary whitespace-nowrap" :disabled="newStatus === order.status">Aggiorna Stato</button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="card p-4 sm:p-5 overflow-x-auto">
          <h2 class="text-lg font-semibold mb-4">Articoli</h2>
          <table class="w-full text-sm">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-3 py-2 text-left font-medium">Prodotto</th>
                <th class="px-3 py-2 text-right font-medium">Qtà</th>
                <th class="px-3 py-2 text-right font-medium">Prezzo</th>
                <th class="px-3 py-2 text-right font-medium">Subtotale</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="item in order.items" :key="item.id">
                <td class="px-3 py-2">{{ item.product?.name || '-' }} <span class="text-xs text-gray-400">{{ item.product?.sku }}</span></td>
                <td class="px-3 py-2 text-right">{{ item.quantity }}</td>
                <td class="px-3 py-2 text-right">€ {{ item.unit_price.toFixed(2) }}</td>
                <td class="px-3 py-2 text-right font-medium">€ {{ (item.quantity * item.unit_price).toFixed(2) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="font-bold">
                <td colspan="3" class="px-3 py-2 text-right">Totale</td>
                <td class="px-3 py-2 text-right">€ {{ orderTotal.toFixed(2) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <div class="card p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-semibold">Colli</h2>
            <button @click="showPackageForm = !showPackageForm" class="btn-secondary text-xs">+ Nuovo Collo</button>
          </div>

          <div v-if="showPackageForm" class="mb-4 p-4 bg-gray-50 dark:bg-gray-700/30 rounded-lg space-y-3">
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label class="block text-xs font-medium mb-1">Peso (kg)</label>
                <input v-model.number="pkgForm.weight" type="number" step="0.1" class="input-field" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1">Corriere</label>
                <input v-model="pkgForm.carrier" class="input-field" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1">Tracking</label>
                <input v-model="pkgForm.tracking_number" class="input-field" />
              </div>
            </div>
            <div v-for="(pi, idx) in pkgForm.items" :key="idx" class="flex gap-2 items-end">
              <select v-model.number="pi.product_id" class="input-field flex-1">
                <option value="">Prodotto...</option>
                <option v-for="item in order.items" :key="item.product_id" :value="item.product_id">{{ item.product?.name }}</option>
              </select>
              <input v-model.number="pi.quantity" type="number" min="1" class="input-field w-24" placeholder="Qtà" />
              <button type="button" @click="pkgForm.items.splice(idx, 1)" class="text-red-500 p-1">✕</button>
            </div>
            <div class="flex justify-between">
              <button type="button" @click="pkgForm.items.push({ product_id: '', quantity: 1 })" class="text-primary-600 text-xs">+ Aggiungi prodotto</button>
              <button @click="createPackage" class="btn-primary text-xs">Crea Collo</button>
            </div>
          </div>

          <div v-if="packages.length === 0" class="text-gray-400 text-sm text-center py-4">Nessun collo</div>
          <div v-else class="space-y-3">
            <div v-for="pkg in packages" :key="pkg.id" class="p-3 border border-gray-200 dark:border-gray-600 rounded-lg">
              <div class="flex justify-between text-sm">
                <span class="font-medium">Collo #{{ pkg.id }}</span>
                <span class="text-gray-500">{{ pkg.carrier || '-' }} | {{ pkg.tracking_number || 'No tracking' }}</span>
              </div>
              <div class="text-xs text-gray-400 mt-1">Peso: {{ pkg.weight ? pkg.weight + ' kg' : '-' }} | {{ pkg.items?.length || 0 }} articoli</div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div class="card p-5">
          <h3 class="font-semibold mb-3">Stato</h3>
          <span :class="statusClass(order.status)" class="badge text-sm">{{ statusLabel(order.status) }}</span>
        </div>
        <div class="card p-5" v-if="order.customer">
          <h3 class="font-semibold mb-3">Cliente</h3>
          <p class="text-sm">{{ order.customer.contact_name }}</p>
          <p class="text-sm text-gray-500">{{ order.customer.company_name || '' }}</p>
          <p class="text-sm text-gray-500">{{ order.customer.email || '' }}</p>
        </div>
        <div class="card p-5" v-if="order.notes">
          <h3 class="font-semibold mb-3">Note</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400">{{ order.notes }}</p>
        </div>

        <button @click="deleteOrder" class="btn-danger w-full">Elimina Ordine</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/composables/api'

const route = useRoute()
const router = useRouter()
const order = ref(null)
const packages = ref([])
const newStatus = ref('')
const showPackageForm = ref(false)
const pkgForm = ref({ weight: null, carrier: '', tracking_number: '', items: [{ product_id: '', quantity: 1 }] })

const statuses = [
  { value: 'in_lavorazione', label: 'In lavorazione' },
  { value: 'in_preparazione', label: 'In preparazione' },
  { value: 'pronto', label: 'Pronto' },
  { value: 'spedito', label: 'Spedito' },
  { value: 'consegnato', label: 'Consegnato' },
]

const orderTotal = computed(() => (order.value?.items || []).reduce((s, i) => s + i.quantity * i.unit_price, 0))

const statusMap = {
  in_lavorazione: { label: 'In lavorazione', class: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700' },
  in_preparazione: { label: 'In preparazione', class: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700' },
  pronto: { label: 'Pronto', class: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700' },
  spedito: { label: 'Spedito', class: 'bg-green-100 dark:bg-green-900/30 text-green-700' },
  consegnato: { label: 'Consegnato', class: 'bg-gray-100 dark:bg-gray-700 text-gray-600' },
}
function statusLabel(s) { return statusMap[s]?.label || s }
function statusClass(s) { return statusMap[s]?.class || '' }
function formatDate(d) { return new Date(d).toLocaleString('it-IT') }

async function loadOrder() {
  const { data } = await api.get(`/orders/${route.params.id}`)
  order.value = data
  newStatus.value = data.status
}

async function loadPackages() {
  const { data } = await api.get('/packages', { params: { order_id: route.params.id } })
  packages.value = data
}

async function updateStatus() {
  await api.patch(`/orders/${route.params.id}/status`, { status: newStatus.value })
  await loadOrder()
}

async function createPackage() {
  const payload = { ...pkgForm.value, order_id: Number(route.params.id) }
  payload.items = payload.items.filter(i => i.product_id)
  await api.post('/packages', payload)
  pkgForm.value = { weight: null, carrier: '', tracking_number: '', items: [{ product_id: '', quantity: 1 }] }
  showPackageForm.value = false
  await loadPackages()
}

async function deleteOrder() {
  if (!confirm('Eliminare questo ordine?')) return
  await api.delete(`/orders/${route.params.id}`)
  router.push('/orders')
}

onMounted(() => { loadOrder(); loadPackages() })
</script>
