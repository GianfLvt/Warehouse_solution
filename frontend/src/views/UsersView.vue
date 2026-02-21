<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <h1 class="text-2xl font-bold">Gestione Utenti</h1>
      <button @click="showForm = !showForm" class="btn-primary text-center">+ Nuovo Utente</button>
    </div>

    <div v-if="showForm" class="card p-5 mb-6">
      <h2 class="text-lg font-semibold mb-4">{{ editId ? 'Modifica Utente' : 'Nuovo Utente' }}</h2>
      <form @submit.prevent="saveUser" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Nome *</label>
          <input v-model="userForm.first_name" class="input-field" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Cognome *</label>
          <input v-model="userForm.last_name" class="input-field" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Email *</label>
          <input v-model="userForm.email" type="email" class="input-field" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Ruolo *</label>
          <select v-model="userForm.role" class="input-field">
            <option value="admin">Admin</option>
            <option value="responsabile">Responsabile</option>
            <option value="magazziniere">Magazziniere</option>
            <option value="commerciale">Commerciale</option>
            <option value="operatore">Operatore</option>
          </select>
        </div>
        <div v-if="!editId">
          <label class="block text-sm font-medium mb-1">Password *</label>
          <input v-model="userForm.password" type="password" class="input-field" :required="!editId" />
        </div>
        <div class="flex items-end gap-3 md:col-span-2">
          <button type="submit" class="btn-primary">{{ editId ? 'Aggiorna' : 'Crea' }}</button>
          <button type="button" @click="cancelForm" class="btn-secondary">Annulla</button>
        </div>
      </form>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm min-w-[500px]">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th class="px-4 py-3 text-left font-medium">Nome</th>
            <th class="px-4 py-3 text-left font-medium">Email</th>
            <th class="px-4 py-3 text-center font-medium">Ruolo</th>
            <th class="px-4 py-3 text-center font-medium">Stato</th>
            <th class="px-4 py-3 text-center font-medium">Azioni</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
          <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
            <td class="px-4 py-3 font-medium">{{ u.first_name }} {{ u.last_name }}</td>
            <td class="px-4 py-3">{{ u.email }}</td>
            <td class="px-4 py-3 text-center">
              <span class="badge bg-primary-100 dark:bg-primary-900/30 text-primary-700">{{ u.role }}</span>
            </td>
            <td class="px-4 py-3 text-center">
              <span :class="u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="badge">{{ u.is_active ? 'Attivo' : 'Disattivato' }}</span>
            </td>
            <td class="px-4 py-3 text-center">
              <div class="flex items-center justify-center gap-2">
                <button @click="editUser(u)" class="text-primary-600 hover:underline text-xs">Modifica</button>
                <button @click="toggleActive(u)" class="text-yellow-600 hover:underline text-xs">{{ u.is_active ? 'Disattiva' : 'Attiva' }}</button>
                <button @click="deleteUser(u)" class="text-red-500 hover:underline text-xs">Elimina</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/api'

const users = ref([])
const showForm = ref(false)
const editId = ref(null)
const userForm = ref({ first_name: '', last_name: '', email: '', role: 'operatore', password: '' })

async function load() {
  const { data } = await api.get('/users')
  users.value = data
}

function editUser(u) {
  editId.value = u.id
  userForm.value = { first_name: u.first_name, last_name: u.last_name, email: u.email, role: u.role, password: '' }
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editId.value = null
  userForm.value = { first_name: '', last_name: '', email: '', role: 'operatore', password: '' }
}

async function saveUser() {
  if (editId.value) {
    const payload = { first_name: userForm.value.first_name, last_name: userForm.value.last_name, email: userForm.value.email, role: userForm.value.role }
    await api.put(`/users/${editId.value}`, payload)
  } else {
    await api.post('/users', userForm.value)
  }
  cancelForm()
  await load()
}

async function toggleActive(u) {
  await api.put(`/users/${u.id}`, { is_active: !u.is_active })
  await load()
}

async function deleteUser(u) {
  if (!confirm(`Eliminare "${u.first_name} ${u.last_name}"?`)) return
  await api.delete(`/users/${u.id}`)
  await load()
}

onMounted(load)
</script>
