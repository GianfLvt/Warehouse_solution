<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">{{ isEdit ? 'Modifica Prodotto' : 'Nuovo Prodotto' }}</h1>
    <form @submit.prevent="save" class="card p-6 max-w-3xl space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">SKU *</label>
          <input v-model="form.sku" class="input-field" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Barcode</label>
          <div class="flex gap-2">
            <input v-model="form.barcode" class="input-field flex-1" placeholder="Scansiona o inserisci manualmente" />
            <BarcodeScanner button-class="btn-secondary flex items-center gap-1 px-3 text-sm whitespace-nowrap" @scanned="onBarcodeScan" />
          </div>
        </div>
        <div class="md:col-span-2">
          <label class="block text-sm font-medium mb-1">Nome *</label>
          <input v-model="form.name" class="input-field" required />
        </div>
        <div class="md:col-span-2">
          <label class="block text-sm font-medium mb-1">Descrizione</label>
          <textarea v-model="form.description" class="input-field" rows="3"></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Categoria</label>
          <input v-model="form.category" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Fornitore</label>
          <input v-model="form.supplier" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Prezzo Acquisto (€)</label>
          <input v-model.number="form.purchase_price" type="number" step="0.01" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Prezzo Vendita (€)</label>
          <input v-model.number="form.sale_price" type="number" step="0.01" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Quantità</label>
          <input v-model.number="form.quantity" type="number" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Soglia minima scorta</label>
          <input v-model.number="form.min_stock" type="number" class="input-field" />
        </div>
      </div>

      <div>
        <h3 class="text-sm font-semibold mb-3">Ubicazione</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div>
            <label class="block text-xs font-medium mb-1">Corsia</label>
            <input v-model="form.location_aisle" class="input-field" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Scaffale</label>
            <input v-model="form.location_shelf" class="input-field" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Ripiano</label>
            <input v-model="form.location_level" class="input-field" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1">Bin</label>
            <input v-model="form.location_bin" class="input-field" />
          </div>
        </div>
      </div>

      <div v-if="isEdit" class="border-t border-gray-200 dark:border-gray-700 pt-4">
        <h3 class="text-sm font-semibold mb-3">Codici Generati</h3>
        <div class="flex flex-col sm:flex-row flex-wrap gap-4">
          <div class="text-center">
            <img :src="barcodeUrl" alt="Barcode" class="border border-gray-200 dark:border-gray-700 rounded-lg p-2 bg-white max-w-full" />
            <a :href="barcodeUrl" download class="text-xs text-primary-600 hover:underline mt-1 inline-block">Scarica Barcode</a>
          </div>
          <div class="text-center">
            <img :src="qrcodeUrl" alt="QR Code" class="border border-gray-200 dark:border-gray-700 rounded-lg p-2 bg-white w-[140px] h-[140px] sm:w-[180px] sm:h-[180px]" />
            <a :href="qrcodeUrl" download class="text-xs text-primary-600 hover:underline mt-1 inline-block">Scarica QR Code</a>
          </div>
        </div>
        <p class="text-xs text-gray-500 mt-2">Il codice generato contiene: <span class="font-mono font-semibold">{{ form.barcode || form.sku }}</span></p>
      </div>

      <div v-if="error" class="bg-red-50 dark:bg-red-900/30 text-red-600 text-sm p-3 rounded-lg">{{ error }}</div>

      <div class="flex gap-3">
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Salvataggio...' : 'Salva' }}</button>
        <router-link to="/products" class="btn-secondary">Annulla</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/composables/api'
import BarcodeScanner from '@/components/BarcodeScanner.vue'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const error = ref('')

const barcodeUrl = computed(() => isEdit.value ? `/api/products/${route.params.id}/barcode` : '')
const qrcodeUrl = computed(() => isEdit.value ? `/api/products/${route.params.id}/qrcode` : '')

const form = ref({
  sku: '', barcode: '', name: '', description: '', category: '', supplier: '',
  purchase_price: 0, sale_price: 0, quantity: 0, min_stock: 0,
  location_aisle: '', location_shelf: '', location_level: '', location_bin: ''
})

onMounted(async () => {
  if (isEdit.value) {
    const { data } = await api.get(`/products/${route.params.id}`)
    Object.assign(form.value, data)
  } else if (route.query.barcode) {
    form.value.barcode = route.query.barcode
  }
})

function onBarcodeScan(code) {
  form.value.barcode = code
}

async function save() {
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      await api.put(`/products/${route.params.id}`, form.value)
    } else {
      await api.post('/products', form.value)
    }
    router.push('/products')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Errore durante il salvataggio'
  } finally {
    saving.value = false
  }
}
</script>
