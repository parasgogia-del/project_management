<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div>
        <h1 class="text-xl font-bold text-gray-900">{{ project?.project_name || 'Loading...' }}</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project Progress</p>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <template v-else-if="project">
      <!-- Progress -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-3">Progress</h2>
        <ProgressBar :value="project.progress || 0" />
      </div>

      <!-- Members -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-semibold text-gray-800">Members</h2>
          <Button variant="ghost" icon-left="plus" @click="showInviteModal = true">Invite Member</Button>
        </div>
        <div v-if="!project.project_members?.length" class="text-xs text-gray-400 text-center py-2">No members</div>
        <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div v-for="m in project.project_members" :key="m.name" class="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <Avatar :label="m.user" size="sm" />
            <div>
              <p class="text-xs font-medium text-gray-800">{{ m.user }}</p>
              <p class="text-[10px] text-gray-400">{{ m.project_role }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Deliverables -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-3">Deliverables</h2>
        <div v-if="deliverables.length === 0" class="text-xs text-gray-400 text-center py-4">No deliverables</div>
        <div v-else class="space-y-2">
          <div
            v-for="d in deliverables"
            :key="d.name"
            @click="$router.push(`/client/deliverable/${d.name}`)"
            class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <div class="min-w-0">
              <p class="text-sm font-medium text-gray-800">{{ d.title }}</p>
              <p class="text-xs text-gray-400">Due: {{ d.due_date || 'Not set' }}</p>
            </div>
            <Badge :label="d.status" :theme="statusColorMap[d.status] || 'gray'" />
          </div>
        </div>
      </div>

      <!-- Tasks -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h2 class="text-sm font-semibold text-gray-800 mb-3">Tasks ({{ tasks.length }})</h2>
        <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks</div>
        <div v-else class="divide-y divide-gray-50">
          <div
            v-for="task in tasks"
            :key="task.name"
            @click="$router.push(`/client/task/${task.name}`)"
            class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
          >
            <div class="min-w-0 flex-1">
              <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
              <p class="text-xs text-gray-400">Due: {{ task.due_date || 'None' }} | {{ task.assigned_to || 'Unassigned' }}</p>
            </div>
            <div class="flex items-center gap-2 flex-shrink-0 ml-3">
              <Badge :label="task.priority" :theme="statusColorMap[task.priority] || 'gray'" />
              <Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" />
            </div>
          </div>
        </div>
      </div>

      <!-- Attachments -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <FileUpload doctype="Project Info" :docname="projectId" />
      </div>

      <!-- Comments -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <CommentSection doctype="Project Info" :docname="projectId" />
      </div>
    </template>
  </div>

  <Dialog v-model="showInviteModal" :options="{ title: 'Invite Member', size: 'sm' }">
    <template #body-content>
      <div class="space-y-4">
        <Input v-model="inviteForm.email" type="email" label="Email *" placeholder="user@example.com" />
        <Input v-model="inviteForm.notes" type="textarea" :rows="2" label="Notes (optional)" />
        <p v-if="inviteError" class="text-xs text-red-500">{{ inviteError }}</p>
      </div>
    </template>
    <template #actions="{ close }">
      <Button variant="outline" @click="close">Cancel</Button>
      <Button
        theme="blue" variant="solid"
        :disabled="!inviteForm.email"
        :loading="inviting"
        :loading-text="inviting ? 'Inviting...' : null"
        @click="inviteMember"
      >Invite</Button>
    </template>
  </Dialog>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, Avatar, LoadingIndicator, Dialog, Input } from 'frappe-ui'
import { useProject, useDeliverables, useTasks } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'ClientProjectView',
  components: { FeatherIcon, Button, Badge, Avatar, LoadingIndicator, Dialog, Input, ProgressBar, FileUpload, CommentSection },
  data() {
    return {
      project: null, deliverables: [], tasks: [], loading: true,
      showInviteModal: false, inviting: false, inviteError: '',
      inviteForm: { email: '', notes: '' },
    }
  },
  computed: {
    projectId() { return this.$route.params.id },
  },
  mounted() { this.loadAll() },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [p, d, t] = await Promise.all([
          useProject(this.projectId, 'client').fetch(),
          useDeliverables(this.projectId, 'client').fetch(),
          useTasks({ project: this.projectId, portal: 'client' }).fetch(),
        ])
        this.project = p
        this.deliverables = d || []
        this.tasks = t || []
      } catch {} finally { this.loading = false }
    },
    async inviteMember() {
      this.inviting = true; this.inviteError = ''
      try {
        this.project = await frappeRequest({
          url: 'project_management.api.client.invite_project_member',
          method: 'POST',
          params: { project: this.projectId, email: this.inviteForm.email, notes: this.inviteForm.notes },
        })
        this.showInviteModal = false
        this.inviteForm = { email: '', notes: '' }
      } catch (err) {
        this.inviteError = err.message || 'Failed to invite member'
      } finally { this.inviting = false }
    },
  },
}
</script>
