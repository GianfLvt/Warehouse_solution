<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-600 to-primary-900 px-4">
    <div class="card w-full max-w-md p-8">
      <div class="text-center mb-8">
        <div class="w-16 h-16 bg-primary-100 dark:bg-primary-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-primary-600" fill="currentColor" viewBox="0 0 64 64">
            <path d="M8 28L32 12L56 28V54H8V28Z"/>
            <rect x="16" y="34" width="12" height="20" rx="1" fill="#e0e7ff"/>
            <rect x="36" y="34" width="12" height="20" rx="1" fill="#e0e7ff"/>
            <rect x="22" y="22" width="20" height="6" rx="1" fill="#e0e7ff"/>
          </svg>
        </div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">WareHouse</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Gestione Magazzino e Logistica</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div v-if="error" class="bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-sm p-3 rounded-lg">
          {{ error }}
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Email</label>
          <input v-model="email" type="email" class="input-field" placeholder="admin@warehouse.local" required />
        </div>

        <div>
          <label class="block text-sm font-medium mb-1">Password</label>
          <input v-model="password" type="password" class="input-field" placeholder="••••••••" required />
        </div>

        <button type="submit" class="btn-primary w-full" :disabled="loading">
          {{ loading ? 'Accesso...' : 'Accedi' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/composables/api'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const form = new URLSearchParams()
    form.append('username', email.value)
    form.append('password', password.value)
    const { data } = await api.post('/auth/login', form)
    auth.setAuth(data)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Errore di connessione'
  } finally {
    loading.value = false
  }
}
</script>
