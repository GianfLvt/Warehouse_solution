import { ref, onUnmounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export function useWebSocket(channel) {
  const messages = ref([])
  const connected = ref(false)
  let ws = null
  let reconnectTimer = null

  function connect() {
    const auth = useAuthStore()
    if (!auth.token) return

    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${protocol}//${location.host}/ws/${channel}`
    ws = new WebSocket(url)

    ws.onopen = () => {
      connected.value = true
    }
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        messages.value.push(data)
        if (messages.value.length > 100) messages.value.shift()
      } catch {
        messages.value.push({ type: 'raw', data: event.data })
      }
    }
    ws.onclose = () => {
      connected.value = false
      reconnectTimer = setTimeout(connect, 5000)
    }
    ws.onerror = () => {
      ws?.close()
    }
  }

  function send(data) {
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(typeof data === 'string' ? data : JSON.stringify(data))
    }
  }

  function disconnect() {
    clearTimeout(reconnectTimer)
    ws?.close()
    ws = null
    connected.value = false
  }

  connect()
  onUnmounted(disconnect)

  return { messages, connected, send, disconnect }
}
