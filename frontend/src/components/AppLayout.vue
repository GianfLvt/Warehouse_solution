<template>
  <div class="flex h-screen overflow-hidden">
    <div
      v-if="ui.isMobile && ui.sidebarOpen"
      class="fixed inset-0 z-20 bg-black/50"
      @click="ui.toggleSidebar()"
    ></div>

    <aside
      :class="[
        'fixed inset-y-0 left-0 z-30 flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-transform duration-300',
        ui.isMobile
          ? (ui.sidebarOpen ? 'translate-x-0 w-64' : '-translate-x-full w-64')
          : (ui.sidebarOpen ? 'translate-x-0 w-64' : 'translate-x-0 w-16')
      ]"
    >
      <div class="flex items-center h-14 px-4 border-b border-gray-200 dark:border-gray-700">
        <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <span class="text-white font-bold text-sm">W</span>
        </div>
        <span v-if="ui.sidebarOpen" class="ml-3 font-bold text-lg text-gray-900 dark:text-white truncate">WareHouse</span>
      </div>

      <nav class="flex-1 overflow-y-auto py-4">
        <router-link
          v-for="item in menuItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center px-4 py-2.5 mx-2 rounded-lg text-sm transition-colors"
          :class="$route.path === item.to || $route.path.startsWith(item.to + '/')
            ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
          @click="ui.closeSidebarOnMobile()"
        >
          <component :is="item.icon" class="w-5 h-5 flex-shrink-0" />
          <span v-if="ui.sidebarOpen" class="ml-3 truncate">{{ item.label }}</span>
        </router-link>
      </nav>
    </aside>

    <div
      :class="[
        'flex-1 flex flex-col transition-all duration-300 min-w-0',
        ui.isMobile ? 'ml-0' : (ui.sidebarOpen ? 'ml-64' : 'ml-16')
      ]"
    >
      <header class="h-14 flex items-center justify-between px-3 sm:px-6 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
        <button @click="ui.toggleSidebar()" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <div class="flex items-center gap-2 sm:gap-3 min-w-0">
          <button @click="ui.toggleDark()" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 flex-shrink-0">
            <svg v-if="ui.darkMode" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/>
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
            </svg>
          </button>

          <div class="text-sm hidden sm:flex items-center gap-1 min-w-0">
            <span class="font-medium truncate">{{ auth.fullName }}</span>
            <span class="badge bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300 flex-shrink-0">{{ auth.user?.role }}</span>
          </div>

          <button @click="handleLogout" class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500 flex-shrink-0">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
          </button>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6 bg-gray-50 dark:bg-gray-900">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const auth = useAuthStore()
const ui = useUiStore()

const menuItems = computed(() => {
  const role = auth.user?.role
  const items = [
    { to: '/', label: 'Dashboard', icon: 'IconDashboard' },
  ]
  if (['admin', 'responsabile', 'magazziniere'].includes(role)) {
    items.push({ to: '/products', label: 'Prodotti', icon: 'IconProducts' })
    items.push({ to: '/stock-movements', label: 'Movimenti', icon: 'IconMovements' })
  }
  if (['admin', 'responsabile', 'commerciale'].includes(role)) {
    items.push({ to: '/customers', label: 'Clienti', icon: 'IconCustomers' })
  }
  if (['admin', 'responsabile', 'commerciale', 'magazziniere'].includes(role)) {
    items.push({ to: '/orders', label: 'Ordini Clienti', icon: 'IconOrders' })
  }
  if (['admin', 'responsabile', 'magazziniere'].includes(role)) {
    items.push({ to: '/supplier-orders', label: 'Ordini Fornitori', icon: 'IconSupplier' })
  }
  if (['admin', 'responsabile', 'commerciale'].includes(role)) {
    items.push({ to: '/quotes', label: 'Preventivi', icon: 'IconQuotes' })
  }
  if (role === 'admin') {
    items.push({ to: '/users', label: 'Utenti', icon: 'IconUsers' })
  }
  return items
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<script>
const iconBase = { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="d"/></svg>', props: ['d'] }

export default {
  components: {
    IconDashboard: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"/></svg>' },
    IconProducts: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>' },
    IconMovements: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"/></svg>' },
    IconCustomers: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>' },
    IconOrders: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/></svg>' },
    IconSupplier: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-1v8m0 0l3-3m-3 3L9 8"/></svg>' },
    IconQuotes: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/></svg>' },
    IconUsers: { template: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>' },
  }
}
</script>
