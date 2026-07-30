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

    <!-- Assigned Tasks -->
    <div class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">Assigned Tasks</h2>
      <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks assigned</div>
      <div v-else class="divide-y divide-gray-50">
        <div
          v-for="task in tasks"
          :key="task.name"
          @click="$router.push(`/vendor/task/${task.name}`)"
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
          <div class="min-w-0">
            <p class="text-sm font-medium text-gray-800">{{ d.title }}</p>
            <p class="text-xs text-gray-400">{{ d.project }} | Due: {{ d.due_date || 'None' }}</p>
          </div>
          <StatusBadge :status="d.status" />
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
            <StatusBadge :status="p.status" />
            <span class="text-xs text-gray-400">{{ p.client }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import ProgressBar from '@/components/ProgressBar.vue'

export default {
  name: 'VendorDashboard',
  components: { StatusBadge, ProgressBar },
  data() {
    return {
      tasks: [],
      deliverables: [],
      vendorProjects: [],
      vendorName: '',
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
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const userRes = await call('project_management.api.client.get_session_user')
        this.vendorName = userRes.message
        const [t, d, p] = await Promise.all([
          call('project_management.api.vendor.get_vendor_tasks', { vendor_name: this.vendorName }),
          call('project_management.api.vendor.get_vendor_deliverables', { vendor_name: this.vendorName }),
          call('project_management.api.vendor.get_vendor_projects', { vendor_name: this.vendorName }),
        ])
        this.tasks = t.message || []
        this.deliverables = d.message || []
        this.vendorProjects = p.message || []
      } catch {}
    },
  },
}
</script>
