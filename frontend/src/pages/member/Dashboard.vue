<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-xl font-bold text-gray-900">Member Dashboard</h1>
      <p class="text-sm text-gray-500 mt-0.5">Your tasks and time tracking</p>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-gray-900">{{ myTasks.length }}</p>
        <p class="text-xs text-gray-500">My Tasks</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-blue-600">{{ todayTasks.length }}</p>
        <p class="text-xs text-gray-500">Today's Tasks</p>
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

    <!-- Today's Tasks -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">Today's Tasks</h2>
      <div v-if="todayTasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks for today</div>
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

    <!-- All My Tasks -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">All My Tasks</h2>
      <div v-if="myTasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks assigned</div>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="task in myTasks"
          :key="task.name"
          @click="$router.push(`/member/task/${task.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
        >
          <div class="min-w-0 flex-1">
            <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
            <p class="text-xs text-gray-400">{{ task.project }} | Due: {{ task.due_date || 'None' }}</p>
          </div>
          <div class="flex items-center gap-2">
            <StatusBadge :status="task.priority" />
            <StatusBadge :status="task.status" />
          </div>
        </div>
      </div>
    </div>

    <!-- Recently Completed -->
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
    }
  },
  computed: {
    todayTasks() {
      const today = new Date().toISOString().split('T')[0]
      return this.myTasks.filter(t => t.due_date === today && t.status !== 'Completed')
    },
    completedTasks() {
      return this.myTasks.filter(t => t.status === 'Completed')
    },
    todayHours() {
      return 0
    },
  },
  mounted() {
    this.loadTasks()
  },
  methods: {
    async loadTasks() {
      try {
        const userRes = await call('project_management.api.client.get_session_user')
        this.sessionUser = userRes.message
        const result = await call('project_management.api.client.get_tasks', {
          assigned_to: this.sessionUser,
        })
        this.myTasks = result.message || []
      } catch {
        this.myTasks = []
      }
    },
  },
}
</script>
