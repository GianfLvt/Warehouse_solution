<template>
  <div class="flex h-screen overflow-hidden">
    <div
      v-if="ui.isMobile && ui.sidebarOpen"
      class="fixed inset-0 z-20 bg-black/50"
      @click="ui.toggleSidebar()"
    ></div>

    <aside
      :class="[
        'fixed inset-y-0 left-0 z-30 flex flex-col bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-hidden',
        ui.isMobile
          ? (ui.sidebarOpen ? 'translate-x-0 w-64' : '-translate-x-full w-64')
          : (ui.sidebarOpen ? 'w-64' : 'w-16')
      ]"
    >
      <div
        class="flex items-center h-14 border-b border-gray-200 dark:border-gray-700 flex-shrink-0"
        :class="ui.sidebarOpen ? 'px-4' : 'justify-center px-0'"
      >
        <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <span class="text-white font-bold text-sm">W</span>
        </div>
        <span v-if="ui.sidebarOpen" class="ml-3 font-bold text-lg text-gray-900 dark:text-white truncate">WareHouse</span>
      </div>

      <nav class="flex-1 overflow-y-auto overflow-x-hidden py-2 sidebar-nav">
        <template v-if="ui.sidebarOpen">
          <router-link
            v-for="item in standaloneItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center px-3 py-2 mx-2 rounded-lg text-sm transition-colors"
            :class="isActive(item.to)
              ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
            @click="ui.closeSidebarOnMobile()"
          >
            <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPaths[item.icon]"/>
            </svg>
            <span class="ml-3 truncate">{{ item.label }}</span>
          </router-link>

          <template v-for="section in menuSections" :key="section.title">
            <div v-if="section.items.length">
              <button
                type="button"
                class="w-full flex items-center justify-between px-4 pt-3 pb-1"
                @click="toggleSection(section.title)"
              >
                <span class="text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-500">{{ section.title }}</span>
                <svg
                  class="w-3.5 h-3.5 text-gray-400 dark:text-gray-500 transition-transform duration-200"
                  :class="{ '-rotate-90': collapsedSections[section.title] }"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>

              <div
                class="overflow-hidden transition-all duration-200"
                :style="{ maxHeight: collapsedSections[section.title] ? '0px' : section.items.length * 44 + 'px' }"
              >
                <router-link
                  v-for="item in section.items"
                  :key="item.to"
                  :to="item.to"
                  class="flex items-center px-3 py-2 mx-2 rounded-lg text-sm transition-colors"
                  :class="isActive(item.to)
                    ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 font-medium'
                    : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
                  @click="ui.closeSidebarOnMobile()"
                >
                  <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPaths[item.icon]"/>
                  </svg>
                  <span class="ml-3 truncate">{{ item.label }}</span>
                </router-link>
              </div>
            </div>
          </template>
        </template>

        <template v-else>
          <div class="flex flex-col items-center gap-0.5">
            <router-link
              v-for="item in allItems"
              :key="item.to"
              :to="item.to"
              :title="item.label"
              class="group relative flex items-center justify-center w-10 h-10 rounded-lg transition-colors"
              :class="isActive(item.to)
                ? 'bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                : 'text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="iconPaths[item.icon]"/>
              </svg>
              <span class="absolute left-full ml-3 px-2 py-1 rounded-md bg-gray-900 dark:bg-gray-700 text-white text-xs whitespace-nowrap opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-150 z-50 shadow-lg">{{ item.label }}</span>
            </router-link>
          </div>
        </template>
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
import { computed, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const ui = useUiStore()

const iconPaths = {
  dashboard: 'M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z',
  warehouse: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4',
  products: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4',
  lots: 'M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z',
  movements: 'M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4',
  asn: 'M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4',
  picking: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4',
  shipping: 'M13 16V6a1 1 0 00-1-1H4a1 1 0 00-1 1v10a1 1 0 001 1h1m8-1a1 1 0 01-1 1H9m4-1V8a1 1 0 011-1h2.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a1 1 0 01-1 1h-1m-6-1a1 1 0 001 1h1M5 17a2 2 0 104 0m-4 0a2 2 0 114 0m6 0a2 2 0 104 0m-4 0a2 2 0 114 0',
  inventory: 'M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  customers: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
  orders: 'M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01',
  supplier: 'M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-1v8m0 0l3-3m-3 3L9 8',
  quotes: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z',
  ai: 'M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z',
  iot: 'M8.111 16.404a5.5 5.5 0 017.778 0M12 20h.01m-7.08-7.071c3.904-3.905 10.236-3.905 14.141 0M1.394 9.393c5.857-5.857 15.355-5.857 21.213 0',
  integrations: 'M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1',
  users: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z',
}

const collapsedSections = reactive({})

function toggleSection(title) {
  collapsedSections[title] = !collapsedSections[title]
}

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path === path || route.path.startsWith(path + '/')
}

const standaloneItems = computed(() => [
  { to: '/', label: 'Dashboard', icon: 'dashboard' }
])

const menuSections = computed(() => {
  const role = auth.user?.role
  const sections = []

  if (['admin', 'responsabile', 'magazziniere'].includes(role)) {
    sections.push({
      title: 'Magazzino',
      items: [
        { to: '/warehouses', label: 'Magazzini', icon: 'warehouse' },
        { to: '/products', label: 'Prodotti', icon: 'products' },
        { to: '/lots', label: 'Lotti & Seriali', icon: 'lots' },
        { to: '/stock-movements', label: 'Movimenti', icon: 'movements' },
        { to: '/asn', label: 'Ricezione (ASN)', icon: 'asn' },
      ]
    })
  }

  const operazioniItems = []
  if (['admin', 'responsabile', 'magazziniere', 'operatore'].includes(role)) {
    operazioniItems.push({ to: '/picking', label: 'Picking', icon: 'picking' })
  }
  if (['admin', 'responsabile', 'magazziniere'].includes(role)) {
    operazioniItems.push({ to: '/shipments', label: 'Spedizioni', icon: 'shipping' })
    operazioniItems.push({ to: '/inventory', label: 'Inventario', icon: 'inventory' })
  }
  if (operazioniItems.length) {
    sections.push({ title: 'Operazioni', items: operazioniItems })
  }

  const commercialeItems = []
  if (['admin', 'responsabile', 'commerciale'].includes(role)) {
    commercialeItems.push({ to: '/customers', label: 'Clienti', icon: 'customers' })
  }
  if (['admin', 'responsabile', 'commerciale', 'magazziniere'].includes(role)) {
    commercialeItems.push({ to: '/orders', label: 'Ordini Clienti', icon: 'orders' })
  }
  if (['admin', 'responsabile', 'magazziniere'].includes(role)) {
    commercialeItems.push({ to: '/supplier-orders', label: 'Ordini Fornitori', icon: 'supplier' })
  }
  if (['admin', 'responsabile', 'commerciale'].includes(role)) {
    commercialeItems.push({ to: '/quotes', label: 'Preventivi', icon: 'quotes' })
  }
  if (commercialeItems.length) {
    sections.push({ title: 'Commerciale', items: commercialeItems })
  }

  const avanzateItems = []
  if (['admin', 'responsabile'].includes(role)) {
    avanzateItems.push({ to: '/ai', label: 'AI & Insights', icon: 'ai' })
    avanzateItems.push({ to: '/iot', label: 'IoT', icon: 'iot' })
  }
  if (avanzateItems.length) {
    sections.push({ title: 'Avanzate', items: avanzateItems })
  }

  const adminItems = []
  if (role === 'admin') {
    adminItems.push({ to: '/integrations', label: 'Integrazioni', icon: 'integrations' })
    adminItems.push({ to: '/users', label: 'Utenti', icon: 'users' })
  }
  if (adminItems.length) {
    sections.push({ title: 'Amministrazione', items: adminItems })
  }

  return sections
})

const allItems = computed(() => {
  const items = [...standaloneItems.value]
  menuSections.value.forEach(s => items.push(...s.items))
  return items
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.sidebar-nav {
  scrollbar-width: none;
}
.sidebar-nav::-webkit-scrollbar {
  display: none;
}
</style>
