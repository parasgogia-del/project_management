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
        <h2 class="text-sm font-semibold text-gray-800 mb-3">Members</h2>
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
    return { project: null, deliverables: [], loading: true }
  },
  computed: {
    projectId() { return this.$route.params.id },
  },
  mounted() { this.loadAll() },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [p, d] = await Promise.all([
          call('project_management.api.client.get_project', { name: this.projectId }),
          call('project_management.api.client.get_deliverables', { project: this.projectId }),
        ])
        this.project = p.message
        this.deliverables = d.message || []
      } catch {} finally { this.loading = false }
    },
  },
}
</script>
