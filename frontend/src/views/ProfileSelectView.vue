<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-950 p-8">
    <h1 class="text-4xl font-bold text-white mb-2">StreamPy</h1>
    <p class="text-gray-400 mb-10">Qui regarde ?</p>

    <div v-if="store.loading" class="text-gray-500">Chargement…</div>
    <div v-else-if="store.error" class="text-red-400">{{ store.error }}</div>

    <div v-else class="flex flex-wrap gap-6 justify-center max-w-2xl">
      <button
        v-for="profile in store.profiles"
        :key="profile.id"
        @click="selectProfile(profile)"
        class="flex flex-col items-center gap-2 group"
      >
        <div
          class="w-24 h-24 rounded-xl bg-brand-700 flex items-center justify-center text-3xl
                 group-hover:ring-4 ring-brand-500 transition"
        >
          {{ profile.avatar || '👤' }}
        </div>
        <span class="text-sm text-gray-300 group-hover:text-white">{{ profile.name }}</span>
        <span v-if="profile.has_pin" class="text-xs text-gray-500">🔒</span>
      </button>

      <!-- Add profile -->
      <button
        @click="$router.push('/setup')"
        class="flex flex-col items-center gap-2 group"
      >
        <div
          class="w-24 h-24 rounded-xl border-2 border-dashed border-gray-700 flex items-center
                 justify-center text-3xl text-gray-600 group-hover:border-brand-500
                 group-hover:text-brand-500 transition"
        >
          +
        </div>
        <span class="text-sm text-gray-500 group-hover:text-gray-300">Ajouter</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProfilesStore } from '@/stores/profiles'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const store = useProfilesStore()
const auth = useAuthStore()

onMounted(() => store.fetchProfiles())

async function selectProfile(profile) {
  if (profile.has_pin) {
    router.push({ name: 'PinEntry', params: { profileId: profile.id } })
  } else {
    await auth.login(profile.id)
    router.push({ name: 'Home' })
  }
}
</script>
