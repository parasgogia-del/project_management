<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ deliverable?.title || 'Loading...' }}</h1>
          <Badge v-if="deliverable" :label="deliverable.status" :theme="statusColorMap[deliverable.status] || 'gray'" />
        </div>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <template v-else-if="deliverable">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
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

          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <FileUpload doctype="Deliverable" :docname="deliverableId" />
          </div>

          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <CommentSection doctype="Deliverable" :docname="deliverableId" />
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Actions</h2>
            <div v-if="canManage" class="space-y-2">
              <Button
                v-for="action in availableActions"
                :key="action"
                @click="performAction(action)"
                :disabled="updating"
                theme="blue" variant="solid"
                class="w-full"
              >{{ action }}</Button>
              <p v-if="availableActions.length === 0 && !updating" class="text-xs text-gray-400 text-center">No actions available</p>
              <p v-if="updateError" class="text-xs text-red-500">{{ updateError }}</p>
            </div>
            <p v-else class="text-xs text-gray-400 text-center">You are not associated with this project</p>
          </div>

          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Tasks</h2>
            <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks</div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="t in tasks"
                :key="t.name"
                @click="$router.push(`/member/task/${t.name}`)"
                class="flex items-center justify-between py-2 cursor-pointer hover:bg-gray-50 rounded transition-colors"
              >
                <p class="text-xs text-gray-800 truncate">{{ t.title }}</p>
                <Badge :label="t.status" :theme="statusColorMap[t.status] || 'gray'" />
              </div>
            </div>
          </div>

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
import { FeatherIcon, frappeRequest, Button, Badge, LoadingIndicator } from 'frappe-ui'
import { useDeliverable, useTasks } from '@/data/resources'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'

const MEMBER_ACTIONS = {
  'Draft': ['Start Work'],
  'WIP': ['Submit for Approval'],
  'Ready for Approval': [],
  'Awaiting Client Review': [],
  'Approved': [],
  'Changes Requested': ['Start Rework'],
}

export default {
  name: 'MemberDeliverableView',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, FileUpload, CommentSection },
  data() {
    return { deliverable: null, tasks: [], loading: true, updating: false, updateError: '', canManage: true }
  },
  computed: {
    deliverableId() { return this.$route.params.id },
    availableActions() {
      if (!this.deliverable) return []
      return MEMBER_ACTIONS[this.deliverable.status] || []
    },
    totalTasks() { return this.tasks.length },
    completedTasks() { return this.tasks.filter(t => t.status === 'Completed').length },
    progress() { return this.totalTasks ? Math.round((this.completedTasks / this.totalTasks) * 100) : 0 },
  },
  mounted() { this.loadAll() },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [d, t, access] = await Promise.all([
          useDeliverable(this.deliverableId).fetch(),
          useTasks({ deliverable: this.deliverableId }).fetch(),
          frappeRequest({ url: 'project_management.api.client.get_deliverable_access', method: 'POST', params: { name: this.deliverableId } }),
        ])
        this.deliverable = d; this.tasks = t || []
        this.canManage = access?.can_manage ?? true
      } catch {} finally { this.loading = false }
    },
    async performAction(action) {
      this.updating = true; this.updateError = ''
      try {
        await frappeRequest({
          url: 'project_management.api.client.update_deliverable_status',
          method: 'POST',
          params: { name: this.deliverableId, action },
        })
        await this.loadAll()
      } catch (err) {
        this.updateError = err.message || 'Failed'
      } finally { this.updating = false }
    },
  },
}
</script>
