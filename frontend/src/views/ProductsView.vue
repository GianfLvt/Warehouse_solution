<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Prodotti</h1>
      <router-link to="/products/new" class="btn-primary text-center">+ Nuovo Prodotto</router-link>
    </div>

    <div class="card mb-4">
      <div class="p-4 flex flex-wrap gap-3 items-center">
        <input v-model="search" class="input-field w-full sm:max-w-xs" placeholder="Cerca per nome, SKU o barcode..." />
        <BarcodeScanner @scanned="onBarcodeScan" />
        <select v-model="category" class="input-field w-full sm:max-w-[180px]">
          <option value="">Tutte le categorie</option>
          <option v-for="c in categories" :key="c" :value="c">{{ c }}</option>
        </select>
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="lowStock" class="rounded" />
          Solo sotto scorta
        </label>
      </div>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm min-w-[800px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">SKU</th>
            <th class="px-4 py-3 text-left font-medium">Barcode</th>
            <th class="px-4 py-3 text-left font-medium">Nome</th>
            <th class="px-4 py-3 text-left font-medium">Categoria</th>
            <th class="px-4 py-3 text-right font-medium">Prezzo Acq.</th>
            <th class="px-4 py-3 text-right font-medium">Prezzo Vend.</th>
            <th class="px-4 py-3 text-right font-medium">Qtà</th>
            <th class="px-4 py-3 text-right font-medium">Soglia</th>
            <th class="px-4 py-3 text-left font-medium">Ubicazione</th>
            <th class="px-4 py-3 text-center font-medium">Azioni</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="p in products" :key="p.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3 font-mono text-xs">{{ p.sku }}</td>
            <td class="px-4 py-3 font-mono text-xs">{{ p.barcode || '-' }}</td>
            <td class="px-4 py-3 font-medium">{{ p.name }}</td>
            <td class="px-4 py-3">{{ p.category || '-' }}</td>
            <td class="px-4 py-3 text-right">€ {{ p.purchase_price.toFixed(2) }}</td>
            <td class="px-4 py-3 text-right">€ {{ p.sale_price.toFixed(2) }}</td>
            <td class="px-4 py-3 text-right" :class="p.quantity <= p.min_stock ? 'text-red-600 font-bold' : ''">{{ p.quantity }}</td>
            <td class="px-4 py-3 text-right">{{ p.min_stock }}</td>
            <td class="px-4 py-3 text-xs">{{ formatLocation(p) }}</td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-1">
                <router-link :to="`/products/${p.id}/edit`" class="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                </router-link>
                <button @click="deleteProduct(p)" class="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded text-red-500">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="products.length === 0" class="text-center text-gray-400 py-8">Nessun prodotto trovato</div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/composables/api'
import BarcodeScanner from '@/components/BarcodeScanner.vue'

const router = useRouter()
const products = ref([])
const categories = ref([])
const search = ref('')
const category = ref('')
const lowStock = ref(false)

async function load() {
  const params = {}
  if (search.value) params.search = search.value
  if (category.value) params.category = category.value
  if (lowStock.value) params.low_stock = true
  const { data } = await api.get('/products', { params })
  products.value = data
}

async function loadCategories() {
  const { data } = await api.get('/products/categories')
  categories.value = data
}

async function deleteProduct(p) {
  if (!confirm(`Eliminare "${p.name}"?`)) return
  await api.delete(`/products/${p.id}`)
  await load()
}

function formatLocation(p) {
  const parts = [p.location_aisle, p.location_shelf, p.location_level, p.location_bin].filter(Boolean)
  return parts.length ? parts.join(' / ') : '-'
}

async function onBarcodeScan(code) {
  try {
    const { data } = await api.get(`/products/lookup/${encodeURIComponent(code)}`)
    router.push(`/products/${data.id}/edit`)
  } catch {
    router.push({ path: '/products/new', query: { barcode: code } })
  }
}

let timer
watch([search, category, lowStock], () => {
  clearTimeout(timer)
  timer = setTimeout(load, 300)
})

onMounted(() => { load(); loadCategories() })
</script>
