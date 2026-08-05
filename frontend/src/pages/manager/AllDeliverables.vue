<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <div>
        <h1 class="text-xl font-bold text-gray-900">All Deliverables</h1>
        <p class="text-sm text-gray-500 mt-0.5">Across all projects</p>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <Input
        type="select"
        v-model="projectFilter"
        :options="projectFilterOptions"
        class="w-48"
      />
      <Input
        type="select"
        v-model="statusFilter"
        :options="statusFilterOptions"
        class="w-48"
      />
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <div v-else-if="filteredDeliverables.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState
        icon="package"
        title="No deliverables found"
        description="Deliverables will appear here once created"
      />
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-100">
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Title</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Project</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Status</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Progress</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Due Date</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Members</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="d in filteredDeliverables"
            :key="d.name"
            @click="$router.push(`/deliverable/${d.name}`)"
            class="hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <td class="px-5 py-3">
              <p class="text-sm font-medium text-gray-800">{{ d.title }}</p>
              <p class="text-xs text-gray-400">{{ d.description?.slice(0, 60) || 'No description' }}</p>
            </td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ projectName(d.project) }}</td>
            <td class="px-5 py-3"><Badge :label="d.status" :theme="statusColorMap[d.status] || 'gray'" /></td>
            <td class="px-5 py-3 w-40">
              <ProgressBar :value="d.progress || 0" />
              <p class="text-[10px] text-gray-400 mt-0.5">{{ d.completed_tasks || 0 }}/{{ d.total_tasks || 0 }} tasks</p>
            </td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ d.due_date || '-' }}</td>
            <td class="px-5 py-3">
              <div class="flex -space-x-1">
                <Avatar
                  v-for="(m, i) in (d.members || []).slice(0, 3)"
                  :key="i"
                  :label="m"
                  size="sm"
                  class="ring-2 ring-white"
                  :title="m"
                />
                <div
                  v-if="(d.members || []).length > 3"
                  class="w-5 h-5 rounded-full bg-gray-100 ring-2 ring-white flex items-center justify-center"
                >
                  <span class="text-[8px] font-medium text-gray-500">+{{ d.members.length - 3 }}</span>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, Badge, Avatar, LoadingIndicator, Input } from 'frappe-ui'
import { useDeliverablesWithDetails } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'
import EmptyState from '@/components/EmptyState.vue'
import { frappeRequest } from 'frappe-ui'

export default {
  name: 'AllDeliverables',
  components: { FeatherIcon, Badge, Avatar, LoadingIndicator, Input, ProgressBar, EmptyState },
  data() {
    return {
      deliverables: [],
      projects: [],
      loading: true,
      projectFilter: '',
      statusFilter: '',
    }
  },
  computed: {
    projectFilterOptions() {
      return [
        { label: 'All Projects', value: '' },
        ...this.projects.map(p => ({ label: p.project_name, value: p.name })),
      ]
    },
    statusFilterOptions() {
      return [
        { label: 'All Status', value: '' },
        { label: 'Draft', value: 'Draft' },
        { label: 'WIP', value: 'WIP' },
        { label: 'Ready for Approval', value: 'Ready for Approval' },
        { label: 'Awaiting Client Review', value: 'Awaiting Client Review' },
        { label: 'Approved', value: 'Approved' },
        { label: 'Changes Requested', value: 'Changes Requested' },
      ]
    },
    filteredDeliverables() {
      return this.deliverables.filter(d => {
        const matchProject = !this.projectFilter || d.project === this.projectFilter
        const matchStatus = !this.statusFilter || d.status === this.statusFilter
        return matchProject && matchStatus
      })
    },
  },
  methods: {
    projectName(name) {
      if (!name) return '-'
      const found = this.projects.find(p => p.name === name)
      return found ? found.project_name : name
    },
    async loadDeliverables() {
      this.loading = true
      try {
        const [deliverables, projects] = await Promise.all([
          useDeliverablesWithDetails().fetch(),
          frappeRequest({ url: 'project_management.api.client.get_projects', method: 'POST' }),
        ])
        this.deliverables = deliverables || []
        this.projects = projects || []
      } catch {
        this.deliverables = []
      } finally {
        this.loading = false
      }
    },
  },
  mounted() {
    this.loadDeliverables()
  },
}
</script>
