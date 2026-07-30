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
        <p v-if="deliverable" class="text-sm text-gray-500 mt-0.5">
          Project: {{ deliverable.project }}
        </p>
      </div>
    </div>

    <SkeletonLoader v-if="loading" :lines="5" />

    <template v-else-if="deliverable">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main content -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Details -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Details</h2>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-xs text-gray-500">Description</p>
                <p class="text-gray-700 mt-0.5">{{ deliverable.description || 'No description' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Due Date</p>
                <p class="text-gray-700 mt-0.5">{{ deliverable.due_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Submitted By</p>
                <p class="text-gray-700 mt-0.5">{{ deliverable.submitted_by || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Delivery Date</p>
                <p class="text-gray-700 mt-0.5">{{ deliverable.delivery_date || 'Not delivered yet' }}</p>
              </div>
              <div v-if="deliverable.access_link__notes">
                <p class="text-xs text-gray-500">Access Link / Notes</p>
                <p class="text-gray-700 mt-0.5">{{ deliverable.access_link__notes }}</p>
              </div>
            </div>
          </div>

          <!-- Tasks in this deliverable -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Tasks</h2>
            <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">
              No tasks in this deliverable
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="task in tasks"
                :key="task.name"
                @click="$router.push(`/task/${task.name}`)"
                class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
                  <p class="text-xs text-gray-400">{{ task.assigned_to || 'Unassigned' }}</p>
                </div>
                <StatusBadge :status="task.status" />
              </div>
            </div>
          </div>

          <!-- Comments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <CommentSection doctype="Deliverable" :docname="deliverableId" />
          </div>
        </div>

        <!-- Right column -->
        <div class="space-y-6">
          <!-- Workflow Actions -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Actions</h2>
            <div class="space-y-2">
              <button
                v-for="action in availableActions"
                :key="action"
                @click="performAction(action)"
                :disabled="updating"
                class="w-full px-3 py-2 text-xs font-medium rounded-lg transition-colors"
                :class="actionClasses(action)"
              >
                {{ action }}
              </button>
              <p v-if="availableActions.length === 0" class="text-xs text-gray-400 text-center">
                No actions available for current status
              </p>
            </div>
            <p v-if="updateError" class="text-xs text-red-500 mt-2">{{ updateError }}</p>
          </div>

          <!-- Attachments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <FileUpload doctype="Deliverable" :docname="deliverableId" />
          </div>

          <!-- Progress -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-2">Progress</h2>
            <div class="text-center py-4">
              <p class="text-3xl font-bold text-gray-900">{{ deliverableProgress }}%</p>
              <p class="text-xs text-gray-400 mt-1">{{ completedTaskCount }}/{{ taskCount }} tasks completed</p>
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

const WORKFLOW_ACTIONS = {
  'Draft': [],
  'WIP': [],
  'Ready for Approval': ['Send for Approval'],
  'Awaiting Client Review': [],
  'Approved': [],
  'Changes Requested': [],
}

export default {
  name: 'DeliverableDetail',
  components: { FeatherIcon, StatusBadge, SkeletonLoader, FileUpload, CommentSection },
  data() {
    return {
      deliverable: null,
      tasks: [],
      loading: true,
      updating: false,
      updateError: '',
    }
  },
  computed: {
    deliverableId() {
      return this.$route.params.id
    },
    availableActions() {
      if (!this.deliverable) return []
      return WORKFLOW_ACTIONS[this.deliverable.status] || []
    },
    taskCount() {
      return this.tasks.length
    },
    completedTaskCount() {
      return this.tasks.filter(t => t.status === 'Completed').length
    },
    deliverableProgress() {
      if (!this.taskCount) return 0
      return Math.round((this.completedTaskCount / this.taskCount) * 100)
    },
  },
  mounted() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [dRes, tRes] = await Promise.all([
          call('project_management.api.client.get_deliverable', { name: this.deliverableId }),
          call('project_management.api.client.get_tasks', { deliverable: this.deliverableId }),
        ])
        this.deliverable = dRes.message
        this.tasks = tRes.message || []
      } catch {
        console.error('Failed to load deliverable')
      } finally {
        this.loading = false
      }
    },
    async performAction(action) {
      this.updating = true
      this.updateError = ''
      try {
        await call('project_management.api.client.update_deliverable_status', {
          name: this.deliverableId, action,
        })
        await this.loadAll()
      } catch (err) {
        this.updateError = err.message || 'Failed to update status'
      } finally {
        this.updating = false
      }
    },
    actionClasses(action) {
      return 'bg-blue-600 text-white hover:bg-blue-700'
    },
  },
}
</script>
