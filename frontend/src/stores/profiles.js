import { defineStore } from 'pinia'
import { ref } from 'vue'
import { profilesApi } from '@/api/client'

export const useProfilesStore = defineStore('profiles', () => {
  const profiles = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function fetchProfiles() {
    loading.value = true
    error.value = null
    try {
      const { data } = await profilesApi.list()
      profiles.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || 'Failed to load profiles'
    } finally {
      loading.value = false
    }
  }

  async function createProfile(payload) {
    const { data } = await profilesApi.create(payload)
    await fetchProfiles()
    return data
  }

  async function deleteProfile(id) {
    await profilesApi.delete(id)
    profiles.value = profiles.value.filter((p) => p.id !== id)
  }

  return { profiles, loading, error, fetchProfiles, createProfile, deleteProfile }
})
