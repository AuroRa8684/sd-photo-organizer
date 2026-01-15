/**
 * Vue Router 路由配置
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Import',
    component: () => import('@/pages/ImportPage.vue'),
    meta: { title: '导入照片' }
  },
  {
    path: '/gallery',
    name: 'Gallery',
    component: () => import('@/pages/GalleryPage.vue'),
    meta: { title: '照片墙' }
  },
  {
    path: '/summary',
    name: 'Summary',
    component: () => import('@/pages/SummaryPage.vue'),
    meta: { title: '拍摄总结' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫 - 更新页面标题
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'PhotoFlow'} - 智能照片整理与拍摄`
  next()
})

export default router
