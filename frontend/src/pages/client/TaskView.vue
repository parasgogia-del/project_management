<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div>
        <h1 class="text-xl font-bold text-gray-900">{{ task?.title || 'Loading...' }}</h1>
        <p class="text-sm text-gray-500 mt-0.5">{{ task?.project }}</p>
      </div>
    </div>

    <SkeletonLoader v-if="loading" :lines="4" />

    <template v-else-if="task">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <div class="flex items-center gap-3 mb-4">
              <StatusBadge :status="task.status" />
              <StatusBadge :status="task.priority" />
            </div>
            <p class="text-sm text-gray-600">{{ task.description || 'No description' }}</p>
            <div class="grid grid-cols-3 gap-4 mt-4 text-sm">
              <div>
                <p class="text-xs text-gray-500">Due Date</p>
                <p class="text-gray-700">{{ task.due_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Assigned To</p>
                <p class="text-gray-700">{{ task.assigned_to || 'Not assigned' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Actual Hours</p>
                <p class="text-gray-700">{{ task.actual_hours || 0 }}h</p>
              </div>
            </div>
          </div>

          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <CommentSection doctype="Project Task" :docname="taskId" />
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Deliverable</h2>
            <p class="text-sm text-gray-600">{{ task.deliverable || 'Not linked to any deliverable' }}</p>
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
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'ClientTaskView',
  components: { FeatherIcon, StatusBadge, SkeletonLoader, CommentSection },
  data() {
    return { task: null, loading: true }
  },
  computed: {
    taskId() { return this.$route.params.id },
  },
  mounted() { this.loadAll() },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const res = await call('project_management.api.client.get_task', { name: this.taskId })
        this.task = res.message
      } catch {} finally { this.loading = false }
    },
  },
}
</script>
