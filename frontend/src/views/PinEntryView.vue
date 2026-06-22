<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-gray-950 p-8">
    <h2 class="text-2xl font-semibold text-white mb-2">Entrer le PIN</h2>
    <p class="text-gray-400 mb-8">Profil sélectionné</p>

    <!-- PIN dots display -->
    <div class="flex gap-3 mb-8">
      <div
        v-for="i in 4"
        :key="i"
        class="w-4 h-4 rounded-full border-2 transition"
        :class="pin.length >= i ? 'bg-brand-500 border-brand-500' : 'border-gray-600'"
      />
    </div>

    <!-- Numpad -->
    <div class="grid grid-cols-3 gap-3 mb-4">
      <button
        v-for="digit in ['1','2','3','4','5','6','7','8','9','','0','⌫']"
        :key="digit"
        @click="handleKey(digit)"
        :disabled="digit === ''"
        class="w-16 h-16 rounded-xl text-xl font-medium transition
               bg-gray-800 text-white hover:bg-gray-700 active:scale-95
               disabled:invisible"
      >
        {{ digit }}
      </button>
    </div>

    <p v-if="errorMsg" class="text-red-400 text-sm mt-2">{{ errorMsg }}</p>

    <button
      @click="$router.push('/')"
      class="mt-6 text-sm text-gray-500 hover:text-gray-300"
    >
      ← Retour
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({ profileId: { type: String, required: true } })

const router = useRouter()
const auth = useAuthStore()

const pin = ref('')
const errorMsg = ref('')

function handleKey(key) {
  if (key === '⌫') {
    pin.value = pin.value.slice(0, -1)
    errorMsg.value = ''
    return
  }
  if (pin.value.length >= 4) return
  pin.value += key
  if (pin.value.length === 4) submitPin()
}

async function submitPin() {
  try {
    await auth.login(Number(props.profileId), pin.value)
    router.push({ name: 'Live' })
  } catch {
    errorMsg.value = 'PIN incorrect'
    pin.value = ''
  }
}
</script>
