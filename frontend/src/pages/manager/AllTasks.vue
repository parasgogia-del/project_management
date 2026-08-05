<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <div class="flex-1">
        <h1 class="text-xl font-bold text-gray-900">All Tasks</h1>
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
        class="w-40"
      />
      <Input
        type="select"
        v-model="priorityFilter"
        :options="priorityFilterOptions"
        class="w-40"
      />
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <div v-else-if="filteredTasks.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState icon="list" title="No tasks found" description="Create your first task to get started" />
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-100">
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Task</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Project</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Status</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Priority</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Assigned To</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Due Date</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Hours</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="task in filteredTasks"
            :key="task.name"
            @click="$router.push(`/task/${task.name}`)"
            class="hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <td class="px-5 py-3">
              <p class="text-sm font-medium text-gray-800">{{ task.title }}</p>
              <p class="text-xs text-gray-400">{{ task.deliverable }}</p>
            </td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ projectName(task.project) }}</td>
            <td class="px-5 py-3"><Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" /></td>
            <td class="px-5 py-3"><Badge :label="task.priority" :theme="statusColorMap[task.priority] || 'gray'" /></td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ task.assigned_to || '-' }}</td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ task.due_date || '-' }}</td>
            <td class="px-5 py-3 text-xs text-gray-600">
              {{ task.actual_hours || 0 }}h / {{ task.estimated_hours || 0 }}h
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, Badge, LoadingIndicator, Input, frappeRequest } from 'frappe-ui'
import { useTasks } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'AllTasks',
  components: { FeatherIcon, Badge, LoadingIndicator, Input, EmptyState },
  data() {
    return {
      tasks: [],
      projects: [],
      loading: true,
      projectFilter: '',
      statusFilter: '',
      priorityFilter: '',
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
        { label: 'Open', value: 'Open' },
        { label: 'Working', value: 'Working' },
        { label: 'Blocked', value: 'Blocked' },
        { label: 'Completed', value: 'Completed' },
      ]
    },
    priorityFilterOptions() {
      return [
        { label: 'All Priority', value: '' },
        { label: 'Low', value: 'Low' },
        { label: 'Medium', value: 'Medium' },
        { label: 'High', value: 'High' },
        { label: 'Critical', value: 'Critical' },
      ]
    },
    filteredTasks() {
      return this.tasks.filter(t => {
        const matchProject = !this.projectFilter || t.project === this.projectFilter
        const matchStatus = !this.statusFilter || t.status === this.statusFilter
        const matchPriority = !this.priorityFilter || t.priority === this.priorityFilter
        return matchProject && matchStatus && matchPriority
      })
    },
  },
  methods: {
    projectName(name) {
      if (!name) return '-'
      const found = this.projects.find(p => p.name === name)
      return found ? found.project_name : name
    },
    async loadTasks() {
      this.loading = true
      try {
        const [tasks, projects] = await Promise.all([
          useTasks().fetch(),
          frappeRequest({ url: 'project_management.api.client.get_projects', method: 'POST' }),
        ])
        this.tasks = tasks || []
        this.projects = projects || []
      } catch {
        this.tasks = []
      } finally {
        this.loading = false
      }
    },
  },
  mounted() {
    this.loadTasks()
  },
}
</script>
