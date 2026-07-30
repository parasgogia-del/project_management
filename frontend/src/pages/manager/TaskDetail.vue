<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ task?.title || 'Loading...' }}</h1>
          <StatusBadge v-if="task" :status="task.status" />
          <StatusBadge v-if="task" :status="task.priority" />
        </div>
        <p v-if="task" class="text-sm text-gray-500 mt-0.5">
          {{ task.project }} / {{ task.deliverable }}
        </p>
      </div>
      <button
        v-if="task"
        @click="openEditModal"
        class="px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
      >
        Edit Task
      </button>
    </div>

    <SkeletonLoader v-if="loading" :lines="5" />

    <template v-else-if="task">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Main -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Task Details -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Task Details</h2>
            <div class="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p class="text-xs text-gray-500">Description</p>
                <p class="text-gray-700 mt-0.5">{{ task.description || 'No description' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Assigned To</p>
                <p class="text-gray-700 mt-0.5">{{ task.assigned_to || 'Unassigned' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Assigned Vendor</p>
                <p class="text-gray-700 mt-0.5">{{ task.assigned_vendor || 'None' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Start Date</p>
                <p class="text-gray-700 mt-0.5">{{ task.start_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Due Date</p>
                <p class="text-gray-700 mt-0.5">{{ task.due_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Estimated Hours</p>
                <p class="text-gray-700 mt-0.5">{{ task.estimated_hours || '-' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Actual Hours</p>
                <p class="text-gray-700 mt-0.5 font-semibold">{{ task.actual_hours || 0 }}h</p>
              </div>
            </div>
          </div>

          <!-- Time Logs -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-sm font-semibold text-gray-800">Time Logs</h2>
              <button
                @click="showTimeLogModal = true"
                class="text-xs font-medium text-blue-600 hover:text-blue-700"
              >+ Log Time</button>
            </div>
            <div v-if="timeLogs.length === 0" class="text-xs text-gray-400 text-center py-4">
              No time logged yet
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="log in timeLogs"
                :key="log.name"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p class="text-sm text-gray-800">{{ log.hours }}h - {{ log.description || 'No description' }}</p>
                  <p class="text-xs text-gray-400">{{ log.project_member }} | {{ log.date }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Comments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <CommentSection doctype="Project Task" :docname="taskId" />
          </div>
        </div>

        <!-- Right -->
        <div class="space-y-6">
          <!-- Status Actions -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Update Status</h2>
            <div class="space-y-2">
              <button
                v-for="status in statusOptions"
                :key="status"
                @click="updateStatus(status)"
                :disabled="task.status === status || updating"
                class="w-full px-3 py-2 text-xs font-medium rounded-lg transition-colors text-left"
                :class="task.status === status ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'bg-gray-50 text-gray-600 hover:bg-gray-100'"
              >
                <span class="flex items-center gap-2">
                  <span class="w-2 h-2 rounded-full" :class="statusDotColor(status)" />
                  {{ status }}
                  <span v-if="task.status === status" class="ml-auto text-[10px]">(current)</span>
                </span>
              </button>
            </div>
          </div>

          <!-- Attachments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <FileUpload doctype="Project Task" :docname="taskId" />
          </div>
        </div>
      </div>
    </template>

    <!-- Time Log Modal -->
    <div
      v-if="showTimeLogModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      @click.self="showTimeLogModal = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Log Time</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Hours *</label>
            <input v-model.number="timeLogForm.hours" type="number" step="0.25" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Date</label>
            <input v-model="timeLogForm.date" type="date" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="timeLogForm.description" rows="2" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none resize-none" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button @click="showTimeLogModal = false" class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">Cancel</button>
          <button
            @click="createTimeLog"
            :disabled="!timeLogForm.hours || loggingTime"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ loggingTime ? 'Saving...' : 'Log Time' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Task Modal -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      @click.self="showEditModal = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-4">Edit Task</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input v-model="editForm.title" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Assigned To</label>
              <select v-model="editForm.assigned_to" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none">
                <option value="">Unassigned</option>
                <option v-for="member in projectMembers" :key="member" :value="member">{{ member }}</option>
              </select>
              <button @click="assignEditToMe" type="button" class="mt-1 text-xs text-blue-600 hover:text-blue-700">Assign to me</button>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select v-model="editForm.priority" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none">
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
              <input v-model="editForm.start_date" type="date" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <input v-model="editForm.due_date" type="date" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none" />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Estimated Hours</label>
            <input v-model.number="editForm.estimated_hours" type="number" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="editForm.description" rows="2" class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none resize-none" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button @click="showEditModal = false" class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200">Cancel</button>
          <button
            @click="saveTask"
            :disabled="!editForm.title || savingTask"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {{ savingTask ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </div>
    </div>

    <Toast ref="toast" />
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
// import { store } from '@/data/store.js'
import StatusBadge from '@/components/StatusBadge.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'
import Toast from '@/components/Toast.vue'

export default {
  name: 'TaskDetail',
  components: { FeatherIcon, StatusBadge, SkeletonLoader, FileUpload, CommentSection, Toast },
  data() {
    return {
      task: null,
      timeLogs: [],
      projectMembers: [],
      loading: true,
      updating: false,
      showTimeLogModal: false,
      showEditModal: false,
      loggingTime: false,
      savingTask: false,
      statusOptions: ['Open', 'Working', 'Blocked', 'Completed'],
      timeLogForm: {
        hours: null,
        date: new Date().toISOString().split('T')[0],
        description: '',
      },
      editForm: {
        title: '',
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
    taskId() {
      return this.$route.params.id
    },
  },
  mounted() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [taskRes, logsRes] = await Promise.all([
          call('project_management.api.client.get_task', { name: this.taskId }),
          call('project_management.api.client.get_time_logs', { task: this.taskId }),
        ])
        this.task = taskRes.message
        this.timeLogs = logsRes.message || []

        if (this.task?.project) {
          const projectRes = await call('project_management.api.client.get_project', { name: this.task.project })
          this.projectMembers = (projectRes.message?.project_members || []).map(m => m.user)
        }
      } catch {
        console.error('Failed to load task')
      } finally {
        this.loading = false
      }
    },
    async updateStatus(status) {
      this.updating = true
      try {
        await call('project_management.api.client.update_task_status', {
          name: this.taskId,
          status,
        })
        await this.loadAll()
      } catch (err) {
        console.error('Failed to update status', err)
      } finally {
        this.updating = false
      }
    },
    async createTimeLog() {
      this.loggingTime = true
      try {
        await call('project_management.api.client.create_time_log', {
          task: this.taskId,
          project: this.task.project,
          date: this.timeLogForm.date,
          hours: this.timeLogForm.hours,
          description: this.timeLogForm.description,
        })
        this.showTimeLogModal = false
        this.timeLogForm = { hours: null, date: new Date().toISOString().split('T')[0], description: '' }
        await this.loadAll()
        const hours = await call('project_management.api.client.get_today_hours')
        store.todayHours = hours.message || 0
      } catch (err) {
        console.error('Failed to log time', err)
      } finally {
        this.loggingTime = false
      }
    },
    openEditModal() {
      this.editForm = {
        title: this.task.title || '',
        assigned_to: this.task.assigned_to || '',
        priority: this.task.priority || 'Medium',
        start_date: this.task.start_date || '',
        due_date: this.task.due_date || '',
        estimated_hours: this.task.estimated_hours || null,
        description: this.task.description || '',
      }
      this.showEditModal = true
    },
    async assignEditToMe() {
      try {
        const result = await call('project_management.api.client.get_session_user')
        this.editForm.assigned_to = result.message
      } catch {
        console.error('Failed to get session user')
      }
    },
    async saveTask() {
      this.savingTask = true
      try {
        await call('project_management.api.client.update_task', {
          name: this.taskId,
          data: this.editForm,
        })
        this.showEditModal = false
        await this.loadAll()
      } catch (err) {
        console.error('Failed to update task', err)
      } finally {
        this.savingTask = false
      }
    },
    statusDotColor(status) {
      const colors = { Open: 'bg-gray-400', Working: 'bg-blue-500', Blocked: 'bg-red-500', Completed: 'bg-green-500' }
      return colors[status] || 'bg-gray-400'
    },
  },
}
</script>
