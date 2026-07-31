<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-gray-900">Projects</h1>
        <p class="text-sm text-gray-500 mt-0.5">Manage all your projects</p>
      </div>
      <Button route="/project/new" appearance="primary" icon-left="plus">
        New Project
      </Button>
    </div>

    <div class="flex items-center gap-3">
      <Input
        v-model="searchQuery"
        icon-left="search"
        placeholder="Search projects..."
        class="w-64"
      />
      <Input
        type="select"
        v-model="statusFilter"
        :options="projectStatusOptions"
        class="w-48"
      />
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <div v-else-if="filteredProjects.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState
        icon="folder"
        title="No projects found"
        description="Create your first project to get started"
      >
        <Button route="/project/new" appearance="primary" icon-left="plus" class="mt-3">
          New Project
        </Button>
      </EmptyState>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="project in filteredProjects"
        :key="project.name"
        @click="$router.push(`/project/${project.name}`)"
        class="bg-white rounded-xl border border-gray-200 p-5 cursor-pointer hover:shadow-md hover:border-blue-200 transition-all"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="min-w-0 flex-1">
            <h3 class="text-sm font-semibold text-gray-900 truncate">{{ project.project_name }}</h3>
            <p class="text-xs text-gray-500 mt-0.5">{{ project.client }}</p>
          </div>
          <Badge :label="project.status" :color-map="statusColorMap" />
        </div>

        <p v-if="project.description" class="text-xs text-gray-400 line-clamp-2 mb-3">
          {{ project.description }}
        </p>

        <ProgressBar :value="project.progress || 0" />

        <div class="flex items-center justify-between mt-3 pt-3 border-t border-gray-50">
          <div class="flex items-center gap-1 text-xs text-gray-400">
            <feather-icon name="user" class="w-3 h-3" />
            {{ project.project_manager || 'Unassigned' }}
          </div>
          <div class="flex items-center gap-2 text-xs text-gray-400">
            <span v-if="project.start_date">{{ formatDate(project.start_date) }}</span>
            <span v-if="project.end_date">- {{ formatDate(project.end_date) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Input, Badge, LoadingIndicator } from 'frappe-ui'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'ProjectList',
  components: { FeatherIcon, Button, Input, Badge, LoadingIndicator, ProgressBar, EmptyState },
  data() {
    return {
      projects: [],
      loading: true,
      searchQuery: '',
      statusFilter: '',
      projectStatusOptions: [
        { label: 'All Status', value: '' },
        { label: 'Planning', value: 'Planning' },
        { label: 'In Progress', value: 'In Progress' },
        { label: 'Completed', value: 'Completed' },
        { label: 'On Hold', value: 'On Hold' },
        { label: 'Cancelled', value: 'Cancelled' },
      ],
    }
  },
  computed: {
    filteredProjects() {
      return this.projects.filter(p => {
        const matchSearch = !this.searchQuery ||
          p.project_name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          (p.client || '').toLowerCase().includes(this.searchQuery.toLowerCase())
        const matchStatus = !this.statusFilter || p.status === this.statusFilter
        return matchSearch && matchStatus
      })
    },
  },
  mounted() {
    this.loadProjects()
  },
  methods: {
    async loadProjects() {
      this.loading = true
      try {
        const result = await frappeRequest({ url: 'project_management.api.client.get_projects', method: 'POST' })
        this.projects = result || []
      } catch {
        this.projects = []
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    },
  },
}
</script>
