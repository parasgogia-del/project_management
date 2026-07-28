<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-bold text-gray-900">Projects</h1>
        <p class="text-sm text-gray-500 mt-0.5">Manage all your projects</p>
      </div>
      <router-link
        to="/project/new"
        class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
      >
        <feather-icon name="plus" class="w-4 h-4" />
        New Project
      </router-link>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-3">
      <div class="relative">
        <feather-icon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search projects..."
          class="pl-9 pr-4 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 bg-white w-64"
        />
      </div>
      <select
        v-model="statusFilter"
        class="px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white"
      >
        <option value="">All Status</option>
        <option value="Planning">Planning</option>
        <option value="In Progress">In Progress</option>
        <option value="Completed">Completed</option>
        <option value="On Hold">On Hold</option>
        <option value="Cancelled">Cancelled</option>
      </select>
    </div>

    <SkeletonLoader v-if="loading" :lines="4" />

    <div v-else-if="filteredProjects.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState
        icon="folder"
        title="No projects found"
        description="Create your first project to get started"
      >
        <router-link
          to="/project/new"
          class="mt-3 inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <feather-icon name="plus" class="w-4 h-4" />
          New Project
        </router-link>
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
          <StatusBadge :status="project.status" />
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
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'ProjectList',
  components: { FeatherIcon, StatusBadge, ProgressBar, SkeletonLoader, EmptyState },
  data() {
    return {
      projects: [],
      loading: true,
      searchQuery: '',
      statusFilter: '',
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
        const result = await call('project_management.api.client.get_projects')
        this.projects = result.message || []
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
