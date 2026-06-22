<template>
  <div class="min-h-screen bg-black flex flex-col">
    <!-- Back bar -->
    <div class="flex items-center gap-4 px-6 py-3 bg-gray-900/80 backdrop-blur-sm">
      <button @click="goBack" class="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
        </svg>
        <span class="text-sm">Retour</span>
      </button>
      <span class="text-white font-medium text-sm truncate flex-1">{{ title }}</span>
      <span class="text-xs text-gray-500 uppercase tracking-wider">{{ typeLabel }}</span>
    </div>

    <!-- Video area -->
    <div class="flex-1 flex items-center justify-center bg-black relative">
      <!-- Loading -->
      <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
        <div class="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Error -->
      <div v-if="error" class="text-center text-red-400 px-8">
        <svg class="w-12 h-12 mx-auto mb-3 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        <p class="font-medium">Impossible de lire le flux</p>
        <p class="text-sm text-gray-500 mt-1">{{ error }}</p>
        <button @click="loadStream" class="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700">
          Réessayer
        </button>
      </div>

      <!-- Video element -->
      <video
        v-show="!loading && !error"
        ref="videoEl"
        class="w-full max-h-screen"
        controls
        autoplay
        playsinline
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @ended="onEnded"
        @error="onVideoError"
        @waiting="loading = true"
        @playing="loading = false"
        @canplay="loading = false"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'

const route = useRoute()
const router = useRouter()
const catalog = useCatalogStore()

const videoEl = ref(null)
const loading = ref(true)
const error = ref(null)
const streamUrl = ref(null)
const hlsInstance = ref(null)

// Progress tracking
const currentTime = ref(0)
const duration = ref(0)
let saveTimer = null

const streamType = computed(() => route.params.type)
// streamId est toujours un Number (utilisé pour les appels API)
const streamId = computed(() => Number(route.params.id))
const containerExt = computed(() => route.query.ext || null)
// Titre affiché dans la barre — passé en query param depuis les vues parentes
const streamTitle = computed(() => route.query.title || null)

const title = computed(() => {
  if (streamTitle.value) return streamTitle.value
  const id = streamId.value
  const type = streamType.value
  if (type === 'live') {
    const item = catalog.liveStreams.find((s) => s.stream_id === id)
    return item?.name || 'Live TV'
  }
  if (type === 'vod') {
    const item = catalog.vodStreams.find((s) => s.stream_id === id)
    return item?.name || 'Film'
  }
  // Pour series, le titre de l'épisode est passé en query
  return 'Épisode'
})

const typeLabel = computed(() => {
  if (streamType.value === 'live') return 'Live'
  if (streamType.value === 'vod') return 'Film'
  return 'Série'
})

async function loadStream() {
  loading.value = true
  error.value = null
  try {
    const url = await catalog.getStreamUrl(streamType.value, streamId.value, containerExt.value)
    streamUrl.value = url
    await setupPlayer(url)
  } catch (e) {
    error.value = e?.response?.data?.detail || 'Erreur réseau'
    loading.value = false
  }
}

async function setupPlayer(url) {
  if (!videoEl.value) return

  // Try HLS.js for .m3u8 streams
  if (url.includes('.m3u8') && streamType.value === 'live') {
    const Hls = (await import('hls.js')).default
    if (Hls.isSupported()) {
      if (hlsInstance.value) {
        hlsInstance.value.destroy()
      }
      const hls = new Hls({ enableWorker: true, lowLatencyMode: true })
      hlsInstance.value = hls
      hls.loadSource(url)
      hls.attachMedia(videoEl.value)
      hls.on(Hls.Events.ERROR, (event, data) => {
        if (data.fatal) {
          error.value = `HLS error: ${data.type}`
          loading.value = false
        }
      })
      return
    }
    // Fallback: native HLS (Safari)
  }

  // Direct src for VOD/series or native HLS
  videoEl.value.src = url

  // Restore progress for VOD/series
  if (streamType.value !== 'live') {
    const hist = catalog.history.find(
      (h) => h.item_type === streamType.value && h.item_id === streamId.value
    )
    if (hist && hist.progress_sec > 10 && !hist.completed) {
      videoEl.value.currentTime = hist.progress_sec
    }
  }
}

function onLoadedMetadata() {
  duration.value = videoEl.value?.duration || 0
  loading.value = false
}

function onTimeUpdate() {
  currentTime.value = videoEl.value?.currentTime || 0
}

function onEnded() {
  if (streamType.value !== 'live') {
    saveProgress(true)
  }
}

function onVideoError() {
  error.value = 'Erreur de lecture vidéo'
  loading.value = false
}

function saveProgress(completed = false) {
  if (streamType.value === 'live') return
  catalog.saveProgress({
    item_type: streamType.value,
    item_id: streamId.value,
    progress_sec: Math.floor(currentTime.value),
    duration_sec: Math.floor(duration.value) || null,
    completed,
  })
}

function goBack() {
  saveProgress(false)
  router.back()
}

onMounted(async () => {
  await catalog.fetchHistory()
  await loadStream()

  // Auto-save every 15 seconds for VOD/series
  if (streamType.value !== 'live') {
    saveTimer = setInterval(() => saveProgress(false), 15000)
  }
})

onBeforeUnmount(() => {
  if (saveTimer) clearInterval(saveTimer)
  saveProgress(false)
  if (hlsInstance.value) {
    hlsInstance.value.destroy()
    hlsInstance.value = null
  }
})
</script>
