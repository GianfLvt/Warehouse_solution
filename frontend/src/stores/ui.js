import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const isMobile = ref(window.innerWidth < 768)
  const sidebarOpen = ref(!isMobile.value)
  const darkMode = ref(localStorage.getItem('bp_dark') === 'true')

  if (darkMode.value) document.documentElement.classList.add('dark')

  function handleResize() {
    const mobile = window.innerWidth < 768
    if (mobile !== isMobile.value) {
      isMobile.value = mobile
      sidebarOpen.value = !mobile
    }
  }

  window.addEventListener('resize', handleResize)

  function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
  }

  function closeSidebarOnMobile() {
    if (isMobile.value) sidebarOpen.value = false
  }

  function toggleDark() {
    darkMode.value = !darkMode.value
    localStorage.setItem('bp_dark', String(darkMode.value))
    document.documentElement.classList.toggle('dark', darkMode.value)
  }

  return { sidebarOpen, darkMode, isMobile, toggleSidebar, closeSidebarOnMobile, toggleDark }
})
