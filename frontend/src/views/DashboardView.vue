<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Dashboard</h1>

    <div class="grid grid-cols-2 md:grid-cols-3 gap-3 sm:gap-4 mb-8">
      <div class="card p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Ordini in attesa</p>
        <p class="text-2xl sm:text-3xl font-bold text-primary-600 mt-1">{{ stats.pending_orders }}</p>
      </div>
      <div class="card p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Spedizioni oggi</p>
        <p class="text-2xl sm:text-3xl font-bold text-green-600 mt-1">{{ stats.daily_shipments }}</p>
      </div>
      <div class="card p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Prodotti sotto scorta</p>
        <p class="text-2xl sm:text-3xl font-bold mt-1" :class="stats.low_stock_products > 0 ? 'text-red-600' : 'text-gray-600'">{{ stats.low_stock_products }}</p>
      </div>
      <div class="card p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Fatturato mensile</p>
        <p class="text-2xl sm:text-3xl font-bold text-emerald-600 mt-1">€ {{ formatNumber(stats.monthly_revenue) }}</p>
      </div>
      <div class="card p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Totale prodotti</p>
        <p class="text-2xl sm:text-3xl font-bold text-purple-600 mt-1">{{ stats.total_products }}</p>
      </div>
      <div class="card p-4 sm:p-5">
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Totale clienti</p>
        <p class="text-2xl sm:text-3xl font-bold text-blue-600 mt-1">{{ stats.total_customers }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Prodotti sotto scorta</h2>
        <div v-if="lowStock.length === 0" class="text-gray-400 text-sm py-4 text-center">Nessun prodotto sotto scorta</div>
        <div v-else class="space-y-2">
          <div v-for="p in lowStock" :key="p.id" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
            <div>
              <span class="font-medium text-sm">{{ p.name }}</span>
              <span class="text-xs text-gray-400 ml-2">{{ p.sku }}</span>
            </div>
            <div class="flex items-center gap-3">
              <span class="badge bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">{{ p.quantity }} / {{ p.min_stock }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Ordini recenti</h2>
        <div v-if="recentOrders.length === 0" class="text-gray-400 text-sm py-4 text-center">Nessun ordine</div>
        <div v-else class="space-y-2">
          <div v-for="o in recentOrders" :key="o.id" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
            <div>
              <router-link :to="`/orders/${o.id}`" class="font-medium text-sm text-primary-600 hover:underline">Ordine #{{ o.id }}</router-link>
              <span class="text-xs text-gray-400 ml-2">{{ formatDate(o.created_at) }}</span>
            </div>
            <span :class="statusClass(o.status)" class="badge text-xs">{{ statusLabel(o.status) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/api'

const stats = ref({ pending_orders: 0, daily_shipments: 0, low_stock_products: 0, monthly_revenue: 0, total_products: 0, total_customers: 0 })
const lowStock = ref([])
const recentOrders = ref([])

onMounted(async () => {
  const [s, ls, ro] = await Promise.all([
    api.get('/dashboard/stats'),
    api.get('/dashboard/low-stock'),
    api.get('/dashboard/recent-orders'),
  ])
  stats.value = s.data
  lowStock.value = ls.data
  recentOrders.value = ro.data
})

const statusMap = {
  in_lavorazione: { label: 'In lavorazione', class: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' },
  in_preparazione: { label: 'In preparazione', class: 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400' },
  pronto: { label: 'Pronto', class: 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400' },
  spedito: { label: 'Spedito', class: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' },
  consegnato: { label: 'Consegnato', class: 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300' },
}

function statusLabel(s) { return statusMap[s]?.label || s }
function statusClass(s) { return statusMap[s]?.class || '' }
function formatNumber(n) { return Number(n).toLocaleString('it-IT', { minimumFractionDigits: 2 }) }
function formatDate(d) { return new Date(d).toLocaleDateString('it-IT') }
</script>
