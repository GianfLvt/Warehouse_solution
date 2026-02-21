<template>
  <div>
    <button type="button" @click="toggle" :class="buttonClass">
      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"/>
      </svg>
      <span>{{ scanning ? 'Chiudi Scanner' : 'Scansiona' }}</span>
    </button>

    <div v-if="scanning" class="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
      <div class="bg-white dark:bg-gray-800 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">
        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 class="font-semibold">Scansiona Barcode / QR Code</h3>
          <button @click="stop" class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div :id="readerId" class="w-full"></div>

        <div v-if="cameras.length > 1" class="px-4 pt-3">
          <select v-model="selectedCameraId" @change="switchCamera" class="input-field text-sm">
            <option v-for="cam in cameras" :key="cam.id" :value="cam.id">{{ cam.label || 'Camera ' + cam.id }}</option>
          </select>
        </div>

        <div class="p-4 space-y-3">
          <div v-if="cameraActive" class="text-center text-sm text-gray-500 dark:text-gray-400">
            Inquadra il codice a barre o QR code con la fotocamera
          </div>
          <div class="relative">
            <input
              v-model="manualCode"
              @keydown.enter.prevent="submitManual"
              class="input-field pr-20"
              placeholder="Oppure digita il codice..."
            />
            <button
              type="button"
              @click="submitManual"
              class="absolute right-1 top-1 bottom-1 px-3 bg-primary-600 text-white text-sm rounded-md hover:bg-primary-700"
            >Cerca</button>
          </div>
          <div v-if="scanError" class="text-red-500 text-sm text-center">{{ scanError }}</div>
          <div v-if="lastScanned" class="bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 text-sm p-3 rounded-lg text-center">
            Trovato: <span class="font-bold">{{ lastScanned }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue'
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode'

const props = defineProps({
  buttonClass: { type: String, default: 'btn-secondary flex items-center gap-2' }
})

const emit = defineEmits(['scanned'])

const readerId = 'barcode-reader-' + Math.random().toString(36).substring(2, 9)
const scanning = ref(false)
const cameraActive = ref(false)
const manualCode = ref('')
const scanError = ref('')
const lastScanned = ref('')
const cameras = ref([])
const selectedCameraId = ref('')
let scanner = null

const supportedFormats = [
  Html5QrcodeSupportedFormats.QR_CODE,
  Html5QrcodeSupportedFormats.EAN_13,
  Html5QrcodeSupportedFormats.EAN_8,
  Html5QrcodeSupportedFormats.CODE_128,
  Html5QrcodeSupportedFormats.CODE_39,
  Html5QrcodeSupportedFormats.CODE_93,
  Html5QrcodeSupportedFormats.UPC_A,
  Html5QrcodeSupportedFormats.UPC_E,
  Html5QrcodeSupportedFormats.ITF,
  Html5QrcodeSupportedFormats.DATA_MATRIX,
  Html5QrcodeSupportedFormats.CODABAR
]

async function toggle() {
  if (scanning.value) {
    await stop()
  } else {
    await start()
  }
}

async function startCameraWithId(cameraId) {
  try {
    await scanner.start(
      cameraId,
      { fps: 10, qrbox: { width: 250, height: 150 } },
      onScanSuccess,
      () => {}
    )
    cameraActive.value = true
    scanError.value = ''
  } catch (err) {
    cameraActive.value = false
    throw err
  }
}

async function startCameraWithFacing() {
  try {
    await scanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 250, height: 150 } },
      onScanSuccess,
      () => {}
    )
    cameraActive.value = true
    scanError.value = ''
  } catch {
    try {
      await scanner.start(
        { facingMode: 'user' },
        { fps: 10, qrbox: { width: 250, height: 150 } },
        onScanSuccess,
        () => {}
      )
      cameraActive.value = true
      scanError.value = ''
    } catch (err) {
      cameraActive.value = false
      throw err
    }
  }
}

async function start() {
  scanning.value = true
  scanError.value = ''
  lastScanned.value = ''
  manualCode.value = ''
  cameraActive.value = false

  await nextTick()

  try {
    scanner = new Html5Qrcode(readerId, { formatsToSupport: supportedFormats, verbose: false })

    let deviceList = []
    try {
      deviceList = await Html5Qrcode.getCameras()
    } catch {
      deviceList = []
    }
    cameras.value = deviceList

    if (deviceList.length > 0) {
      const backCamera = deviceList.find(c =>
        /back|rear|environment|posteriore/i.test(c.label)
      )
      const chosen = backCamera || deviceList[deviceList.length - 1]
      selectedCameraId.value = chosen.id
      await startCameraWithId(chosen.id)
    } else {
      await startCameraWithFacing()
    }
  } catch {
    scanError.value = 'Fotocamera non disponibile. Usa il campo manuale sotto per inserire il codice.'
  }
}

async function switchCamera() {
  if (!scanner || !selectedCameraId.value) return
  try {
    const state = scanner.getState()
    if (state === 2) await scanner.stop()
  } catch {}
  try {
    await startCameraWithId(selectedCameraId.value)
  } catch {
    scanError.value = 'Impossibile avviare la camera selezionata.'
  }
}

function onScanSuccess(decodedText) {
  lastScanned.value = decodedText
  scanError.value = ''
  emit('scanned', decodedText)
  stop()
}

function submitManual() {
  const code = manualCode.value.trim()
  if (!code) return
  lastScanned.value = code
  scanError.value = ''
  emit('scanned', code)
  stop()
}

async function stop() {
  if (scanner) {
    try {
      const state = scanner.getState()
      if (state === 2) {
        await scanner.stop()
      }
    } catch {}
    try {
      scanner.clear()
    } catch {}
    scanner = null
  }
  cameraActive.value = false
  scanning.value = false
}

onBeforeUnmount(() => {
  stop()
})
</script>
