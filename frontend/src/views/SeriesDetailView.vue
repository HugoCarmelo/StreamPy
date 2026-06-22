<template>
  <div class="series-detail">
    <!-- Back -->
    <button class="btn-back" @click="router.back()">
      <span>←</span> Retour
    </button>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner" />
      <p>Chargement de la série...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="loadSeriesInfo">Réessayer</button>
    </div>

    <!-- Content -->
    <template v-else-if="seriesInfo">
      <!-- Hero -->
      <div class="hero" :style="heroStyle">
        <div class="hero-overlay" />
        <div class="hero-content">
          <img
            v-if="seriesInfo.info?.cover"
            :src="seriesInfo.info.cover"
            :alt="seriesInfo.info.name"
            class="hero-poster"
            @error="onPosterError"
          />
          <div class="hero-meta">
            <h1>{{ seriesInfo.info?.name || 'Série inconnue' }}</h1>
            <div class="hero-tags">
              <span v-if="seriesInfo.info?.genre" class="tag">{{ seriesInfo.info.genre }}</span>
              <span v-if="seriesInfo.info?.releaseDate" class="tag">{{ seriesInfo.info.releaseDate }}</span>
              <span class="tag">{{ seasonCount }} saison{{ seasonCount > 1 ? 's' : '' }}</span>
            </div>
            <p v-if="seriesInfo.info?.plot" class="hero-plot">{{ seriesInfo.info.plot }}</p>
            <p v-if="seriesInfo.info?.cast" class="hero-cast">
              <strong>Casting :</strong> {{ seriesInfo.info.cast }}
            </p>
            <!-- Favorite -->
            <button class="btn-favorite" @click="toggleFavorite">
              {{ isFavorite ? '★ Favori' : '☆ Ajouter aux favoris' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Season Tabs -->
      <div class="seasons-section">
        <div class="season-tabs">
          <button
            v-for="season in sortedSeasons"
            :key="season"
            :class="['season-tab', { active: selectedSeason === season }]"
            @click="selectedSeason = season"
          >
            Saison {{ season }}
          </button>
        </div>

        <!-- Episodes -->
        <div class="episodes-grid">
          <div
            v-for="episode in currentEpisodes"
            :key="episode.id"
            class="episode-card"
            @click="playEpisode(episode)"
          >
            <!-- Thumbnail -->
            <div class="episode-thumb">
              <img
                v-if="episode.info?.movie_image"
                :src="episode.info.movie_image"
                :alt="episode.title"
                @error="(e) => e.target.style.display='none'"
              />
              <div class="episode-play-icon">▶</div>
              <!-- Progress bar -->
              <div
                v-if="getProgress(episode.id)"
                class="episode-progress"
                :style="{ width: getProgressPercent(episode.id) + '%' }"
              />
            </div>
            <!-- Info -->
            <div class="episode-info">
              <span class="episode-num">E{{ episode.episode_num }}</span>
              <p class="episode-title">{{ episode.title || `Épisode ${episode.episode_num}` }}</p>
              <span v-if="episode.info?.duration" class="episode-duration">
                {{ episode.info.duration }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCatalogStore } from '@/stores/catalog'

const route = useRoute()
const router = useRouter()
const catalog = useCatalogStore()

const seriesId = computed(() => Number(route.params.id))
const seriesInfo = ref(null)
const loading = ref(true)
const error = ref(null)
const selectedSeason = ref(null)

// ── Computed ────────────────────────────────────────────────────────────────

const sortedSeasons = computed(() => {
  if (!seriesInfo.value?.episodes) return []
  return Object.keys(seriesInfo.value.episodes).sort((a, b) => Number(a) - Number(b))
})

const seasonCount = computed(() => sortedSeasons.value.length)

const currentEpisodes = computed(() => {
  if (!selectedSeason.value || !seriesInfo.value?.episodes) return []
  return seriesInfo.value.episodes[selectedSeason.value] || []
})

const heroStyle = computed(() => {
  const cover = seriesInfo.value?.info?.cover
  if (!cover) return {}
  return { '--hero-bg': `url(${cover})` }
})

const isFavorite = computed(() => catalog.isFavorite('series', seriesId.value))

// ── Methods ─────────────────────────────────────────────────────────────────

async function loadSeriesInfo() {
  loading.value = true
  error.value = null
  try {
    const data = await catalog.fetchSeriesInfo(seriesId.value)
    seriesInfo.value = data
    const seasons = Object.keys(data.episodes || {}).sort((a, b) => Number(a) - Number(b))
    if (seasons.length) selectedSeason.value = seasons[0]
  } catch (e) {
    error.value = 'Impossible de charger les informations de la série.'
  } finally {
    loading.value = false
  }
}

async function playEpisode(episode) {
  // episode.id = l'id de l'épisode (stream_id pour la requête series)
  const episodeId = episode.id
  const ext = episode.container_extension || episode.info?.container_extension || 'mp4'
  // Naviguer vers le player avec type=series, id=episodeId et ext en query
  router.push({
    name: 'Player',
    params: { type: 'series', id: String(episodeId) },
    query: { ext },
  })
}

async function toggleFavorite() {
  const info = seriesInfo.value?.info
  if (isFavorite.value) {
    await catalog.removeFavorite('series', seriesId.value)
  } else {
    await catalog.addFavorite({
      item_type: 'series',
      item_id: seriesId.value,
      item_name: info?.name || 'Série',
      item_logo: info?.cover || null,
    })
  }
}

function getProgress(episodeId) {
  return catalog.history.find(h => h.item_type === 'series' && h.item_id === episodeId)
}

function getProgressPercent(episodeId) {
  const h = getProgress(episodeId)
  if (!h || !h.duration_sec) return 0
  return Math.min(100, Math.round((h.progress_sec / h.duration_sec) * 100))
}

function onPosterError(e) {
  e.target.style.display = 'none'
}

onMounted(loadSeriesInfo)
</script>

<style scoped>
.series-detail {
  min-height: 100vh;
  background: #0f0f0f;
  color: #fff;
}

.btn-back {
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 100;
  background: rgba(0,0,0,0.6);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  backdrop-filter: blur(8px);
}
.btn-back:hover { background: rgba(255,255,255,0.15); }

/* ── Hero ── */
.hero {
  position: relative;
  min-height: 60vh;
  background-image: var(--hero-bg);
  background-size: cover;
  background-position: center top;
  display: flex;
  align-items: flex-end;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    rgba(15,15,15,0.3) 0%,
    rgba(15,15,15,0.9) 70%,
    #0f0f0f 100%
  );
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 2rem;
  padding: 2rem;
  align-items: flex-end;
  width: 100%;
}

.hero-poster {
  width: 140px;
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.6);
  flex-shrink: 0;
}

.hero-meta { flex: 1; }

.hero-meta h1 {
  font-size: clamp(1.4rem, 4vw, 2.4rem);
  font-weight: 700;
  margin: 0 0 0.5rem;
}

.hero-tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.tag {
  background: rgba(255,255,255,0.12);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.hero-plot {
  color: #ccc;
  font-size: 0.9rem;
  line-height: 1.5;
  max-width: 700px;
  margin-bottom: 0.5rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hero-cast {
  font-size: 0.82rem;
  color: #aaa;
  margin-bottom: 1rem;
}

.btn-favorite {
  background: rgba(255,200,0,0.15);
  border: 1px solid rgba(255,200,0,0.5);
  color: #ffc800;
  padding: 0.5rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.2s;
}
.btn-favorite:hover { background: rgba(255,200,0,0.25); }

/* ── Seasons ── */
.seasons-section {
  padding: 0 1.5rem 4rem;
}

.season-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.season-tab {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: #ccc;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}
.season-tab:hover { background: rgba(255,255,255,0.15); }
.season-tab.active {
  background: #e50914;
  border-color: #e50914;
  color: #fff;
  font-weight: 600;
}

/* ── Episodes ── */
.episodes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.episode-card {
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.episode-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}

.episode-thumb {
  position: relative;
  aspect-ratio: 16/9;
  background: #2a2a2a;
  overflow: hidden;
}

.episode-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.episode-play-icon {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  opacity: 0;
  background: rgba(0,0,0,0.4);
  transition: opacity 0.2s;
}
.episode-card:hover .episode-play-icon { opacity: 1; }

.episode-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: #e50914;
}

.episode-info {
  padding: 0.6rem 0.75rem;
}

.episode-num {
  font-size: 0.72rem;
  color: #e50914;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.episode-title {
  font-size: 0.85rem;
  margin: 0.2rem 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.episode-duration {
  font-size: 0.75rem;
  color: #888;
}

/* ── States ── */
.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
  color: #888;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #e50914;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ── */
@media (max-width: 640px) {
  .hero-content { flex-direction: column; align-items: flex-start; }
  .hero-poster { width: 100px; }
  .episodes-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
}
</style>
