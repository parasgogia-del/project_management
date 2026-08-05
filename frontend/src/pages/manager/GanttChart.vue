<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <h1 class="text-xl font-bold text-gray-900">Gantt Chart</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
      <Button variant="outline" icon-left="refresh-cw" @click="loadTasks">
        Refresh
      </Button>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <div v-else-if="tasks.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState icon="grid" title="No tasks for Gantt chart" description="Add tasks with dates to see them here" />
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <!-- Summary row -->
      <div class="flex items-center gap-6 px-4 py-2 border-b border-gray-200 bg-gray-50 text-xs text-gray-500">
        <span>{{ tasks.length }} tasks</span>
        <span>{{ tasks.filter(t => t.status === 'Completed').length }} completed</span>
        <span>{{ tasks.filter(t => t.status === 'Working').length }} in progress</span>
        <span>{{ totalDays }} day span</span>
      </div>

      <!-- Header with date range -->
      <div class="flex border-b border-gray-200">
        <div class="w-72 flex-shrink-0 px-4 py-2 text-xs font-medium text-gray-500 border-r border-gray-200">
          Task
        </div>
        <div class="flex-1 overflow-x-auto">
          <div class="flex" :style="{ minWidth: `${dateRange.length * 40}px` }">
            <div
              v-for="date in dateRange"
              :key="date"
              class="w-10 flex-shrink-0 px-1 py-2 text-center text-[10px] text-gray-400 border-r border-gray-100"
              :class="{ 'bg-blue-50 text-blue-600 font-medium': isToday(date) }"
            >
              {{ formatShortDate(date) }}
            </div>
          </div>
        </div>
      </div>

      <!-- Task rows -->
      <div class="max-h-[600px] overflow-y-auto">
        <div
          v-for="task in tasks"
          :key="task.name"
          class="flex border-b border-gray-50 hover:bg-gray-50"
        >
          <div class="w-72 flex-shrink-0 px-4 py-2 border-r border-gray-200">
            <p class="text-xs font-medium text-gray-800 truncate">{{ task.title }}</p>
            <div class="flex items-center gap-2 mt-0.5">
              <p class="text-[10px] text-gray-400">{{ task.assigned_to || task.assigned_vendor || 'Unassigned' }}</p>
              <span class="text-[10px] text-gray-400">|</span>
              <p class="text-[10px] text-gray-400">{{ getDuration(task) }}</p>
            </div>
          </div>
          <div class="flex-1 relative" :style="{ minWidth: `${dateRange.length * 40}px` }">
            <!-- Grid lines -->
            <div class="absolute inset-0 flex">
              <div
                v-for="date in dateRange"
                :key="date"
                class="w-10 flex-shrink-0 border-r border-gray-50"
                :class="{ 'bg-blue-50/50': isToday(date) }"
              />
            </div>
            <!-- Task bar -->
            <div
              class="absolute top-1/2 -translate-y-1/2 h-6 rounded-md flex items-center px-1.5 text-[9px] font-medium text-white cursor-pointer group"
              :style="taskBarStyle(task)"
              :title="`${task.title} (${task.start_date} - ${task.due_date}) | Duration: ${getDuration(task)} | ${task.status}`"
              @click="$router.push(`/task/${task.name}`)"
            >
              <span class="truncate">{{ task.title }}</span>
              <!-- Progress fill -->
              <div
                v-if="task.status === 'Completed'"
                class="absolute inset-0 rounded-md bg-white/20"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Legend -->
      <div class="flex items-center gap-4 px-4 py-2 border-t border-gray-200 bg-gray-50">
        <div v-for="(color, status) in legend" :key="status" class="flex items-center gap-1.5">
          <div class="w-3 h-3 rounded" :style="{ backgroundColor: color }" />
          <span class="text-[10px] text-gray-500">{{ status }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, Button, LoadingIndicator } from 'frappe-ui'
import { useGanttTasks } from '@/data/resources'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'GanttChart',
  components: { FeatherIcon, Button, LoadingIndicator, EmptyState },
  data() {
    return {
      tasks: [],
      loading: true,
      refreshInterval: null,
      legend: {
        Open: '#6b7280',
        Working: '#3b82f6',
        Blocked: '#ef4444',
        Completed: '#22c55e',
      },
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
    dateRange() {
      if (!this.tasks.length) return []
      const dates = this.tasks
        .flatMap(t => [t.start_date, t.due_date])
        .filter(Boolean)
        .sort()

      if (!dates.length) return []

      const start = new Date(dates[0])
      const end = new Date(dates[dates.length - 1])

      start.setDate(start.getDate() - 2)
      end.setDate(end.getDate() + 5)

      const range = []
      const current = new Date(start)
      while (current <= end) {
        range.push(current.toISOString().split('T')[0])
        current.setDate(current.getDate() + 1)
      }
      return range
    },
    totalDays() {
      if (!this.dateRange.length) return 0
      return this.dateRange.length
    },
  },
  mounted() {
    this.loadTasks()
    this.refreshInterval = setInterval(() => this.loadTasks(false), 30000)
  },
  beforeUnmount() {
    if (this.refreshInterval) clearInterval(this.refreshInterval)
  },
  methods: {
    async loadTasks(showLoader = true) {
      if (showLoader) this.loading = true
      try {
        this.tasks = (await useGanttTasks(this.projectId).fetch()) || []
      } catch {
        this.tasks = []
      } finally {
        this.loading = false
      }
    },
    getDuration(task) {
      if (!task.start_date || !task.due_date) return 'N/A'
      const start = new Date(task.start_date)
      const end = new Date(task.due_date)
      const diff = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1
      if (diff === 1) return '1 day'
      return `${diff} days`
    },
    taskBarStyle(task) {
      if (!this.dateRange.length) return {}
      const startDate = task.start_date || task.due_date
      const endDate = task.due_date || task.start_date
      if (!startDate || !endDate) return { display: 'none' }

      const startIdx = this.dateRange.indexOf(startDate)
      const endIdx = this.dateRange.indexOf(endDate)
      if (startIdx === -1 || endIdx === -1) return { display: 'none' }

      const left = startIdx * 40
      const width = Math.max((endIdx - startIdx + 1) * 40, 40)
      const color = task.color || '#6b7280'

      return {
        left: `${left}px`,
        width: `${width}px`,
        backgroundColor: color,
      }
    },
    isToday(date) {
      return date === new Date().toISOString().split('T')[0]
    },
    formatShortDate(dateStr) {
      const d = new Date(dateStr)
      return `${d.getMonth() + 1}/${d.getDate()}`
    },
  },
}
</script>
