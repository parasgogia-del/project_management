<template>
  <div class="space-y-6">
    <!-- Page header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-sm text-gray-500 mt-0.5">Overview of your projects and tasks</p>
      </div>
      <Button route="/project/new" appearance="primary" icon-left="plus">
        New Project
      </Button>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      <div
        v-for="stat in stats"
        :key="stat.label"
        class="bg-white rounded-xl border border-gray-200 p-4"
      >
        <div class="flex items-center gap-2 mb-2">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center" :class="stat.bgColor">
            <feather-icon :name="stat.icon" class="w-4 h-4" :class="stat.iconColor" />
          </div>
        </div>
        <p class="text-2xl font-bold text-gray-900">{{ stat.value }}</p>
        <p class="text-xs text-gray-500 mt-0.5">{{ stat.label }}</p>
      </div>
    </div>

    <!-- Two-column layout -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Left: Project progress + Daily report -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Project Progress Overview -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold text-gray-800">Project Progress</h2>
            <router-link to="/projects" class="text-xs text-blue-600 hover:underline">View all</router-link>
          </div>
          <div v-if="projects.length === 0" class="text-center py-8">
            <p class="text-sm text-gray-400">No projects yet</p>
          </div>
          <div v-else class="space-y-4">
            <div
              v-for="project in projects.slice(0, 5)"
              :key="project.name"
              class="cursor-pointer hover:bg-gray-50 rounded-lg p-2 -mx-2 transition-colors"
              @click="$router.push(`/project/${project.name}`)"
            >
              <div class="flex items-center justify-between mb-1.5">
                <div class="min-w-0">
                  <p class="text-sm font-medium text-gray-800 truncate">{{ project.project_name }}</p>
                  <p class="text-xs text-gray-400">{{ project.client }}</p>
                </div>
                <Badge :label="project.status" :color-map="statusColorMap" />
              </div>
              <ProgressBar :value="project.progress || 0" />
            </div>
          </div>
        </div>

        <!-- Daily/Weekly Progress Report -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold text-gray-800">Progress Report</h2>
            <div class="flex gap-1 bg-gray-100 rounded-lg p-0.5">
              <Button
                appearance="minimal"
                :active="reportPeriod === 'daily'"
                @click="reportPeriod = 'daily'"
              >Daily</Button>
              <Button
                appearance="minimal"
                :active="reportPeriod === 'weekly'"
                @click="reportPeriod = 'weekly'"
              >Weekly</Button>
            </div>
          </div>

          <div v-if="report" class="grid grid-cols-4 gap-4">
            <div class="text-center p-3 bg-gray-50 rounded-lg">
              <p class="text-lg font-bold text-gray-900">{{ report.tasks.total }}</p>
              <p class="text-[10px] text-gray-500">Total Tasks</p>
            </div>
            <div class="text-center p-3 bg-green-50 rounded-lg">
              <p class="text-lg font-bold text-green-700">{{ report.tasks.completed }}</p>
              <p class="text-[10px] text-gray-500">Completed</p>
            </div>
            <div class="text-center p-3 bg-blue-50 rounded-lg">
              <p class="text-lg font-bold text-blue-700">{{ report.tasks.in_progress }}</p>
              <p class="text-[10px] text-gray-500">In Progress</p>
            </div>
            <div class="text-center p-3 bg-red-50 rounded-lg">
              <p class="text-lg font-bold text-red-600">{{ report.tasks.blocked }}</p>
              <p class="text-[10px] text-gray-500">Blocked</p>
            </div>
          </div>
          <div v-if="report" class="grid grid-cols-3 gap-4 mt-3">
            <div class="text-center p-3 bg-yellow-50 rounded-lg">
              <p class="text-lg font-bold text-yellow-700">{{ report.tasks.overdue }}</p>
              <p class="text-[10px] text-gray-500">Overdue</p>
            </div>
            <div class="text-center p-3 bg-purple-50 rounded-lg">
              <p class="text-lg font-bold text-purple-700">{{ report.time.total_hours?.toFixed(1) || 0 }}h</p>
              <p class="text-[10px] text-gray-500">Hours Logged</p>
            </div>
            <div class="text-center p-3 bg-indigo-50 rounded-lg">
              <p class="text-lg font-bold text-indigo-700">{{ report.completion_percentage || 0 }}%</p>
              <p class="text-[10px] text-gray-500">Completion</p>
            </div>
          </div>
          <LoadingIndicator v-else-if="reportLoading" class="mx-auto my-8 h-6 w-6 text-gray-400" />
        </div>

        <!-- Recent Tasks -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold text-gray-800">Recent Tasks</h2>
          </div>
          <div v-if="allTasks.length === 0" class="text-center py-6">
            <p class="text-sm text-gray-400">No tasks found</p>
          </div>
          <div v-else class="divide-y divide-gray-50">
            <div
              v-for="task in allTasks.slice(0, 8)"
              :key="task.name"
              class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
              @click="$router.push(`/task/${task.name}`)"
            >
              <div class="min-w-0 flex-1">
                <p class="text-sm font-medium text-gray-800 truncate">{{ task.title }}</p>
                <p class="text-xs text-gray-400">{{ task.project }}</p>
              </div>
              <div class="flex items-center gap-2 ml-4">
                <Badge :label="task.priority" :color-map="statusColorMap" />
                <Badge :label="task.status" :color-map="statusColorMap" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right column -->
      <div class="space-y-6">
        <!-- Quick Actions -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <h2 class="text-sm font-semibold text-gray-800 mb-4">Quick Actions</h2>
          <div class="space-y-2">
            <router-link
              to="/project/new"
              class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-blue-50 flex items-center justify-center">
                <feather-icon name="folder-plus" class="w-4 h-4 text-blue-600" />
              </div>
              <span class="text-sm text-gray-700">Create Project</span>
            </router-link>
            <router-link
              to="/projects"
              class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
                <feather-icon name="folder" class="w-4 h-4 text-green-600" />
              </div>
              <span class="text-sm text-gray-700">View Projects</span>
            </router-link>
            <router-link
              to="/member/dashboard"
              class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-purple-50 flex items-center justify-center">
                <feather-icon name="users" class="w-4 h-4 text-purple-600" />
              </div>
              <span class="text-sm text-gray-700">Member Portal</span>
            </router-link>
            <router-link
              to="/client/dashboard"
              class="flex items-center gap-3 p-2.5 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div class="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center">
                <feather-icon name="user" class="w-4 h-4 text-orange-600" />
              </div>
              <span class="text-sm text-gray-700">Client Portal</span>
            </router-link>
          </div>
        </div>

        <!-- Recent Activity -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <h2 class="text-sm font-semibold text-gray-800 mb-4">Recent Activity</h2>
          <ActivityTimeline :items="recentActivity" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, LoadingIndicator } from 'frappe-ui'
import { useTasks } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'
import ActivityTimeline from '@/components/ActivityTimeline.vue'

export default {
  name: 'ManagerDashboard',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, ProgressBar, ActivityTimeline },
  data() {
    return {
      projects: [],
      allTasks: [],
      report: null,
      reportLoading: false,
      reportPeriod: 'daily',
      recentActivity: [],
      stats: [
        { label: 'Total Projects', value: 0, icon: 'folder', bgColor: 'bg-blue-50', iconColor: 'text-blue-600' },
        { label: 'Active Projects', value: 0, icon: 'play-circle', bgColor: 'bg-green-50', iconColor: 'text-green-600' },
        { label: 'Completed', value: 0, icon: 'check-circle', bgColor: 'bg-emerald-50', iconColor: 'text-emerald-600' },
        { label: 'Delayed Tasks', value: 0, icon: 'alert-circle', bgColor: 'bg-red-50', iconColor: 'text-red-600' },
        { label: 'Pending Tasks', value: 0, icon: 'package', bgColor: 'bg-yellow-50', iconColor: 'text-yellow-600' },
        { label: 'Total Tasks', value: 0, icon: 'list', bgColor: 'bg-purple-50', iconColor: 'text-purple-600' },
      ],
    }
  },
  watch: {
    reportPeriod() {
      this.loadReport()
    },
  },
  mounted() {
    this.loadAll()
    this.logSession()
  },
  methods: {
    async logSession() {
      try {
        const res = await frappeRequest({ url: 'project_management.api.client.get_session_user', method: 'POST' })
        console.log('Dashboard User:', res.user, '| Roles:', res.roles)
      } catch {}
    },
    async loadAll() {
      await Promise.all([
        this.loadProjects(),
        this.loadTasks(),
        this.loadReport(),
      ])
      this.updateStats()
    },
    async loadProjects() {
      try {
        const result = await frappeRequest({ url: 'project_management.api.client.get_projects', method: 'POST' })
        this.projects = result || []
      } catch {
        this.projects = []
      }
    },
    async loadTasks() {
      try {
        this.allTasks = (await useTasks().fetch()) || []
      } catch {
        this.allTasks = []
      }
    },
    async loadReport() {
      this.reportLoading = true
      try {
        const result = await frappeRequest({
          url: 'project_management.api.client.get_progress_report',
          method: 'POST',
          params: { period: this.reportPeriod },
        })
        this.report = result || null
      } catch {
        this.report = null
      } finally {
        this.reportLoading = false
      }
    },
    updateStats() {
      const today = new Date().toISOString().split('T')[0]
      this.stats[0].value = this.projects.length
      this.stats[1].value = this.projects.filter(p => p.status === 'In Progress').length
      this.stats[2].value = this.projects.filter(p => p.status === 'Completed').length
      this.stats[3].value = this.allTasks.filter(
        t => t.due_date && t.due_date < today && t.status !== 'Completed'
      ).length
      this.stats[4].value = this.allTasks.filter(t => t.status !== 'Completed').length
      this.stats[5].value = this.allTasks.length

      // Build recent activity from tasks
      this.recentActivity = this.allTasks.slice(0, 10).map(t => ({
        text: `${t.title} - ${t.status}`,
        time: t.due_date || '',
      }))
    },
  },
}
</script>
