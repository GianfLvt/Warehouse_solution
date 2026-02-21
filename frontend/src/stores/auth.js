import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('bp_token') || '')
  const user = ref(JSON.parse(localStorage.getItem('bp_user') || 'null'))

  const isAuthenticated = computed(() => !!token.value)
  const fullName = computed(() => user.value ? `${user.value.first_name} ${user.value.last_name}` : '')

  function setAuth(data) {
    token.value = data.access_token
    user.value = data.user
    localStorage.setItem('bp_token', data.access_token)
    localStorage.setItem('bp_user', JSON.stringify(data.user))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('bp_token')
    localStorage.removeItem('bp_user')
  }

  return { token, user, isAuthenticated, fullName, setAuth, logout }
})
