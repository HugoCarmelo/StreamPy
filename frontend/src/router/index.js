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
  // Redirige /home vers /live (compat)
  {
    path: '/home',
    redirect: '/live',
  },
  {
    path: '/series/:id',
    name: 'SeriesDetail',
    component: () => import('@/views/SeriesDetailView.vue'),
    props: true,
    meta: { requiresAuth: true },
  },
  {
    path: '/player',
    name: 'Player',
    component: () => import('@/views/PlayerView.vue'),
    meta: { requiresAuth: true },
  },
  {
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
