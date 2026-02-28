<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Dashboard WMS 4.0</h1>

    <!-- KPI Row 1: Core -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 sm:gap-4 mb-6">
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
        <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Utilizzo magazzino</p>
        <p class="text-2xl sm:text-3xl font-bold text-indigo-600 mt-1">{{ stats.warehouse_utilization }}%</p>
      </div>
    </div>

    <!-- KPI Row 2: WMS 4.0 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6">
      <div class="card p-4 sm:p-5 border-l-4 border-blue-500">
        <p class="text-xs text-gray-500 dark:text-gray-400">Picking waves attive</p>
        <p class="text-xl font-bold text-blue-600 mt-1">{{ stats.active_picking_waves }}</p>
      </div>
      <div class="card p-4 sm:p-5 border-l-4 border-amber-500">
        <p class="text-xs text-gray-500 dark:text-gray-400">ASN in attesa</p>
        <p class="text-xl font-bold text-amber-600 mt-1">{{ stats.pending_asns }}</p>
      </div>
      <div class="card p-4 sm:p-5 border-l-4 border-red-500">
        <p class="text-xs text-gray-500 dark:text-gray-400">Anomalie aperte</p>
        <p class="text-xl font-bold mt-1" :class="stats.open_anomalies > 0 ? 'text-red-600' : 'text-gray-600'">{{ stats.open_anomalies }}</p>
      </div>
      <div class="card p-4 sm:p-5 border-l-4 border-purple-500">
        <p class="text-xs text-gray-500 dark:text-gray-400">Totale prodotti</p>
        <p class="text-xl font-bold text-purple-600 mt-1">{{ stats.total_products }}</p>
      </div>
    </div>

    <!-- KPI Performance -->
    <div v-if="kpi" class="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4 mb-6">
      <div class="card p-4">
        <p class="text-xs text-gray-500 dark:text-gray-400">Tempo medio picking</p>
        <p class="text-lg font-bold">{{ kpi.avg_picking_time_min }} min</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 dark:text-gray-400">Errore picking</p>
        <p class="text-lg font-bold" :class="kpi.picking_error_rate > 2 ? 'text-red-600' : 'text-green-600'">{{ kpi.picking_error_rate }}%</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 dark:text-gray-400">Rotazione stock</p>
        <p class="text-lg font-bold">{{ kpi.stock_turnover_ratio }}x</p>
      </div>
      <div class="card p-4">
        <p class="text-xs text-gray-500 dark:text-gray-400">Fulfillment rate</p>
        <p class="text-lg font-bold text-green-600">{{ kpi.order_fulfillment_rate }}%</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
      <!-- Low stock -->
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Prodotti sotto scorta</h2>
        <div v-if="lowStock.length === 0" class="text-gray-400 text-sm py-4 text-center">Nessun prodotto sotto scorta</div>
        <div v-else class="space-y-2 max-h-64 overflow-y-auto">
          <div v-for="p in lowStock" :key="p.id" class="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
            <div>
              <span class="font-medium text-sm">{{ p.name }}</span>
              <span class="text-xs text-gray-400 ml-2">{{ p.sku }}</span>
            </div>
            <span class="badge bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">{{ p.quantity }} / {{ p.min_stock }}</span>
          </div>
        </div>
      </div>

      <!-- Recent orders -->
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Ordini recenti</h2>
        <div v-if="recentOrders.length === 0" class="text-gray-400 text-sm py-4 text-center">Nessun ordine</div>
        <div v-else class="space-y-2 max-h-64 overflow-y-auto">
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

    <!-- Operator KPI -->
    <div v-if="operatorKpi.length > 0" class="card p-5 mb-6">
      <h2 class="text-lg font-semibold mb-4">Performance Operatori (7gg)</h2>
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-4 py-2 text-left font-medium">Operatore</th>
              <th class="px-4 py-2 text-right font-medium">Picks completati</th>
              <th class="px-4 py-2 text-right font-medium">Errori</th>
              <th class="px-4 py-2 text-right font-medium">Efficienza</th>
              <th class="px-4 py-2 text-right font-medium">Tempo medio (s)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
            <tr v-for="op in operatorKpi" :key="op.user_id">
              <td class="px-4 py-2">{{ op.user_name }}</td>
              <td class="px-4 py-2 text-right font-mono">{{ op.picks_completed }}</td>
              <td class="px-4 py-2 text-right font-mono" :class="op.picks_errors > 0 ? 'text-red-600' : ''">{{ op.picks_errors }}</td>
              <td class="px-4 py-2 text-right">
                <span class="badge" :class="op.efficiency_score >= 80 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">{{ op.efficiency_score }}%</span>
              </td>
              <td class="px-4 py-2 text-right font-mono">{{ op.avg_pick_time_sec }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Real-time events -->
    <div v-if="wsMessages.length > 0" class="card p-5">
      <h2 class="text-lg font-semibold mb-4">
        Eventi in tempo reale
        <span class="ml-2 w-2 h-2 rounded-full inline-block" :class="wsConnected ? 'bg-green-500' : 'bg-red-500'"></span>
      </h2>
      <div class="space-y-1 max-h-48 overflow-y-auto">
        <div v-for="(msg, idx) in wsMessages.slice(-20).reverse()" :key="idx" class="text-xs text-gray-500 dark:text-gray-400 py-1 border-b border-gray-50 dark:border-gray-800">
          <span class="font-mono">{{ msg.type }}</span> — {{ msg.data || JSON.stringify(msg) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/api'
import { useWebSocket } from '@/composables/useWebSocket'

const stats = ref({
  pending_orders: 0, daily_shipments: 0, low_stock_products: 0, monthly_revenue: 0,
  total_products: 0, total_customers: 0, active_picking_waves: 0, pending_asns: 0,
  open_anomalies: 0, warehouse_utilization: 0,
})
const lowStock = ref([])
const recentOrders = ref([])
const kpi = ref(null)
const operatorKpi = ref([])

const { messages: wsMessages, connected: wsConnected } = useWebSocket('alerts')

onMounted(async () => {
  const [s, ls, ro] = await Promise.all([
    api.get('/dashboard/stats'),
    api.get('/dashboard/low-stock'),
    api.get('/dashboard/recent-orders'),
  ])
  stats.value = s.data
  lowStock.value = ls.data
  recentOrders.value = ro.data

  try {
    const [k, ok] = await Promise.all([
      api.get('/dashboard/kpi', { params: { days: 30 } }),
      api.get('/dashboard/operator-kpi', { params: { days: 7 } }),
    ])
    kpi.value = k.data
    operatorKpi.value = ok.data
  } catch { /* kpi endpoints may not have data yet */ }
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
