import { createRouter, createWebHistory } from 'vue-router'
import { sessionUser, getPortal } from '@/data/session'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/pages/Register.vue'),
    meta: { public: true },
  },
  {
    path: '/no-access',
    name: 'NoAccess',
    component: () => import('@/pages/NoAccess.vue'),
  },
  // Manager routes
  {
    path: '/',
    component: () => import('@/components/layout/AppLayout.vue'),
    children: [
      {
        path: '',
        name: 'ManagerDashboard',
        component: () => import('@/pages/manager/Dashboard.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('@/pages/manager/ProjectList.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'deliverables',
        name: 'AllDeliverables',
        component: () => import('@/pages/manager/AllDeliverables.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'tasks',
        name: 'AllTasks',
        component: () => import('@/pages/manager/AllTasks.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'project/new',
        name: 'ProjectCreate',
        component: () => import('@/pages/manager/ProjectForm.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'project/:id',
        name: 'ProjectDetail',
        component: () => import('@/pages/manager/ProjectDetail.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'project/:id/edit',
        name: 'ProjectEdit',
        component: () => import('@/pages/manager/ProjectForm.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'project/:id/gantt',
        name: 'GanttChart',
        component: () => import('@/pages/manager/GanttChart.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'project/:id/deliverables',
        name: 'DeliverableList',
        component: () => import('@/pages/manager/DeliverableList.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'project/:id/tasks',
        name: 'TaskList',
        component: () => import('@/pages/manager/TaskList.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'project/:id/reports',
        name: 'Reports',
        component: () => import('@/pages/manager/Reports.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'deliverable/:id',
        name: 'DeliverableDetail',
        component: () => import('@/pages/manager/DeliverableDetail.vue'),
        meta: { roles: ['Project Manager'] },
      },
      {
        path: 'task/:id',
        name: 'TaskDetail',
        component: () => import('@/pages/manager/TaskDetail.vue'),
        meta: { roles: ['Project Manager'] },
      },
      // Member portal
      {
        path: 'member/dashboard',
        name: 'MemberDashboard',
        component: () => import('@/pages/member/Dashboard.vue'),
        meta: { roles: ['Project Manager', 'Project Member'] },
      },
      {
        path: 'member/project/:id',
        name: 'MemberProjectDetail',
        component: () => import('@/pages/member/ProjectDetail.vue'),
        meta: { roles: ['Project Manager', 'Project Member'] },
      },
      {
        path: 'member/task/:id',
        name: 'MemberTask',
        component: () => import('@/pages/member/TaskPage.vue'),
        meta: { roles: ['Project Manager', 'Project Member'] },
      },
      {
        path: 'member/deliverable/:id',
        name: 'MemberDeliverable',
        component: () => import('@/pages/member/DeliverableView.vue'),
        meta: { roles: ['Project Manager', 'Project Member'] },
      },
      // Client portal
      {
        path: 'client/dashboard',
        name: 'ClientDashboard',
        component: () => import('@/pages/client/Dashboard.vue'),
        meta: { roles: ['Project Manager', 'Client'] },
      },
      {
        path: 'client/project/:id',
        name: 'ClientProject',
        component: () => import('@/pages/client/ProjectView.vue'),
        meta: { roles: ['Project Manager', 'Client'] },
      },
      {
        path: 'client/task/:id',
        name: 'ClientTask',
        component: () => import('@/pages/client/TaskView.vue'),
        meta: { roles: ['Project Manager', 'Client'] },
      },
      {
        path: 'client/deliverable/:id',
        name: 'ClientDeliverable',
        component: () => import('@/pages/client/DeliverableView.vue'),
        meta: { roles: ['Project Manager', 'Client'] },
      },
      // Vendor portal
      {
        path: 'vendor/dashboard',
        name: 'VendorDashboard',
        component: () => import('@/pages/vendor/Dashboard.vue'),
        meta: { roles: ['Project Manager', 'Vendor'] },
      },
      {
        path: 'vendor/task/:id',
        name: 'VendorTask',
        component: () => import('@/pages/vendor/TaskPage.vue'),
        meta: { roles: ['Project Manager', 'Vendor'] },
      },
      {
        path: 'vendor/deliverable/:id',
        name: 'VendorDeliverable',
        component: () => import('@/pages/vendor/DeliverableView.vue'),
        meta: { roles: ['Project Manager', 'Vendor'] },
      },
    ],
  },
]

let router = createRouter({
  history: createWebHistory('/project_management'),
  routes,
})

router.beforeEach(async (to) => {
  if (!sessionUser.data) {
    try {
      await sessionUser.fetch()
    } catch (e) {
      console.error('Failed to fetch session', e)
    }
  }

  const data = sessionUser.data
  const isLoggedIn = !!(data && data.user && data.user !== 'Guest')
  const roles = data?.roles || []
  const portal = getPortal()

  if (!isLoggedIn) {
    if (to.meta.public) return true
    return '/login'
  }

  if (to.meta.public) {
    return portal || true
  }

  if (to.meta.roles && !to.meta.roles.some((r) => roles.includes(r))) {
    if (portal) return portal
    return to.path === '/no-access' ? true : '/no-access'
  }

  return true
})

export default router
