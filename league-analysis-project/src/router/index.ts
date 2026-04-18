import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../pages/Dashboard.vue'

const routes = [
  { path: '/', component: Dashboard },
  { path: '/members', component: () => import('../pages/MemberList.vue') },
  { path: '/team-builder', component: () => import('../pages/TeamBuilder.vue') },
  { path: '/analysis', component: () => import('../pages/DataAnalysis.vue') },
  { path: '/skills', component: () => import('../pages/SkillCalc.vue') }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
