<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div>
        <h1 class="text-xl font-bold text-gray-900">{{ project?.project_name || 'Loading...' }}</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project Progress</p>
      </div>
    </div>

    <SkeletonLoader v-if="loading" :lines="4" />

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
          <button @click="showInviteModal = true" class="text-xs font-medium text-blue-600 hover:text-blue-700">+ Invite Member</button>
        </div>
        <div v-if="!project.project_members?.length" class="text-xs text-gray-400 text-center py-2">No members</div>
        <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div v-for="m in project.project_members" :key="m.name" class="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
            <div class="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center">
              <span class="text-[10px] font-medium text-blue-700">{{ m.user?.split('@')[0]?.slice(0,2)?.toUpperCase() }}</span>
            </div>
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
            <StatusBadge :status="d.status" />
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
              <StatusBadge :status="task.priority" />
              <StatusBadge :status="task.status" />
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

  <!-- Invite Member Modal -->
  <div v-if="showInviteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/30" @click.self="showInviteModal = false">
    <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4">Invite Member</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email *</label>
          <input v-model="inviteForm.email" type="email" placeholder="user@example.com" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
          <textarea v-model="inviteForm.notes" rows="2" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none resize-none" />
        </div>
        <p v-if="inviteError" class="text-xs text-red-500">{{ inviteError }}</p>
      </div>
      <div class="flex justify-end gap-3 mt-6">
        <button @click="showInviteModal = false" class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg">Cancel</button>
        <button @click="inviteMember" :disabled="!inviteForm.email || inviting" class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {{ inviting ? 'Inviting...' : 'Invite' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'ClientProjectView',
  components: { FeatherIcon, StatusBadge, ProgressBar, SkeletonLoader, FileUpload, CommentSection },
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
          call('project_management.api.client.get_project', { name: this.projectId }),
          call('project_management.api.client.get_deliverables', { project: this.projectId }),
          call('project_management.api.client.get_tasks', { project: this.projectId }),
        ])
        this.project = p.message
        this.deliverables = d.message || []
        this.tasks = t.message || []
      } catch {} finally { this.loading = false }
    },
    async inviteMember() {
      this.inviting = true; this.inviteError = ''
      try {
        const res = await call('project_management.api.client.invite_project_member', {
          project: this.projectId, email: this.inviteForm.email, notes: this.inviteForm.notes,
        })
        this.project = res.message
        this.showInviteModal = false
        this.inviteForm = { email: '', notes: '' }
      } catch (err) {
        this.inviteError = err.message || 'Failed to invite member'
      } finally { this.inviting = false }
    },
  },
}
</script>
