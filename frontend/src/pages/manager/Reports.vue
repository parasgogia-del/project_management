<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div>
        <h1 class="text-xl font-bold text-gray-900">Reports</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
    </div>

    <!-- Period toggle -->
    <div class="flex gap-1 bg-gray-100 rounded-lg p-0.5 w-fit">
      <button
        @click="period = 'daily'"
        class="px-4 py-1.5 text-sm font-medium rounded-md transition-colors"
        :class="period === 'daily' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500'"
      >Daily</button>
      <button
        @click="period = 'weekly'"
        class="px-4 py-1.5 text-sm font-medium rounded-md transition-colors"
        :class="period === 'weekly' ? 'bg-white text-gray-800 shadow-sm' : 'text-gray-500'"
      >Weekly</button>
    </div>

    <SkeletonLoader v-if="loading" :lines="5" />

    <template v-else-if="report">
      <!-- Summary cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-gray-900">{{ report.tasks.total }}</p>
          <p class="text-xs text-gray-500 mt-1">Total Tasks</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-green-600">{{ report.tasks.completed }}</p>
          <p class="text-xs text-gray-500 mt-1">Completed</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-blue-600">{{ report.tasks.in_progress }}</p>
          <p class="text-xs text-gray-500 mt-1">In Progress</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-red-600">{{ report.tasks.overdue }}</p>
          <p class="text-xs text-gray-500 mt-1">Overdue</p>
        </div>
      </div>

      <div class="grid grid-cols-3 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-purple-600">{{ report.time.total_hours?.toFixed(1) || 0 }}h</p>
          <p class="text-xs text-gray-500 mt-1">Hours Logged ({{ period }})</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-indigo-600">{{ report.deliverables.approved }}/{{ report.deliverables.total }}</p>
          <p class="text-xs text-gray-500 mt-1">Deliverables Approved</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-orange-600">{{ report.tasks.blocked }}</p>
          <p class="text-xs text-gray-500 mt-1">Blocked Tasks</p>
        </div>
      </div>

      <!-- Recent Tasks -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-3">Recent Tasks</h2>
        <div v-if="report.recent_tasks?.length" class="divide-y divide-gray-50">
          <div
            v-for="t in report.recent_tasks"
            :key="t.name"
            class="flex items-center justify-between py-2"
          >
            <div>
              <p class="text-sm text-gray-800">{{ t.title }}</p>
              <p class="text-xs text-gray-400">{{ t.assigned_to || 'Unassigned' }}</p>
            </div>
            <StatusBadge :status="t.status" />
          </div>
        </div>
        <p v-else class="text-xs text-gray-400 text-center py-4">No tasks</p>
      </div>

      <!-- Recent Time Logs -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-3">Recent Time Logs</h2>
        <div v-if="report.recent_logs?.length" class="divide-y divide-gray-50">
          <div
            v-for="l in report.recent_logs"
            :key="l.name"
            class="flex items-center justify-between py-2"
          >
            <div>
              <p class="text-sm text-gray-800">{{ l.task }}</p>
              <p class="text-xs text-gray-400">{{ l.member }}</p>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium text-gray-700">{{ l.hours }}h</p>
              <p class="text-xs text-gray-400">{{ l.date }}</p>
            </div>
          </div>
        </div>
        <p v-else class="text-xs text-gray-400 text-center py-4">No time logs</p>
      </div>
    </template>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

export default {
  name: 'Reports',
  components: { FeatherIcon, StatusBadge, SkeletonLoader },
  data() {
    return {
      report: null,
      loading: true,
      period: 'daily',
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
  },
  watch: {
    period() {
      this.loadReport()
    },
  },
  mounted() {
    this.loadReport()
  },
  methods: {
    async loadReport() {
      this.loading = true
      try {
        const result = await call('project_management.api.client.get_progress_report', {
          project: this.projectId,
          period: this.period,
        })
        this.report = result.message || null
      } catch {
        this.report = null
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
