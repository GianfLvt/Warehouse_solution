<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">AI & Insights</h1>

    <!-- Tabs -->
    <div class="flex border-b border-gray-200 dark:border-gray-700 mb-6 overflow-x-auto">
      <button v-for="tab in tabs" :key="tab.key" @click="activeTab = tab.key"
        class="px-4 py-2 text-sm font-medium whitespace-nowrap border-b-2 transition-colors"
        :class="activeTab === tab.key ? 'border-primary-600 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700'">
        {{ tab.label }}
      </button>
    </div>

    <!-- Stock Predictions -->
    <div v-if="activeTab === 'predictions'" class="space-y-4">
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Previsioni Domanda Stock</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm min-w-[700px]">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-3 text-left font-medium">Prodotto</th>
                <th class="px-4 py-3 text-right font-medium">Qtà attuale</th>
                <th class="px-4 py-3 text-right font-medium">Media giorn. (30gg)</th>
                <th class="px-4 py-3 text-right font-medium">Previsione 30gg</th>
                <th class="px-4 py-3 text-right font-medium">Giorni copertura</th>
                <th class="px-4 py-3 text-left font-medium">Rischio</th>
                <th class="px-4 py-3 text-right font-medium">Riordino suggerito</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="p in predictions" :key="p.product_id" :class="p.days_of_coverage < 7 ? 'bg-red-50 dark:bg-red-900/10' : ''">
                <td class="px-4 py-3 font-medium">{{ p.product_name }}</td>
                <td class="px-4 py-3 text-right">{{ p.current_stock }}</td>
                <td class="px-4 py-3 text-right">{{ p.avg_daily_demand?.toFixed(1) }}</td>
                <td class="px-4 py-3 text-right">{{ p.predicted_demand_30d }}</td>
                <td class="px-4 py-3 text-right font-mono" :class="p.days_of_coverage < 7 ? 'text-red-600 font-bold' : ''">
                  {{ p.days_of_coverage || '∞' }}
                </td>
                <td class="px-4 py-3">
                  <span class="badge text-xs" :class="riskClass(p.risk_level)">{{ p.risk_level }}</span>
                </td>
                <td class="px-4 py-3 text-right font-bold text-primary-600">{{ p.suggested_reorder || '-' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="predictions.length === 0" class="text-center text-gray-400 py-8">Nessuna previsione disponibile</div>
        </div>
      </div>
    </div>

    <!-- Anomalies -->
    <div v-if="activeTab === 'anomalies'" class="space-y-4">
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Anomalie Rilevate</h2>
        <div class="space-y-3">
          <div v-for="a in anomalies" :key="a.id || a.anomaly_type + a.related_id"
            class="border rounded-lg p-4" :class="severityBorderClass(a.severity)">
            <div class="flex items-center justify-between mb-2">
              <span class="badge text-xs" :class="severityClass(a.severity)">{{ a.severity }}</span>
              <span class="text-xs text-gray-400">{{ a.anomaly_type }}</span>
            </div>
            <p class="text-sm font-medium">{{ a.description }}</p>
            <p v-if="a.suggested_action" class="text-xs text-gray-500 mt-1">Azione: {{ a.suggested_action }}</p>
          </div>
          <div v-if="anomalies.length === 0" class="text-center text-gray-400 py-6 text-sm">Nessuna anomalia rilevata</div>
        </div>
      </div>
    </div>

    <!-- Slotting -->
    <div v-if="activeTab === 'slotting'" class="space-y-4">
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Ottimizzazione Slotting</h2>
        <p class="text-sm text-gray-500 mb-4">Suggerimenti per riposizionamento prodotti in base a frequenza di prelievo e rotazione.</p>
        <div class="overflow-x-auto">
          <table class="w-full text-sm min-w-[700px]">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-3 text-left font-medium">Prodotto</th>
                <th class="px-4 py-3 text-left font-medium">Classe ABC</th>
                <th class="px-4 py-3 text-right font-medium">Movimenti (30gg)</th>
                <th class="px-4 py-3 text-left font-medium">Ubicazione attuale</th>
                <th class="px-4 py-3 text-left font-medium">Ubicazione suggerita</th>
                <th class="px-4 py-3 text-left font-medium">Motivo</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="s in slotting" :key="s.product_id">
                <td class="px-4 py-3">{{ s.product_name }}</td>
                <td class="px-4 py-3"><span class="badge text-xs" :class="abcClass(s.abc_class)">{{ s.abc_class }}</span></td>
                <td class="px-4 py-3 text-right">{{ s.movement_count_30d }}</td>
                <td class="px-4 py-3 font-mono text-xs">{{ s.current_location || '-' }}</td>
                <td class="px-4 py-3 font-mono text-xs text-primary-600">{{ s.suggested_zone || '-' }}</td>
                <td class="px-4 py-3 text-xs text-gray-500">{{ s.reason }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="slotting.length === 0" class="text-center text-gray-400 py-8">Nessun suggerimento disponibile</div>
        </div>
      </div>
    </div>

    <!-- Seasonal trends -->
    <div v-if="activeTab === 'trends'" class="space-y-4">
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Trend Stagionali</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm min-w-[800px]">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-3 text-left font-medium">Mese</th>
                <th class="px-4 py-3 text-right font-medium">Movimenti</th>
                <th class="px-4 py-3 text-right font-medium">Vendite €</th>
                <th class="px-4 py-3 text-right font-medium">Ordini</th>
                <th class="px-4 py-3 text-left font-medium">Trend</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="t in trends" :key="t.month">
                <td class="px-4 py-3 font-medium">{{ t.month }}</td>
                <td class="px-4 py-3 text-right">{{ t.total_movements }}</td>
                <td class="px-4 py-3 text-right">€ {{ formatNumber(t.total_revenue) }}</td>
                <td class="px-4 py-3 text-right">{{ t.total_orders }}</td>
                <td class="px-4 py-3">
                  <div class="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div class="bg-primary-600 h-2 rounded-full" :style="{ width: trendWidth(t) }"></div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="trends.length === 0" class="text-center text-gray-400 py-8">Nessun dato stagionale</div>
        </div>
      </div>
    </div>

    <!-- Operator Performance -->
    <div v-if="activeTab === 'operators'" class="space-y-4">
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Performance Operatori</h2>
        <div class="overflow-x-auto">
          <table class="w-full text-sm min-w-[600px]">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-4 py-3 text-left font-medium">Operatore</th>
                <th class="px-4 py-3 text-right font-medium">Picks</th>
                <th class="px-4 py-3 text-right font-medium">Errori</th>
                <th class="px-4 py-3 text-right font-medium">Efficienza</th>
                <th class="px-4 py-3 text-right font-medium">Tempo medio (s)</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
              <tr v-for="op in operators" :key="op.user_id">
                <td class="px-4 py-3 font-medium">{{ op.user_name || `User #${op.user_id}` }}</td>
                <td class="px-4 py-3 text-right">{{ op.picks_completed }}</td>
                <td class="px-4 py-3 text-right" :class="op.picks_errors > 0 ? 'text-red-600' : ''">{{ op.picks_errors }}</td>
                <td class="px-4 py-3 text-right">
                  <span class="badge" :class="op.efficiency_score >= 80 ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'">{{ op.efficiency_score }}%</span>
                </td>
                <td class="px-4 py-3 text-right font-mono">{{ op.avg_pick_time_sec }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="operators.length === 0" class="text-center text-gray-400 py-8">Nessun dato performance</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import api from '@/composables/api'

const tabs = [
  { key: 'predictions', label: 'Previsioni Stock' },
  { key: 'anomalies', label: 'Anomalie' },
  { key: 'slotting', label: 'Slotting' },
  { key: 'trends', label: 'Trend Stagionali' },
  { key: 'operators', label: 'Performance' },
]
const activeTab = ref('predictions')

const predictions = ref([])
const anomalies = ref([])
const slotting = ref([])
const trends = ref([])
const operators = ref([])

async function loadTab() {
  try {
    if (activeTab.value === 'predictions') {
      const { data } = await api.get('/ai/stock-predictions')
      predictions.value = data
    } else if (activeTab.value === 'anomalies') {
      const { data } = await api.get('/ai/anomalies')
      anomalies.value = data
    } else if (activeTab.value === 'slotting') {
      const { data } = await api.get('/ai/slotting')
      slotting.value = data
    } else if (activeTab.value === 'trends') {
      const { data } = await api.get('/ai/seasonal-trends')
      trends.value = data
    } else if (activeTab.value === 'operators') {
      const { data } = await api.get('/ai/operator-performance')
      operators.value = data
    }
  } catch (e) {
    console.error('AI load error:', e)
  }
}

watch(activeTab, loadTab)
onMounted(loadTab)

function riskClass(level) {
  const m = { critical: 'bg-red-100 text-red-700', high: 'bg-orange-100 text-orange-700', medium: 'bg-yellow-100 text-yellow-700', low: 'bg-green-100 text-green-700' }
  return m[level] || 'bg-gray-100 text-gray-600'
}
function severityClass(s) {
  const m = { critical: 'bg-red-100 text-red-700', high: 'bg-orange-100 text-orange-700', medium: 'bg-yellow-100 text-yellow-700', low: 'bg-blue-100 text-blue-700' }
  return m[s] || 'bg-gray-100 text-gray-600'
}
function severityBorderClass(s) {
  const m = { critical: 'border-red-300 dark:border-red-700', high: 'border-orange-300 dark:border-orange-700', medium: 'border-yellow-300 dark:border-yellow-700', low: 'border-blue-200 dark:border-blue-800' }
  return m[s] || 'border-gray-200 dark:border-gray-700'
}
function abcClass(c) {
  const m = { A: 'bg-red-100 text-red-700', B: 'bg-yellow-100 text-yellow-700', C: 'bg-green-100 text-green-700' }
  return m[c] || 'bg-gray-100 text-gray-600'
}

function trendWidth(t) {
  const max = Math.max(...trends.value.map(x => x.total_movements || 0), 1)
  return Math.round(((t.total_movements || 0) / max) * 100) + '%'
}

function formatNumber(n) { return Number(n || 0).toLocaleString('it-IT', { minimumFractionDigits: 2 }) }
</script>
