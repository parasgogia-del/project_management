<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button appearance="minimal" icon="arrow-left" @click="$router.back()" />
      <div>
        <h1 class="text-xl font-bold text-gray-900">Reports</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
    </div>

    <div class="flex gap-1 bg-gray-100 rounded-lg p-0.5 w-fit">
      <Button
        appearance="minimal"
        :active="period === 'daily'"
        @click="period = 'daily'"
      >Daily</Button>
      <Button
        appearance="minimal"
        :active="period === 'weekly'"
        @click="period = 'weekly'"
      >Weekly</Button>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

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

      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-purple-600">{{ report.tasks.completed_in_period || 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">Completed {{ period === 'daily' ? 'Today' : 'This Week' }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-cyan-600">{{ report.tasks.created_in_period || 0 }}</p>
          <p class="text-xs text-gray-500 mt-1">Created {{ period === 'daily' ? 'Today' : 'This Week' }}</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-indigo-600">{{ report.deliverables.approved }}/{{ report.deliverables.total }}</p>
          <p class="text-xs text-gray-500 mt-1">Deliverables Approved</p>
        </div>
        <div class="bg-white rounded-xl border border-gray-200 p-4 text-center">
          <p class="text-2xl font-bold text-orange-600">{{ report.time.total_hours?.toFixed(1) || 0 }}h</p>
          <p class="text-xs text-gray-500 mt-1">Hours Logged</p>
        </div>
      </div>

      <!-- Completion % bar -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-sm font-semibold text-gray-800">Project Completion</h2>
          <span class="text-sm font-bold text-blue-600">{{ report.completion_percentage || 0 }}%</span>
        </div>
        <div class="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
          <div
            class="h-full bg-blue-600 rounded-full transition-all"
            :style="{ width: `${report.completion_percentage || 0}%` }"
          />
        </div>
        <p class="text-xs text-gray-400 mt-2">{{ report.tasks.completed }} of {{ report.tasks.total }} tasks completed</p>
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
            <Badge :label="t.status" :color-map="statusColorMap" />
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
import { FeatherIcon, Button, Badge, LoadingIndicator } from 'frappe-ui'
import { useProgressReport } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'

export default {
  name: 'Reports',
  components: { FeatherIcon, Button, Badge, LoadingIndicator },
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
        this.report = (await useProgressReport(this.projectId, this.period).fetch()) || null
      } catch {
        this.report = null
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
