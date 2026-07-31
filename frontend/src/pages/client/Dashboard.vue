<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-xl font-bold text-gray-900">Client Portal</h1>
      <p class="text-sm text-gray-500 mt-0.5">Overview of your projects</p>
    </div>

    <!-- Projects -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="project in projects"
        :key="project.name"
        @click="$router.push(`/client/project/${project.name}`)"
        class="bg-white rounded-xl border border-gray-200 p-5 cursor-pointer hover:shadow-md hover:border-blue-200 transition-all"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="min-w-0 flex-1">
            <h3 class="text-sm font-semibold text-gray-900 truncate">{{ project.project_name }}</h3>
          </div>
          <Badge :label="project.status" :color-map="statusColorMap" />
        </div>
        <ProgressBar :value="project.progress || 0" />
        <div class="mt-3 pt-3 border-t border-gray-50 text-xs text-gray-400">
          {{ project.start_date || 'No start' }} - {{ project.end_date || 'No end' }}
        </div>
      </div>
    </div>

    <div v-if="projects.length === 0 && !loading" class="bg-white rounded-xl border border-gray-200">
      <EmptyState icon="folder" title="No projects" description="No projects found for your account" />
    </div>

    <!-- Deliverables across all projects -->
    <div v-if="allDeliverables.length" class="bg-white rounded-xl border border-gray-200 p-5">
      <h2 class="text-sm font-semibold text-gray-800 mb-3">All Deliverables</h2>
      <div class="divide-y divide-gray-50">
        <div
          v-for="d in allDeliverables"
          :key="d.name"
          @click="$router.push(`/client/deliverable/${d.name}`)"
          class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
        >
          <div class="min-w-0">
            <p class="text-sm font-medium text-gray-800">{{ d.title }}</p>
            <p class="text-xs text-gray-400">{{ d.project }} | Due: {{ d.due_date || 'None' }}</p>
          </div>
          <Badge :label="d.status" :color-map="statusColorMap" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { frappeRequest, Badge } from 'frappe-ui'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'ClientDashboard',
  components: { Badge, ProgressBar, EmptyState },
  data() {
    return {
      projects: [],
      allDeliverables: [],
      loading: true,
    }
  },
  mounted() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [pRes, dRes] = await Promise.all([
          frappeRequest({ url: 'project_management.api.client.get_projects', method: 'POST' }),
          frappeRequest({ url: 'project_management.api.client.get_deliverables', method: 'POST' }),
        ])
        this.projects = pRes || []
        this.allDeliverables = dRes || []
      } catch {} finally { this.loading = false }
    },
  },
}
</script>
