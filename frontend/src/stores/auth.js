import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const profileId = ref(
    localStorage.getItem('profile_id') ? Number(localStorage.getItem('profile_id')) : null
  )

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(id, pin = null) {
    const { data } = await authApi.login(id, pin)
    accessToken.value = data.access_token
    refreshToken.value = data.refresh_token
    profileId.value = data.profile_id
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('refresh_token', data.refresh_token)
    localStorage.setItem('profile_id', String(data.profile_id))
  }

  async function logout() {
    if (refreshToken.value) {
      try {
        await authApi.logout(refreshToken.value)
      } catch {
        // ignore — token may already be invalid
      }
    }
    accessToken.value = null
    refreshToken.value = null
    profileId.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('profile_id')
  }

  return { accessToken, refreshToken, profileId, isAuthenticated, login, logout }
})
