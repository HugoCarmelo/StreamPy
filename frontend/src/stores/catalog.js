import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useCatalogStore = defineStore('catalog', () => {
  // Live
  const liveCategories = ref([])
  const liveStreams = ref([])

  // VOD
  const vodCategories = ref([])
  const vodStreams = ref([])

  // Series
  const seriesCategories = ref([])
  const seriesList = ref([])

  // Favorites
  const favorites = ref([])

  // History
  const history = ref([])

  // Loading / error
  const loading = ref(false)
  const error = ref(null)

  // -------------------------------------------------------------------------
  // Live
  // -------------------------------------------------------------------------
  async function fetchLiveCategories() {
    const { data } = await api.get('/catalog/live/categories')
    liveCategories.value = data
  }

  async function fetchLiveStreams(categoryId = null) {
    loading.value = true
    error.value = null
    try {
      const params = categoryId ? { category_id: categoryId } : {}
      const { data } = await api.get('/catalog/live/streams', { params })
      liveStreams.value = data
    } catch (e) {
      error.value = e?.response?.data?.detail || 'Erreur chargement Live TV'
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // VOD
  // -------------------------------------------------------------------------
  async function fetchVodCategories() {
    const { data } = await api.get('/catalog/vod/categories')
    vodCategories.value = data
  }

  async function fetchVodStreams(categoryId = null) {
    loading.value = true
    error.value = null
    try {
      const params = categoryId ? { category_id: categoryId } : {}
      const { data } = await api.get('/catalog/vod/streams', { params })
      vodStreams.value = data
    } catch (e) {
      error.value = e?.response?.data?.detail || 'Erreur chargement VOD'
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // Series
  // -------------------------------------------------------------------------
  async function fetchSeriesCategories() {
    const { data } = await api.get('/catalog/series/categories')
    seriesCategories.value = data
  }

  async function fetchSeries(categoryId = null) {
    loading.value = true
    error.value = null
    try {
      const params = categoryId ? { category_id: categoryId } : {}
      const { data } = await api.get('/catalog/series', { params })
      seriesList.value = data
    } catch (e) {
      error.value = e?.response?.data?.detail || 'Erreur chargement Séries'
    } finally {
      loading.value = false
    }
  }

  // -------------------------------------------------------------------------
  // Stream URL
  // -------------------------------------------------------------------------
  async function getStreamUrl(streamType, streamId) {
    const { data } = await api.get('/catalog/stream-url', {
      params: { stream_type: streamType, stream_id: streamId },
    })
    return data.url
  }

  // -------------------------------------------------------------------------
  // Favorites
  // -------------------------------------------------------------------------
  async function fetchFavorites() {
    const { data } = await api.get('/favorites')
    favorites.value = data
  }

  async function addFavorite(item) {
    await api.post('/favorites', item)
    await fetchFavorites()
  }

  async function removeFavorite(itemType, itemId) {
    await api.delete(`/favorites/${itemType}/${itemId}`)
    favorites.value = favorites.value.filter(
      (f) => !(f.item_type === itemType && f.item_id === itemId)
    )
  }

  function isFavorite(itemType, itemId) {
    return favorites.value.some((f) => f.item_type === itemType && f.item_id === itemId)
  }

  // -------------------------------------------------------------------------
  // History
  // -------------------------------------------------------------------------
  async function fetchHistory() {
    const { data } = await api.get('/history')
    history.value = data
  }

  async function saveProgress(payload) {
    await api.put('/history', payload)
  }

  return {
    liveCategories, liveStreams,
    vodCategories, vodStreams,
    seriesCategories, seriesList,
    favorites, history,
    loading, error,
    fetchLiveCategories, fetchLiveStreams,
    fetchVodCategories, fetchVodStreams,
    fetchSeriesCategories, fetchSeries,
    getStreamUrl,
    fetchFavorites, addFavorite, removeFavorite, isFavorite,
    fetchHistory, saveProgress,
  }
})
