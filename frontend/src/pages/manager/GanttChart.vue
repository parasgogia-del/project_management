<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div>
        <h1 class="text-xl font-bold text-gray-900">Gantt Chart</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
    </div>

    <SkeletonLoader v-if="loading" :lines="5" />

    <div v-else-if="tasks.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState icon="grid" title="No tasks for Gantt chart" description="Add tasks with dates to see them here" />
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <!-- Header with date range -->
      <div class="flex border-b border-gray-200">
        <div class="w-64 flex-shrink-0 px-4 py-2 text-xs font-medium text-gray-500 border-r border-gray-200">
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
          <div class="w-64 flex-shrink-0 px-4 py-2 border-r border-gray-200">
            <p class="text-xs font-medium text-gray-800 truncate">{{ task.title }}</p>
            <p class="text-[10px] text-gray-400">{{ task.assigned_to || task.assigned_vendor || 'Unassigned' }}</p>
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
              class="absolute top-1/2 -translate-y-1/2 h-5 rounded-md flex items-center px-1.5 text-[9px] font-medium text-white cursor-pointer"
              :style="taskBarStyle(task)"
              :title="`${task.title} (${task.start_date} - ${task.due_date})`"
              @click="$router.push(`/task/${task.name}`)"
            >
              <span class="truncate">{{ task.title }}</span>
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
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'GanttChart',
  components: { FeatherIcon, SkeletonLoader, EmptyState },
  data() {
    return {
      tasks: [],
      loading: true,
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

      // Add padding
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
  },
  mounted() {
    this.loadTasks()
  },
  methods: {
    async loadTasks() {
      this.loading = true
      try {
        const result = await call('project_management.api.client.get_gantt_tasks', {
          project: this.projectId,
        })
        this.tasks = result.message || []
      } catch {
        this.tasks = []
      } finally {
        this.loading = false
      }
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
