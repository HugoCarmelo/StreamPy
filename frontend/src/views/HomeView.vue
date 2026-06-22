<template>
  <div class="min-h-screen bg-gray-950 flex flex-col">
    <!-- Navbar -->
    <header class="flex items-center justify-between px-8 py-4 bg-gray-900 shadow">
      <span class="text-xl font-bold text-white">StreamPy</span>
      <button
        @click="handleLogout"
        class="text-sm text-gray-400 hover:text-white transition"
      >
        Changer de profil
      </button>
    </header>

    <!-- Content placeholder -->
    <main class="flex-1 flex flex-col items-center justify-center text-center p-8">
      <p class="text-5xl mb-4">🎬</p>
      <h2 class="text-2xl font-semibold text-white mb-2">Bienvenue sur StreamPy</h2>
      <p class="text-gray-400 max-w-sm">
        L'interface de catalogue et de lecture IPTV est en cours de développement.<br />
        Les modules Live TV, VOD et Séries arriveront bientôt.
      </p>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

async function handleLogout() {
  await auth.logout()
  router.push({ name: 'ProfileSelect' })
}
</script>
