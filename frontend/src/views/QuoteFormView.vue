<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">Nuovo Preventivo</h1>
    <form @submit.prevent="save" class="card p-6 max-w-4xl space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Cliente *</label>
          <select v-model.number="form.customer_id" class="input-field" required>
            <option value="">Seleziona...</option>
            <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.contact_name }} {{ c.company_name ? `(${c.company_name})` : '' }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Note</label>
          <input v-model="form.notes" class="input-field" />
        </div>
      </div>

      <div>
        <div class="flex items-center justify-between mb-3">
          <h3 class="text-sm font-semibold">Articoli *</h3>
          <div class="flex gap-2">
            <BarcodeScanner button-class="btn-secondary flex items-center gap-1 text-xs" @scanned="onScanQuoteItem" />
            <button type="button" @click="addItem" class="btn-secondary text-xs">+ Aggiungi</button>
          </div>
        </div>
        <div v-for="(item, i) in form.items" :key="i" class="flex flex-col sm:grid sm:grid-cols-12 gap-2 mb-3 p-3 sm:p-0 bg-gray-50 dark:bg-gray-700/30 sm:bg-transparent rounded-lg sm:items-end">
          <div class="sm:col-span-5">
            <label class="block text-xs font-medium mb-1 sm:hidden">Prodotto</label>
            <select v-model.number="item.product_id" class="input-field" required @change="onProductSelect(item)">
              <option value="">Prodotto...</option>
              <option v-for="p in products" :key="p.id" :value="p.id">{{ p.sku }} - {{ p.name }}</option>
            </select>
          </div>
          <div class="sm:col-span-2">
            <label class="block text-xs font-medium mb-1 sm:hidden">Quantità</label>
            <input v-model.number="item.quantity" type="number" min="1" class="input-field" placeholder="Qtà" required />
          </div>
          <div class="sm:col-span-3">
            <label class="block text-xs font-medium mb-1 sm:hidden">Prezzo</label>
            <input v-model.number="item.unit_price" type="number" step="0.01" class="input-field" placeholder="Prezzo" required />
          </div>
          <div class="sm:col-span-2 flex justify-end">
            <button type="button" @click="removeItem(i)" class="p-2 text-red-500 hover:bg-red-50 rounded">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>
        <div class="text-right text-sm font-semibold mt-3">
          Totale: € {{ total.toFixed(2) }}
        </div>
      </div>

      <div v-if="error" class="bg-red-50 dark:bg-red-900/30 text-red-600 text-sm p-3 rounded-lg">{{ error }}</div>

      <div class="flex gap-3">
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Salvataggio...' : 'Crea Preventivo' }}</button>
        <router-link to="/quotes" class="btn-secondary">Annulla</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/composables/api'
import BarcodeScanner from '@/components/BarcodeScanner.vue'

const router = useRouter()
const customers = ref([])
const products = ref([])
const saving = ref(false)
const error = ref('')

const form = ref({
  customer_id: '',
  notes: '',
  items: [{ product_id: '', quantity: 1, unit_price: 0 }],
})

const total = computed(() => form.value.items.reduce((s, i) => s + (i.quantity || 0) * (i.unit_price || 0), 0))

function addItem() { form.value.items.push({ product_id: '', quantity: 1, unit_price: 0 }) }
function removeItem(i) { if (form.value.items.length > 1) form.value.items.splice(i, 1) }

function onProductSelect(item) {
  const p = products.value.find(x => x.id === item.product_id)
  if (p) item.unit_price = p.sale_price
}

async function onScanQuoteItem(code) {
  try {
    const { data } = await api.get(`/products/lookup/${encodeURIComponent(code)}`)
    const existing = form.value.items.find(i => i.product_id === data.id)
    if (existing) {
      existing.quantity += 1
    } else {
      form.value.items.push({ product_id: data.id, quantity: 1, unit_price: data.sale_price })
    }
  } catch {
    alert('Prodotto non trovato per questo codice')
  }
}

onMounted(async () => {
  const [c, p] = await Promise.all([api.get('/customers'), api.get('/products')])
  customers.value = c.data
  products.value = p.data
})

async function save() {
  saving.value = true
  error.value = ''
  try {
    await api.post('/quotes', form.value)
    router.push('/quotes')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Errore durante la creazione'
  } finally {
    saving.value = false
  }
}
</script>
