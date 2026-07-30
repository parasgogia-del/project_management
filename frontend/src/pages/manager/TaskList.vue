<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div class="flex-1">
        <h1 class="text-xl font-bold text-gray-900">Tasks</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
      <button
        @click="showCreateModal = true"
        class="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
      >
        <feather-icon name="plus" class="w-4 h-4" />
        New Task
      </button>
    </div>

    <!-- Filters -->
    <div class="flex items-center gap-3">
      <select
        v-model="statusFilter"
        class="px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none"
      >
        <option value="">All Status</option>
        <option value="Open">Open</option>
        <option value="Working">Working</option>
        <option value="Blocked">Blocked</option>
        <option value="Completed">Completed</option>
      </select>
      <select
        v-model="priorityFilter"
        class="px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none"
      >
        <option value="">All Priority</option>
        <option value="Low">Low</option>
        <option value="Medium">Medium</option>
        <option value="High">High</option>
        <option value="Critical">Critical</option>
      </select>
    </div>

    <SkeletonLoader v-if="loading" :lines="4" />

    <div v-else-if="filteredTasks.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState icon="list" title="No tasks found" description="Create your first task to get started" />
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-100">
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Task</th>
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
            <td class="px-5 py-3"><StatusBadge :status="task.status" /></td>
            <td class="px-5 py-3"><StatusBadge :status="task.priority" /></td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ task.assigned_to || '-' }}</td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ task.due_date || '-' }}</td>
            <td class="px-5 py-3 text-xs text-gray-600">
              {{ task.actual_hours || 0 }}h / {{ task.estimated_hours || 0 }}h
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create Task Modal -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      @click.self="showCreateModal = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Create Task</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input v-model="newTask.title" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400" placeholder="Task title" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Deliverable *</label>
            <select v-model="newTask.deliverable" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white">
              <option value="">Select deliverable</option>
              <option v-for="d in projectDeliverables" :key="d.name" :value="d.name">{{ d.title }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
              <select v-model="newTask.assigned_to" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white">
                <option value="">Unassigned</option>
                <option v-for="member in projectMembers" :key="member" :value="member">{{ member }}</option>
              </select>
              <button @click="assignToMe" type="button" class="mt-1 text-xs text-blue-600 hover:text-blue-700">Assign to me</button>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select v-model="newTask.priority" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none">
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
                <option>Critical</option>
              </select>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input v-model="newTask.start_date" type="date" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <input v-model="newTask.due_date" type="date" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estimated Hours</label>
            <input v-model.number="newTask.estimated_hours" type="number" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="newTask.description" rows="2" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none resize-none" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button @click="showCreateModal = false" class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">Cancel</button>
          <button
            @click="createTask"
            :disabled="!newTask.title || !newTask.deliverable || creating"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ creating ? 'Creating...' : 'Create Task' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'TaskList',
  components: { FeatherIcon, StatusBadge, SkeletonLoader, EmptyState },
  data() {
    return {
      tasks: [],
      projectMembers: [],
      projectDeliverables: [],
      loading: true,
      statusFilter: '',
      priorityFilter: '',
      showCreateModal: false,
      creating: false,
      newTask: {
        title: '',
        deliverable: '',
        assigned_to: '',
        priority: 'Medium',
        start_date: '',
        due_date: '',
        estimated_hours: null,
        description: '',
      },
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
    filteredTasks() {
      return this.tasks.filter(t => {
        const matchStatus = !this.statusFilter || t.status === this.statusFilter
        const matchPriority = !this.priorityFilter || t.priority === this.priorityFilter
        return matchStatus && matchPriority
      })
    },
  },
  mounted() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [tasksRes, projectRes, deliverablesRes] = await Promise.all([
          call('project_management.api.client.get_tasks', { project: this.projectId }),
          call('project_management.api.client.get_project', { name: this.projectId }),
          call('project_management.api.client.get_deliverables', { project: this.projectId }),
        ])
        this.tasks = tasksRes.message || []
        this.projectMembers = (projectRes.message?.project_members || []).map(m => m.user)
        this.projectDeliverables = deliverablesRes.message || []
      } catch {
        this.tasks = []
        this.projectMembers = []
        this.projectDeliverables = []
      } finally {
        this.loading = false
      }
    },
    async createTask() {
      this.creating = true
      try {
        await call('project_management.api.client.create_task', {
          data: {
            ...this.newTask,
            project: this.projectId,
            status: 'Open',
          },
        })
        this.showCreateModal = false
        this.resetNewTask()
        await this.loadAll()
      } catch (err) {
        console.error('Failed to create task', err)
      } finally {
        this.creating = false
      }
    },
    async assignToMe() {
      try {
        const result = await call('project_management.api.client.get_session_user')
        this.newTask.assigned_to = result.message
      } catch {
        console.error('Failed to get session user')
      }
    },
    resetNewTask() {
      this.newTask = { title: '', deliverable: '', assigned_to: '', priority: 'Medium', start_date: '', due_date: '', estimated_hours: null, description: '' }
    },
  },
}
</script>
