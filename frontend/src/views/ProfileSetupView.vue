<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-950 p-8">
    <div class="w-full max-w-md bg-gray-900 rounded-2xl p-8">
      <h2 class="text-2xl font-semibold text-white mb-6">Nouveau profil</h2>

      <form @submit.prevent="submit" class="flex flex-col gap-4">
        <!-- Name -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">Nom</label>
          <input
            v-model="form.name"
            type="text"
            required
            class="w-full bg-gray-800 text-white rounded-lg px-4 py-2 outline-none
                   focus:ring-2 ring-brand-500"
          />
        </div>

        <!-- Avatar emoji -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">Avatar (emoji)</label>
          <input
            v-model="form.avatar"
            type="text"
            maxlength="2"
            placeholder="👤"
            class="w-full bg-gray-800 text-white rounded-lg px-4 py-2 outline-none
                   focus:ring-2 ring-brand-500"
          />
        </div>

        <!-- Server URL -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">URL du serveur Xtream</label>
          <input
            v-model="form.server_url"
            type="url"
            required
            placeholder="http://iptv.example.com:8080"
            class="w-full bg-gray-800 text-white rounded-lg px-4 py-2 outline-none
                   focus:ring-2 ring-brand-500"
          />
        </div>

        <!-- Username -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">Identifiant</label>
          <input
            v-model="form.username"
            type="text"
            required
            class="w-full bg-gray-800 text-white rounded-lg px-4 py-2 outline-none
                   focus:ring-2 ring-brand-500"
          />
        </div>

        <!-- Password -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">Mot de passe</label>
          <input
            v-model="form.password"
            type="password"
            required
            class="w-full bg-gray-800 text-white rounded-lg px-4 py-2 outline-none
                   focus:ring-2 ring-brand-500"
          />
        </div>

        <!-- PIN (optional) -->
        <div>
          <label class="block text-sm text-gray-400 mb-1">PIN (optionnel, 4 chiffres)</label>
          <input
            v-model="form.pin"
            type="password"
            maxlength="4"
            inputmode="numeric"
            placeholder="••••"
            class="w-full bg-gray-800 text-white rounded-lg px-4 py-2 outline-none
                   focus:ring-2 ring-brand-500"
          />
        </div>

        <p v-if="errorMsg" class="text-red-400 text-sm">{{ errorMsg }}</p>

        <div class="flex gap-3 mt-2">
          <button
            type="button"
            @click="$router.push('/')"
            class="flex-1 py-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700"
          >
            Annuler
          </button>
          <button
            type="submit"
            :disabled="saving"
            class="flex-1 py-2 rounded-lg bg-brand-600 text-white hover:bg-brand-500
                   disabled:opacity-50"
          >
            {{ saving ? 'Création…' : 'Créer' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProfilesStore } from '@/stores/profiles'

const router = useRouter()
const store = useProfilesStore()

const saving = ref(false)
const errorMsg = ref('')

const form = ref({
  name: '',
  avatar: '',
  server_url: '',
  username: '',
  password: '',
  pin: '',
})

async function submit() {
  saving.value = true
  errorMsg.value = ''
  try {
    const payload = { ...form.value }
    if (!payload.pin) delete payload.pin
    if (!payload.avatar) delete payload.avatar
    await store.createProfile(payload)
    router.push('/')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Erreur lors de la création'
  } finally {
    saving.value = false
  }
}
</script>
