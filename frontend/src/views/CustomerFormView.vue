<template>
  <div>
    <h1 class="text-2xl font-bold mb-6">{{ isEdit ? 'Modifica Cliente' : 'Nuovo Cliente' }}</h1>
    <form @submit.prevent="save" class="card p-6 max-w-3xl space-y-6">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Nome contatto *</label>
          <input v-model="form.contact_name" class="input-field" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Azienda</label>
          <input v-model="form.company_name" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input v-model="form.email" type="email" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Telefono</label>
          <input v-model="form.phone" class="input-field" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Tipo</label>
          <select v-model="form.customer_type" class="input-field">
            <option value="B2C">B2C</option>
            <option value="B2B">B2B</option>
          </select>
        </div>
        <div class="md:col-span-2">
          <label class="block text-sm font-medium mb-1">Note</label>
          <textarea v-model="form.notes" class="input-field" rows="3"></textarea>
        </div>
      </div>

      <div v-if="!isEdit">
        <h3 class="text-sm font-semibold mb-3">Indirizzo</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="md:col-span-2">
            <input v-model="address.address" class="input-field" placeholder="Indirizzo" />
          </div>
          <div>
            <input v-model="address.city" class="input-field" placeholder="Città" />
          </div>
          <div>
            <input v-model="address.zip_code" class="input-field" placeholder="CAP" />
          </div>
          <div>
            <input v-model="address.province" class="input-field" placeholder="Provincia" />
          </div>
        </div>
      </div>

      <div v-if="error" class="bg-red-50 dark:bg-red-900/30 text-red-600 text-sm p-3 rounded-lg">{{ error }}</div>

      <div class="flex gap-3">
        <button type="submit" class="btn-primary" :disabled="saving">{{ saving ? 'Salvataggio...' : 'Salva' }}</button>
        <router-link to="/customers" class="btn-secondary">Annulla</router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/composables/api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const error = ref('')

const form = ref({ contact_name: '', company_name: '', email: '', phone: '', customer_type: 'B2C', notes: '' })
const address = ref({ address: '', city: '', zip_code: '', province: '', is_default: true })

onMounted(async () => {
  if (isEdit.value) {
    const { data } = await api.get(`/customers/${route.params.id}`)
    Object.assign(form.value, data)
  }
})

async function save() {
  saving.value = true
  error.value = ''
  try {
    if (isEdit.value) {
      await api.put(`/customers/${route.params.id}`, form.value)
    } else {
      const payload = { ...form.value }
      if (address.value.address && address.value.city && address.value.zip_code) {
        payload.addresses = [address.value]
      } else {
        payload.addresses = []
      }
      await api.post('/customers', payload)
    }
    router.push('/customers')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Errore durante il salvataggio'
  } finally {
    saving.value = false
  }
}
</script>
