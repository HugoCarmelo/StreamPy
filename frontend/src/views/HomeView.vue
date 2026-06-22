<template>
  <div class="min-h-screen bg-gray-950 text-white flex flex-col">
    <!-- Top bar -->
    <header class="flex items-center justify-between px-6 py-4 bg-gray-900 border-b border-gray-800">
      <div class="flex items-center gap-4">
        <span class="text-2xl font-bold text-indigo-400 tracking-tight">StreamPy</span>
        <!-- Tabs -->
        <nav class="flex gap-1 ml-4">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="switchTab(tab.id)"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'bg-indigo-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>
      <div class="flex items-center gap-3">
        <!-- Search -->
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Rechercher…"
            class="bg-gray-800 text-sm text-white placeholder-gray-500 rounded-lg px-4 py-2 pr-10 w-56 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <svg class="absolute right-3 top-2.5 w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-4.35-4.35M17 11A6 6 0 111 11a6 6 0 0116 0z"/>
          </svg>
        </div>
        <!-- Profile -->
        <button @click="goToProfiles" class="flex items-center gap-2 text-sm text-gray-400 hover:text-white">
          <div class="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center font-bold text-sm">
            {{ profileInitial }}
          </div>
        </button>
      </div>
    </header>

    <div class="flex flex-1 overflow-hidden">
      <!-- Sidebar categories -->
      <aside class="w-52 bg-gray-900 border-r border-gray-800 overflow-y-auto flex-shrink-0">
        <div class="p-3">
          <button
            @click="selectCategory(null)"
            :class="[
              'w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors',
              selectedCategory === null
                ? 'bg-indigo-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            ]"
          >
            Tout
          </button>
          <button
            v-for="cat in currentCategories"
            :key="cat.category_id"
            @click="selectCategory(cat.category_id)"
            :class="[
              'w-full text-left px-3 py-2 rounded-lg text-sm mb-1 transition-colors truncate',
              selectedCategory === cat.category_id
                ? 'bg-indigo-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            ]"
          >
            {{ cat.category_name }}
          </button>
        </div>
      </aside>

      <!-- Main content -->
      <main class="flex-1 overflow-y-auto p-6">
        <!-- Error -->
        <div v-if="catalog.error" class="mb-4 bg-red-900/50 border border-red-700 text-red-300 rounded-lg px-4 py-3 text-sm">
          {{ catalog.error }}
        </div>

        <!-- Loading skeleton -->
        <div v-if="catalog.loading" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          <div v-for="n in 18" :key="n" class="animate-pulse">
            <div class="bg-gray-800 rounded-lg aspect-video mb-2"></div>
            <div class="bg-gray-800 rounded h-3 w-3/4"></div>
          </div>
        </div>

        <!-- Grid -->
        <div v-else class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
          <div
            v-for="item in filteredItems"
            :key="item.stream_id || item.series_id"
            @click="playItem(item)"
            class="group cursor-pointer"
          >
            <div class="relative bg-gray-800 rounded-lg overflow-hidden aspect-video mb-2 transition-transform group-hover:scale-105 group-hover:ring-2 group-hover:ring-indigo-500">
              <img
                v-if="item.stream_icon || item.cover"
                :src="item.stream_icon || item.cover"
                :alt="item.name"
                class="w-full h-full object-cover"
                loading="lazy"
                @error="$event.target.style.display='none'"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-600">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 10l4.553-2.276A1 1 0 0121 8.723v6.554a1 1 0 01-1.447.894L15 14M3 8a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2V8z"/>
                </svg>
              </div>
              <!-- Live badge -->
              <span v-if="activeTab === 'live'" class="absolute top-2 left-2 bg-red-600 text-white text-xs px-1.5 py-0.5 rounded font-medium">
                LIVE
              </span>
              <!-- Favorite btn -->
              <button
                @click.stop="toggleFavorite(item)"
                class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 rounded-full p-1"
              >
                <svg class="w-4 h-4" :class="isFav(item) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/>
                </svg>
              </button>
              <!-- Progress bar -->
              <div v-if="getProgress(item)" class="absolute bottom-0 left-0 right-0 h-1 bg-gray-700">
                <div class="h-full bg-indigo-500" :style="{ width: getProgress(item) + '%' }"></div>
              </div>
            </div>
            <p class="text-xs text-gray-300 truncate leading-tight">{{ item.name }}</p>
          </div>
        </div>

        <!-- Empty state -->
        <div v-if="!catalog.loading && filteredItems.length === 0" class="flex flex-col items-center justify-center py-24 text-gray-600">
          <svg class="w-16 h-16 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z"/>
          </svg>
          <p class="text-sm">Aucun contenu trouvé</p>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'
import { useProfilesStore } from '@/stores/profiles'

const router = useRouter()
const catalog = useCatalogStore()
const profilesStore = useProfilesStore()

const tabs = [
  { id: 'live', label: 'Live TV' },
  { id: 'vod', label: 'Films' },
  { id: 'series', label: 'Séries' },
]

const activeTab = ref('live')
const selectedCategory = ref(null)
const searchQuery = ref('')

const profileInitial = computed(() => {
  const name = profilesStore.activeProfile?.name || '?'
  return name[0].toUpperCase()
})

const currentCategories = computed(() => {
  if (activeTab.value === 'live') return catalog.liveCategories
  if (activeTab.value === 'vod') return catalog.vodCategories
  return catalog.seriesCategories
})

const currentItems = computed(() => {
  if (activeTab.value === 'live') return catalog.liveStreams
  if (activeTab.value === 'vod') return catalog.vodStreams
  return catalog.seriesList
})

const filteredItems = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return currentItems.value
  return currentItems.value.filter((item) =>
    (item.name || '').toLowerCase().includes(q)
  )
})

function getItemType(item) {
  if (activeTab.value === 'live') return 'live'
  if (activeTab.value === 'vod') return 'vod'
  return 'series'
}

function getItemId(item) {
  return item.stream_id || item.series_id
}

function isFav(item) {
  return catalog.isFavorite(getItemType(item), getItemId(item))
}

function getProgress(item) {
  const h = catalog.history.find(
    (e) => e.item_type === getItemType(item) && e.item_id === getItemId(item)
  )
  if (!h || !h.duration_sec || h.duration_sec === 0) return null
  return Math.min(Math.round((h.progress_sec / h.duration_sec) * 100), 100)
}

async function toggleFavorite(item) {
  const type = getItemType(item)
  const id = getItemId(item)
  if (catalog.isFavorite(type, id)) {
    await catalog.removeFavorite(type, id)
  } else {
    await catalog.addFavorite({
      item_type: type,
      item_id: id,
      item_name: item.name,
      item_logo: item.stream_icon || item.cover || null,
    })
  }
}

function playItem(item) {
  const type = getItemType(item)
  const id = getItemId(item)
  router.push({ name: 'player', params: { type, id } })
}

async function switchTab(tabId) {
  activeTab.value = tabId
  selectedCategory.value = null
  searchQuery.value = ''
  await loadContent()
}

async function selectCategory(catId) {
  selectedCategory.value = catId
  await loadContent(catId)
}

async function loadContent(catId = null) {
  if (activeTab.value === 'live') await catalog.fetchLiveStreams(catId)
  else if (activeTab.value === 'vod') await catalog.fetchVodStreams(catId)
  else await catalog.fetchSeries(catId)
}

function goToProfiles() {
  router.push({ name: 'profiles' })
}

onMounted(async () => {
  // Load all categories (fast, cached)
  await Promise.all([
    catalog.fetchLiveCategories(),
    catalog.fetchVodCategories(),
    catalog.fetchSeriesCategories(),
    catalog.fetchFavorites(),
    catalog.fetchHistory(),
  ])
  // Load initial streams
  await catalog.fetchLiveStreams()
})
</script>
