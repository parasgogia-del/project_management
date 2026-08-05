<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div>
        <h1 class="text-xl font-bold text-gray-900">{{ task?.title || 'Loading...' }}</h1>
        <p class="text-sm text-gray-500 mt-0.5">{{ task?.project }}</p>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <template v-else-if="task">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <div class="flex items-center gap-3 mb-4">
              <Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" />
              <Badge :label="task.priority" :theme="statusColorMap[task.priority] || 'gray'" />
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
import { FeatherIcon, Button, Badge, LoadingIndicator } from 'frappe-ui'
import { useTask } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'ClientTaskView',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, CommentSection },
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
        this.task = await useTask(this.taskId).fetch()
      } catch {} finally { this.loading = false }
    },
  },
}
</script>
