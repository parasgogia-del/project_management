import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
    meta: { public: true },
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
      },
      {
        path: 'projects',
        name: 'ProjectList',
        component: () => import('@/pages/manager/ProjectList.vue'),
      },
      {
        path: 'project/new',
        name: 'ProjectCreate',
        component: () => import('@/pages/manager/ProjectForm.vue'),
      },
      {
        path: 'project/:id',
        name: 'ProjectDetail',
        component: () => import('@/pages/manager/ProjectDetail.vue'),
      },
      {
        path: 'project/:id/edit',
        name: 'ProjectEdit',
        component: () => import('@/pages/manager/ProjectForm.vue'),
      },
      {
        path: 'project/:id/gantt',
        name: 'GanttChart',
        component: () => import('@/pages/manager/GanttChart.vue'),
      },
      {
        path: 'project/:id/deliverables',
        name: 'DeliverableList',
        component: () => import('@/pages/manager/DeliverableList.vue'),
      },
      {
        path: 'project/:id/tasks',
        name: 'TaskList',
        component: () => import('@/pages/manager/TaskList.vue'),
      },
      {
        path: 'project/:id/reports',
        name: 'Reports',
        component: () => import('@/pages/manager/Reports.vue'),
      },
      {
        path: 'deliverable/:id',
        name: 'DeliverableDetail',
        component: () => import('@/pages/manager/DeliverableDetail.vue'),
      },
      {
        path: 'task/:id',
        name: 'TaskDetail',
        component: () => import('@/pages/manager/TaskDetail.vue'),
      },
      // Member portal
      {
        path: 'member/dashboard',
        name: 'MemberDashboard',
        component: () => import('@/pages/member/Dashboard.vue'),
      },
      {
        path: 'member/task/:id',
        name: 'MemberTask',
        component: () => import('@/pages/member/TaskPage.vue'),
      },
      // Client portal
      {
        path: 'client/dashboard',
        name: 'ClientDashboard',
        component: () => import('@/pages/client/Dashboard.vue'),
      },
      {
        path: 'client/project/:id',
        name: 'ClientProject',
        component: () => import('@/pages/client/ProjectView.vue'),
      },
      {
        path: 'client/deliverable/:id',
        name: 'ClientDeliverable',
        component: () => import('@/pages/client/DeliverableView.vue'),
      },
      // Vendor portal
      {
        path: 'vendor/dashboard',
        name: 'VendorDashboard',
        component: () => import('@/pages/vendor/Dashboard.vue'),
      },
      {
        path: 'vendor/task/:id',
        name: 'VendorTask',
        component: () => import('@/pages/vendor/TaskPage.vue'),
      },
      {
        path: 'vendor/deliverable/:id',
        name: 'VendorDeliverable',
        component: () => import('@/pages/vendor/DeliverableView.vue'),
      },
    ],
  },
]

let router = createRouter({
  history: createWebHistory('/project_management'),
  routes,
})

export default router
