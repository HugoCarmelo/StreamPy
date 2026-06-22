import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'ProfileSelect',
    component: () => import('@/views/ProfileSelectView.vue'),
  },
  {
    path: '/pin/:profileId',
    name: 'PinEntry',
    component: () => import('@/views/PinEntryView.vue'),
    props: true,
  },
  {
    path: '/setup',
    name: 'ProfileSetup',
    component: () => import('@/views/ProfileSetupView.vue'),
  },
  {
    path: '/home',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true },
  },
   {
    path: '/series/:id',          // ← NOUVEAU
    name: 'series-detail',
    component: () => import('@/views/SeriesDetailView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/player/:type/:id',
    name: 'player',
    component: () => import('@/views/PlayerView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    // Alias so HomeView can navigate to "profiles"
    path: '/',
    name: 'profiles',
    component: () => import('@/views/ProfileSelectView.vue'),
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'ProfileSelect' }
  }
})

export default router
