<template>
  <div>
    <div class="flex items-center gap-3 mb-6">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/></svg>
      </button>
      <h1 class="text-2xl font-bold">{{ isEdit ? 'Modifica' : 'Nuovo' }} ASN</h1>
    </div>

    <form @submit.prevent="save" class="space-y-6">
      <div class="card p-5">
        <h2 class="text-lg font-semibold mb-4">Dati ASN</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="label">Fornitore</label>
            <input v-model="form.supplier_name" class="input-field w-full" placeholder="Nome fornitore" />
          </div>
          <div>
            <label class="label">Magazzino *</label>
            <select v-model.number="form.warehouse_id" class="input-field w-full" required>
              <option value="">Seleziona...</option>
              <option v-for="w in warehouses" :key="w.id" :value="w.id">{{ w.name }}</option>
            </select>
          </div>
          <div>
            <label class="label">Arrivo previsto</label>
            <input v-model="form.expected_arrival" type="datetime-local" class="input-field w-full" />
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div>
            <label class="label">Riferimento PO</label>
            <input v-model="form.po_reference" class="input-field w-full" />
          </div>
          <div>
            <label class="label">Note</label>
            <input v-model="form.notes" class="input-field w-full" />
          </div>
        </div>
      </div>

      <div class="card p-5">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold">Righe</h2>
          <button type="button" @click="addItem" class="btn-primary text-sm">+ Aggiungi riga</button>
        </div>
        <div v-for="(item, idx) in form.items" :key="idx" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-3">
          <div class="flex items-center justify-between mb-3">
            <span class="font-medium text-sm">Riga {{ idx + 1 }}</span>
            <button type="button" @click="removeItem(idx)" class="text-red-500 text-xs hover:underline">Rimuovi</button>
          </div>
          <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
            <div>
              <label class="label text-xs">Prodotto *</label>
              <select v-model.number="item.product_id" class="input-field w-full" required>
                <option value="">Seleziona...</option>
                <option v-for="p in products" :key="p.id" :value="p.id">{{ p.sku }} - {{ p.name }}</option>
              </select>
            </div>
            <div>
              <label class="label text-xs">Quantità *</label>
              <input v-model.number="item.expected_quantity" class="input-field w-full" type="number" min="1" required />
            </div>
            <div>
              <label class="label text-xs">Lotto</label>
              <input v-model="item.lot_number" class="input-field w-full" />
            </div>
            <div>
              <label class="label text-xs">Ubicazione destinazione</label>
              <input v-model.number="item.target_location_id" class="input-field w-full" type="number" placeholder="ID ubicazione" />
            </div>
          </div>
        </div>
        <div v-if="form.items.length === 0" class="text-center text-gray-400 py-4 text-sm">Aggiungi almeno una riga</div>
      </div>

      <div class="flex justify-end gap-3">
        <button type="button" @click="$router.back()" class="btn-secondary">Annulla</button>
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Salvataggio...' : 'Salva ASN' }}</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import api from '@/composables/api'

const router = useRouter()
const route = useRoute()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const warehouses = ref([])
const products = ref([])

const form = ref({
  supplier_name: '',
  warehouse_id: '',
  expected_arrival: '',
  po_reference: '',
  notes: '',
  items: [],
})

function addItem() {
  form.value.items.push({ product_id: '', expected_quantity: 1, lot_number: '', target_location_id: null })
}
function removeItem(idx) {
  form.value.items.splice(idx, 1)
}

async function save() {
  saving.value = true
  try {
    const payload = {
      ...form.value,
      expected_arrival: form.value.expected_arrival || undefined,
      items: form.value.items.map(i => ({
        product_id: i.product_id,
        expected_quantity: i.expected_quantity,
        lot_number: i.lot_number || undefined,
        target_location_id: i.target_location_id || undefined,
      })),
    }
    if (isEdit.value) {
      await api.put(`/asn/${route.params.id}`, payload)
    } else {
      await api.post('/asn', payload)
    }
    router.push('/asn')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [w, p] = await Promise.all([
    api.get('/warehouses'),
    api.get('/products'),
  ])
  warehouses.value = w.data
  products.value = p.data

  if (isEdit.value) {
    const { data } = await api.get(`/asn/${route.params.id}`)
    form.value = {
      supplier_name: data.supplier_name || '',
      warehouse_id: data.warehouse_id,
      expected_arrival: data.expected_arrival?.slice(0, 16) || '',
      po_reference: data.po_reference || '',
      notes: data.notes || '',
      items: (data.items || []).map(i => ({
        product_id: i.product_id,
        expected_quantity: i.expected_quantity,
        lot_number: i.lot_number || '',
        target_location_id: i.target_location_id,
      })),
    }
  }
})
</script>
