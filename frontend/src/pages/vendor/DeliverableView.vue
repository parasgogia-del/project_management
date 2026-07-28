<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ deliverable?.title || 'Loading...' }}</h1>
          <StatusBadge v-if="deliverable" :status="deliverable.status" />
        </div>
      </div>
    </div>

    <SkeletonLoader v-if="loading" :lines="4" />

    <template v-else-if="deliverable">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <!-- Details -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Details</h2>
            <p class="text-sm text-gray-600">{{ deliverable.description || 'No description' }}</p>
            <div class="grid grid-cols-2 gap-4 mt-4 text-sm">
              <div>
                <p class="text-xs text-gray-500">Due Date</p>
                <p class="text-gray-700">{{ deliverable.due_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Delivery Date</p>
                <p class="text-gray-700">{{ deliverable.delivery_date || 'Not delivered' }}</p>
              </div>
              <div v-if="deliverable.access_link__notes">
                <p class="text-xs text-gray-500">Access Link / Notes</p>
                <p class="text-gray-700">{{ deliverable.access_link__notes }}</p>
              </div>
            </div>
          </div>

          <!-- Files -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <FileUpload doctype="Deliverable" :docname="deliverableId" />
          </div>

          <!-- Comments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <CommentSection doctype="Deliverable" :docname="deliverableId" />
          </div>
        </div>

        <div class="space-y-6">
          <!-- Tasks in this deliverable -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Tasks</h2>
            <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks</div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="t in tasks"
                :key="t.name"
                @click="$router.push(`/vendor/task/${t.name}`)"
                class="flex items-center justify-between py-2 cursor-pointer hover:bg-gray-50 rounded transition-colors"
              >
                <p class="text-xs text-gray-800 truncate">{{ t.title }}</p>
                <StatusBadge :status="t.status" />
              </div>
            </div>
          </div>

          <!-- Progress -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-2">Progress</h2>
            <div class="text-center py-4">
              <p class="text-3xl font-bold text-gray-900">{{ progress }}%</p>
              <p class="text-xs text-gray-400 mt-1">{{ completedTasks }}/{{ totalTasks }} tasks</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'VendorDeliverableView',
  components: { FeatherIcon, StatusBadge, SkeletonLoader, FileUpload, CommentSection },
  data() {
    return { deliverable: null, tasks: [], loading: true }
  },
  computed: {
    deliverableId() { return this.$route.params.id },
    totalTasks() { return this.tasks.length },
    completedTasks() { return this.tasks.filter(t => t.status === 'Completed').length },
    progress() { return this.totalTasks ? Math.round((this.completedTasks / this.totalTasks) * 100) : 0 },
  },
  mounted() { this.loadAll() },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [d, t] = await Promise.all([
          call('project_management.api.client.get_deliverable', { name: this.deliverableId }),
          call('project_management.api.client.get_tasks', { deliverable: this.deliverableId }),
        ])
        this.deliverable = d.message; this.tasks = t.message || []
      } catch {} finally { this.loading = false }
    },
  },
}
</script>
