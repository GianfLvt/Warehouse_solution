<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-bold">Movimenti Magazzino</h1>
    </div>

    <div class="card p-4 sm:p-5 mb-6">
      <h2 class="text-lg font-semibold mb-4">Registra Movimento</h2>
      <form @submit.prevent="createMovement" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-3 items-end">
        <div>
          <label class="block text-sm font-medium mb-1">Prodotto *</label>
          <div class="flex flex-col sm:flex-row gap-2">
            <select v-model.number="newMov.product_id" class="input-field" required>
              <option value="">Seleziona...</option>
              <option v-for="p in products" :key="p.id" :value="p.id">{{ p.sku }} - {{ p.name }}</option>
            </select>
            <BarcodeScanner button-class="btn-secondary flex items-center gap-1 text-xs whitespace-nowrap justify-center" @scanned="onScanMovement" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Tipo *</label>
          <select v-model="newMov.movement_type" class="input-field" required>
            <option value="carico">Carico</option>
            <option value="scarico">Scarico</option>
            <option value="trasferimento">Trasferimento</option>
            <option value="reso">Reso</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Quantità *</label>
          <input v-model.number="newMov.quantity" type="number" min="1" class="input-field" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Note</label>
          <input v-model="newMov.notes" class="input-field" />
        </div>
        <button type="submit" class="btn-primary">Registra</button>
      </form>
    </div>

    <div class="card overflow-x-auto">
      <div class="p-4 flex gap-3">
        <select v-model.number="filterProduct" class="input-field w-full sm:max-w-xs">
          <option value="">Tutti i prodotti</option>
          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.sku }} - {{ p.name }}</option>
        </select>
        <select v-model="filterType" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutti i tipi</option>
          <option value="carico">Carico</option>
          <option value="scarico">Scarico</option>
          <option value="trasferimento">Trasferimento</option>
          <option value="reso">Reso</option>
        </select>
      </div>

      <table class="w-full text-sm min-w-[500px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">Data</th>
            <th class="px-4 py-3 text-left font-medium">Prodotto</th>
            <th class="px-4 py-3 text-left font-medium">Tipo</th>
            <th class="px-4 py-3 text-right font-medium">Quantità</th>
            <th class="px-4 py-3 text-left font-medium">Note</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="m in movements" :key="m.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3">{{ formatDate(m.created_at) }}</td>
            <td class="px-4 py-3">{{ productName(m.product_id) }}</td>
            <td class="px-4 py-3">
              <span :class="typeClass(m.movement_type)" class="badge">{{ m.movement_type }}</span>
            </td>
            <td class="px-4 py-3 text-right font-medium">{{ m.quantity }}</td>
            <td class="px-4 py-3 text-gray-500">{{ m.notes || '-' }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="movements.length === 0" class="text-center text-gray-400 py-8">Nessun movimento</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '@/composables/api'
import BarcodeScanner from '@/components/BarcodeScanner.vue'

const products = ref([])
const movements = ref([])
const filterProduct = ref('')
const filterType = ref('')

const newMov = ref({ product_id: '', movement_type: 'carico', quantity: 1, notes: '' })

async function loadProducts() {
  const { data } = await api.get('/products')
  products.value = data
}

async function loadMovements() {
  const params = {}
  if (filterProduct.value) params.product_id = filterProduct.value
  if (filterType.value) params.movement_type = filterType.value
  const { data } = await api.get('/stock-movements', { params })
  movements.value = data
}

async function createMovement() {
  await api.post('/stock-movements', newMov.value)
  newMov.value = { product_id: '', movement_type: 'carico', quantity: 1, notes: '' }
  await Promise.all([loadMovements(), loadProducts()])
}

function productName(id) {
  const p = products.value.find(x => x.id === id)
  return p ? `${p.sku} - ${p.name}` : `#${id}`
}

function formatDate(d) { return new Date(d).toLocaleString('it-IT') }

const typeClasses = {
  carico: 'bg-green-100 dark:bg-green-900/30 text-green-700',
  scarico: 'bg-red-100 dark:bg-red-900/30 text-red-700',
  trasferimento: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700',
  reso: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700',
}
function typeClass(t) { return typeClasses[t] || '' }

async function onScanMovement(code) {
  try {
    const { data } = await api.get(`/products/lookup/${encodeURIComponent(code)}`)
    newMov.value.product_id = data.id
  } catch {
    alert('Prodotto non trovato per questo codice')
  }
}

watch([filterProduct, filterType], loadMovements)
onMounted(() => { loadProducts(); loadMovements() })
</script>
