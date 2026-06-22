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
  // Sections principales — chacune a sa propre URL
  {
    path: '/live',
    name: 'Live',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/vod',
    name: 'VOD',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/series',
    name: 'Series',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true },
  },
  // Fiche détail d'une série
  {
    path: '/series/:id(\\d+)',
    name: 'SeriesDetail',
    component: () => import('@/views/SeriesDetailView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  // Player : /player/:type/:id  (ex: /player/vod/12345 ou /player/live/67890)
  {
    path: '/player/:type/:id',
    name: 'Player',
    component: () => import('@/views/PlayerView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  // Compat : /home redirige vers /live
  {
    path: '/home',
    redirect: '/live',
  },
  // Catch-all
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
