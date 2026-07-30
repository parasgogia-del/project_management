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
          <StatusBadge :status="task.status" />
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
            <button
              @click.stop="toggleFocus(task)"
              class="flex-shrink-0 text-lg leading-none transition-colors"
              :class="task.is_today_focus ? 'text-yellow-500' : 'text-gray-300 hover:text-gray-400'"
              :title="task.is_today_focus ? 'Remove from today' : 'Add to today'"
            >&#9733;</button>
            <div class="min-w-0">
              <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
              <p class="text-xs text-gray-400">{{ task.project }} | Due: {{ task.due_date || 'None' }}</p>
            </div>
          </div>
          <div class="flex items-center gap-2 flex-shrink-0">
            <StatusBadge :status="task.priority" />
            <StatusBadge :status="task.status" />
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
          <StatusBadge status="Completed" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'

export default {
  name: 'MemberDashboard',
  components: { StatusBadge },
  data() {
    return {
      myTasks: [],
      sessionUser: '',
      todayHours: 0,
    }
  },
  computed: {
    todayTasks() {
      return this.myTasks.filter(t => t.is_today_focus && t.status !== 'Completed')
    },
    completedTasks() {
      return this.myTasks.filter(t => t.status === 'Completed')
    },
  },
  mounted() {
    this.loadTasks()
  },
  methods: {
    async loadTasks() {
      try {
        const userRes = await call('project_management.api.client.get_session_user')
        this.sessionUser = userRes.message.user
        const [tasksRes, hoursRes] = await Promise.all([
          call('project_management.api.client.get_tasks', { assigned_to: this.sessionUser }),
          call('project_management.api.client.get_today_hours'),
        ])
        this.myTasks = tasksRes.message || []
        this.todayHours = hoursRes.message || 0
      } catch {
        this.myTasks = []
      }
    },
    async toggleFocus(task) {
      try {
        const res = await call('project_management.api.client.toggle_today_focus', { name: task.name })
        task.is_today_focus = res.message.is_today_focus
      } catch {}
    },
  },
}
</script>
