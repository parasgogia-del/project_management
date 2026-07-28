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
          <!-- Review History -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Review Actions</h2>
            <div class="space-y-2">
              <button
                v-for="action in availableActions"
                :key="action"
                @click="performAction(action)"
                :disabled="updating"
                class="w-full px-3 py-2 text-xs font-medium rounded-lg transition-colors"
                :class="action === 'Approve' ? 'bg-green-600 text-white hover:bg-green-700' : 'bg-orange-100 text-orange-700 hover:bg-orange-200'"
              >
                {{ action }}
              </button>
              <p v-if="!availableActions.length" class="text-xs text-gray-400 text-center">No actions available</p>
            </div>
            <p v-if="updateError" class="text-xs text-red-500 mt-2">{{ updateError }}</p>
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

const ACTIONS = {
  'Draft': [],
  'WIP': [],
  'Ready for Approval': ['Approve', 'Request Changes'],
  'Awaiting Client Review': ['Approve', 'Request Changes'],
  'Approved': [],
  'Changes Requested': [],
}

export default {
  name: 'ClientDeliverableView',
  components: { FeatherIcon, StatusBadge, SkeletonLoader, FileUpload, CommentSection },
  data() {
    return {
      deliverable: null, tasks: [], loading: true, updating: false, updateError: '',
    }
  },
  computed: {
    deliverableId() { return this.$route.params.id },
    availableActions() { return ACTIONS[this.deliverable?.status] || [] },
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
        this.deliverable = d.message
        this.tasks = t.message || []
      } catch {} finally { this.loading = false }
    },
    async performAction(action) {
      this.updating = true; this.updateError = ''
      try {
        await call('project_management.api.client.update_deliverable_status', { name: this.deliverableId, action })
        await this.loadAll()
      } catch (err) { this.updateError = err.message || 'Failed' } finally { this.updating = false }
    },
  },
}
</script>
