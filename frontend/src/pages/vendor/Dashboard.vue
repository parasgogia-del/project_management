<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-xl font-bold text-gray-900">Vendor Portal</h1>
      <p class="text-sm text-gray-500 mt-0.5">Your assigned work</p>
    </div>

    <!-- Stat cards -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-gray-900">{{ tasks.length }}</p>
        <p class="text-xs text-gray-500">Assigned Tasks</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-blue-600">{{ activeDeliverables.length }}</p>
        <p class="text-xs text-gray-500">Active Deliverables</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-orange-600">{{ feedbackCount }}</p>
        <p class="text-xs text-gray-500">Feedback Received</p>
      </div>
      <div class="bg-white rounded-xl border border-gray-200 p-4">
        <p class="text-2xl font-bold text-purple-600">{{ totalHours }}h</p>
        <p class="text-xs text-gray-500">Total Hours</p>
      </div>
    </div>

    <!-- Actions Needed -->
    <div class="bg-white rounded-xl border border-orange-200 p-5">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold text-gray-800">Actions Needed</h2>
        <Badge :label="`${actionItems.length} pending`" theme="orange" />
      </div>
      <div v-if="actionItems.length === 0" class="text-xs text-gray-400 text-center py-4">All caught up!</div>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="item in actionItems"
          :key="`${item.type}-${item.name}`"
          @click="$router.push(item.type === 'deliverable' ? `/vendor/deliverable/${item.name}` : `/vendor/task/${item.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-orange-50 -mx-2 px-2 rounded transition-colors"
        >
          <div class="min-w-0 flex-1">
            <p class="text-sm text-gray-800 truncate">{{ item.title }}</p>
            <p class="text-xs text-gray-400">
              <span class="font-medium text-orange-600">{{ item.reason }}</span>
              <span v-if="item.due_date"> | Due: {{ item.due_date }}</span>
            </p>
          </div>
          <Badge :label="item.status" :theme="statusColorMap[item.status] || 'gray'" />
        </div>
      </div>
    </div>

    <!-- Assigned Tasks -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <div class="flex items-center justify-between mb-3">
        <h2 class="text-sm font-semibold text-gray-800">Assigned Tasks</h2>
        <select
          v-model="taskStatusFilter"
          class="text-xs border border-gray-200 rounded-lg px-2 py-1 bg-white text-gray-700 focus:outline-none focus:border-blue-400"
        >
          <option value="All">All statuses</option>
          <option value="Open">Open</option>
          <option value="Working">Working</option>
          <option value="Blocked">Blocked</option>
          <option value="Completed">Completed</option>
        </select>
      </div>
      <div v-if="filteredTasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks assigned</div>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="task in filteredTasks"
          :key="task.name"
          @click="$router.push(`/vendor/task/${task.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
        >
          <div class="min-w-0 flex-1">
            <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
            <p class="text-xs text-gray-400">{{ task.project }} | Due: {{ task.due_date || 'None' }}</p>
          </div>
          <div class="flex items-center gap-2">
            <Badge :label="task.priority" :theme="statusColorMap[task.priority] || 'gray'" />
            <Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" />
          </div>
        </div>
      </div>
    </div>

    <!-- Deliverables -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">My Deliverables</h2>
      <div v-if="deliverables.length === 0" class="text-xs text-gray-400 text-center py-4">No deliverables</div>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="d in deliverables"
          :key="d.name"
          @click="$router.push(`/vendor/deliverable/${d.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
        >
          <div class="min-w-0 pr-4">
            <p class="text-sm font-medium text-gray-800">{{ d.title }}</p>
            <p class="text-xs text-gray-400">{{ d.project }} | Due: {{ d.due_date || 'None' }}</p>
            <div v-if="d.feedback_comments?.length" class="mt-1">
              <p
                v-for="c in d.feedback_comments.slice(0, 1)"
                :key="c.name"
                class="text-xs italic text-gray-500 truncate"
              >Feedback: {{ stripMarkdown(c.content) }}</p>
            </div>
          </div>
          <Badge :label="d.status" :theme="statusColorMap[d.status] || 'gray'" />
        </div>
      </div>
    </div>

    <!-- Projects -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">Projects</h2>
      <div v-if="vendorProjects.length === 0" class="text-xs text-gray-400 text-center py-4">No projects</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div
          v-for="p in vendorProjects"
          :key="p.name"
          class="p-3 bg-gray-50 rounded-lg"
        >
          <p class="text-sm font-medium text-gray-800">{{ p.project_name }}</p>
          <ProgressBar :value="p.progress || 0" />
          <div class="flex items-center justify-between mt-2">
            <Badge :label="p.status" :theme="statusColorMap[p.status] || 'gray'" />
            <span class="text-xs text-gray-400">{{ p.client }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Badge } from 'frappe-ui'
import { useVendorTasks, useVendorDeliverables, useVendorProjects } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'

export default {
  name: 'VendorDashboard',
  components: { Badge, ProgressBar },
  data() {
    return {
      tasks: [],
      deliverables: [],
      vendorProjects: [],
      taskStatusFilter: 'All',
    }
  },
  computed: {
    activeDeliverables() {
      return this.deliverables.filter(d => d.status !== 'Approved')
    },
    feedbackCount() {
      return this.deliverables.filter(d => d.status === 'Changes Requested').length
    },
    totalHours() {
      return this.tasks.reduce((sum, t) => sum + (t.actual_hours || 0), 0).toFixed(1)
    },
    filteredTasks() {
      if (this.taskStatusFilter === 'All') return this.tasks
      return this.tasks.filter(t => t.status === this.taskStatusFilter)
    },
    actionItems() {
      const items = []
      for (const d of this.deliverables) {
        if (d.status === 'Changes Requested') {
          items.push({ type: 'deliverable', name: d.name, title: d.title, status: d.status, due_date: d.due_date, reason: 'Rework requested' })
        } else if (d.status === 'WIP') {
          items.push({ type: 'deliverable', name: d.name, title: d.title, status: d.status, due_date: d.due_date, reason: 'Deliverable in progress' })
        }
      }
      for (const t of this.tasks) {
        if (['Open', 'Working', 'Blocked'].includes(t.status)) {
          items.push({ type: 'task', name: t.name, title: t.title, status: t.status, due_date: t.due_date, reason: t.project })
        }
      }
      return items.sort((a, b) => {
        const da = a.due_date || '9999-99-99'
        const db = b.due_date || '9999-99-99'
        return da < db ? -1 : da > db ? 1 : 0
      })
    },
  },
  mounted() {
    this.loadData()
  },
  methods: {
    stripMarkdown(text) {
      if (!text) return ''
      return String(text)
        .replace(/\*\*/g, '')
        .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
        .trim()
    },
    async loadData() {
      try {
        const [t, d, p] = await Promise.all([
          useVendorTasks().fetch(),
          useVendorDeliverables().fetch(),
          useVendorProjects().fetch(),
        ])
        this.tasks = t || []
        this.deliverables = d || []
        this.vendorProjects = p || []
      } catch {}
    },
  },
}
</script>
