<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-xl font-bold text-gray-900">Member Dashboard</h1>
      <p class="text-sm text-gray-500 mt-0.5">Your tasks and time tracking</p>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-gray-900">{{ myTasks.length }}</p>
        <p class="text-xs text-gray-500">My Tasks</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-blue-600">{{ todayTasks.length }}</p>
        <p class="text-xs text-gray-500">Today's Focus</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-green-600">{{ completedTasks.length }}</p>
        <p class="text-xs text-gray-500">Completed</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-purple-600">{{ todayHours }}h</p>
        <p class="text-xs text-gray-500">Hours Today</p>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">Actions Needed</h2>
      <p v-if="actionsDeliverables.length === 0 && openTasks.length === 0" class="text-xs text-gray-400 text-center py-4">
        All caught up — nothing needs your attention right now.
      </p>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="d in actionsDeliverables"
          :key="d.name"
          @click="$router.push(`/member/deliverable/${d.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 rounded transition-colors"
        >
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-800 truncate">{{ d.title }}</p>
            <p class="text-xs text-gray-400">Changes Requested — waiting for you to start rework</p>
          </div>
          <Badge label="Changes Requested" :theme="statusColorMap['Changes Requested'] || 'gray'" />
        </div>
        <div
          v-for="task in openTasks"
          :key="task.name"
          @click="$router.push(`/member/task/${task.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 rounded transition-colors"
        >
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-800 truncate">{{ task.title }}</p>
            <p class="text-xs text-gray-400">{{ task.project }}</p>
          </div>
          <Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" />
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">My Projects</h2>
      <p v-if="myProjects.length === 0" class="text-xs text-gray-400 text-center py-4">
        You are not part of any project yet.
      </p>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="project in myProjects"
          :key="project.name"
          @click="$router.push(`/member/project/${project.name}`)"
          class="p-3 rounded-lg border cursor-pointer transition-colors hover:border-blue-500 hover:bg-blue-50"
        >
          <div class="flex items-center justify-between">
            <p class="text-sm font-medium text-gray-800 truncate">{{ project.project_name }}</p>
            <Badge :label="project.status" :theme="statusColorMap[project.status] || 'gray'" />
          </div>
          <p class="text-xs text-gray-400 mt-1">{{ project.client || 'No client' }}</p>
          <div class="mt-2">
            <ProgressBar :value="project.progress || 0" />
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold text-gray-800">My Deliverables</h2>
        <Button
          v-if="selectedProject"
          variant="ghost"
          size="sm"
          @click="selectedProject = ''"
        >Show all</Button>
      </div>
      <p v-if="visibleDeliverables.length === 0" class="text-xs text-gray-400 text-center py-4">No deliverables</p>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="d in visibleDeliverables"
          :key="d.name"
          @click="$router.push(`/member/deliverable/${d.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 rounded transition-colors"
        >
          <div class="min-w-0 flex-1 pr-4">
            <p class="text-sm font-medium text-gray-800 truncate">{{ d.title }}</p>
            <p class="text-xs text-gray-400 truncate">{{ d.project_name || d.project }} | Due: {{ d.due_date || 'None' }}</p>
          </div>
          <div class="flex items-center gap-3 flex-shrink-0 w-40">
            <ProgressBar :value="d.progress || 0" />
            <Badge :label="d.status" :theme="statusColorMap[d.status] || 'gray'" />
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">Today's Focus</h2>
      <p v-if="todayTasks.length === 0" class="text-xs text-gray-400 text-center py-4">
        No tasks selected for today. Star tasks below to add them here.
      </p>
      <div v-else class="space-y-2">
        <div
          v-for="task in todayTasks"
          :key="task.name"
          @click="$router.push(`/member/task/${task.name}`)"
          class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-800">{{ task.title }}</p>
            <p class="text-xs text-gray-400">{{ task.project }}</p>
          </div>
          <Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" />
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">All My Tasks</h2>
      <div v-if="myTasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks assigned</div>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="task in myTasks"
          :key="task.name"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
        >
          <div class="flex items-center gap-3 min-w-0 flex-1" @click="$router.push(`/member/task/${task.name}`)">
            <Button
              variant="ghost"
              @click.stop="toggleFocus(task)"
              :title="task.is_today_focus ? 'Remove from today' : 'Add to today'"
              class="flex-shrink-0"
            >
              <span class="text-lg leading-none" :class="task.is_today_focus ? 'text-yellow-500' : 'text-gray-300'">&#9733;</span>
            </Button>
            <div class="min-w-0">
              <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
              <p class="text-xs text-gray-400">{{ task.project }} | Due: {{ task.due_date || 'None' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <Badge :label="task.priority" :theme="statusColorMap[task.priority] || 'gray'" />
            <Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" />
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">Recently Completed</h2>
      <div v-if="completedTasks.length === 0" class="text-xs text-gray-400 text-center py-4">No completed tasks</div>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="task in completedTasks.slice(0, 5)"
          :key="task.name"
          class="flex items-center justify-between py-2"
        >
          <p class="text-sm text-gray-600 line-through">{{ task.title }}</p>
          <Badge label="Completed" :theme="statusColorMap['Completed'] || 'gray'" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { frappeRequest, Badge, Button } from 'frappe-ui'
import { useTasks } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'

export default {
  name: 'MemberDashboard',
  components: { Badge, Button, ProgressBar },
  data() {
    return {
      myTasks: [],
      myProjects: [],
      sessionUser: '',
      todayHours: 0,
      selectedProject: '',
    }
  },
  computed: {
    todayTasks() {
      return this.myTasks.filter(t => t.is_today_focus && t.status !== 'Completed')
    },
    completedTasks() {
      return this.myTasks.filter(t => t.status === 'Completed')
    },
    allDeliverables() {
      const list = []
      for (const project of this.myProjects) {
        for (const d of project.deliverables || []) {
          list.push({ ...d, project_name: project.project_name })
        }
      }
      return list
    },
    actionsDeliverables() {
      return this.allDeliverables.filter(d => d.status === 'Changes Requested')
    },
    openTasks() {
      return this.myTasks.filter(t => t.status !== 'Completed')
    },
    visibleDeliverables() {
      if (!this.selectedProject) return this.allDeliverables
      return this.allDeliverables.filter(d => d.project === this.selectedProject)
    },
  },
  mounted() {
    this.loadTasks()
  },
  methods: {
    async loadTasks() {
      try {
        const userRes = await frappeRequest({ url: 'project_management.api.client.get_session_user', method: 'POST' })
        this.sessionUser = userRes.user
        console.log('Dashboard User:', userRes.user, '| Roles:', userRes.roles)
        const [tasksRes, hoursRes, projectsRes] = await Promise.all([
          useTasks({ assigned_to: this.sessionUser }).fetch(),
          frappeRequest({ url: 'project_management.api.client.get_today_hours', method: 'POST' }),
          frappeRequest({ url: 'project_management.api.client.get_my_projects', method: 'POST' }),
        ])
        this.myTasks = tasksRes || []
        this.todayHours = hoursRes || 0
        this.myProjects = projectsRes || []
      } catch {
        this.myTasks = []
        this.myProjects = []
      }
    },
    toggleProject(name) {
      this.selectedProject = this.selectedProject === name ? '' : name
    },
    async toggleFocus(task) {
      try {
        const res = await frappeRequest({
          url: 'project_management.api.client.toggle_today_focus',
          method: 'POST',
          params: { name: task.name },
        })
        task.is_today_focus = res.is_today_focus
      } catch {}
    },
  },
}
</script>
