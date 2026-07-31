<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button appearance="minimal" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ task?.title || 'Loading...' }}</h1>
          <Badge v-if="task" :label="task.status" :color-map="statusColorMap" />
          <Badge v-if="task" :label="task.priority" :color-map="statusColorMap" />
        </div>
        <p v-if="task" class="text-sm text-gray-500 mt-0.5">
          {{ task.project }} / {{ task.deliverable }}
        </p>
      </div>
      <Button v-if="task" appearance="secondary" @click="openEditModal">Edit Task</Button>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

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
              <Button appearance="minimal" icon-left="plus" @click="showTimeLogModal = true">Log Time</Button>
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
              <Button
                v-for="status in statusOptions"
                :key="status"
                @click="updateStatus(status)"
                :disabled="task.status === status || updating"
                appearance="minimal"
                :active="task.status === status"
                class="w-full"
              >
                <span class="flex w-full items-center gap-2">
                  <span class="w-2 h-2 rounded-full" :class="statusDotColor(status)" />
                  {{ status }}
                  <span v-if="task.status === status" class="ml-auto text-[10px]">(current)</span>
                </span>
              </Button>
            </div>
          </div>

          <!-- Attachments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <FileUpload doctype="Project Task" :docname="taskId" />
          </div>
        </div>
      </div>
    </template>

    <Dialog v-model="showTimeLogModal" :options="{ title: 'Log Time', size: 'sm' }">
      <template #body-content>
        <div class="space-y-4">
          <Input v-model.number="timeLogForm.hours" type="number" label="Hours *" step="0.25" />
          <Input v-model="timeLogForm.date" type="date" label="Date" />
          <Input v-model="timeLogForm.description" type="textarea" :rows="2" label="Description" />
        </div>
      </template>
      <template #actions="{ close }">
        <Button appearance="secondary" @click="close">Cancel</Button>
        <Button
          appearance="primary"
          :disabled="!timeLogForm.hours"
          :loading="loggingTime"
          :loading-text="loggingTime ? 'Saving...' : null"
          @click="createTimeLog"
        >Log Time</Button>
      </template>
    </Dialog>

    <Dialog v-model="showEditModal" :options="{ title: 'Edit Task', size: 'lg' }">
      <template #body-content>
        <div class="space-y-4">
          <Input v-model="editForm.title" label="Title *" />
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Input
                type="select"
                v-model="editForm.assigned_to"
                label="Assigned To"
                :options="assigneeOptions"
              />
              <Button appearance="minimal" @click="assignEditToMe" class="mt-1">Assign to me</Button>
            </div>
            <Input
              type="select"
              v-model="editForm.priority"
              label="Priority"
              :options="priorityOptions"
            />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <Input type="date" v-model="editForm.start_date" label="Start Date" />
            <Input type="date" v-model="editForm.due_date" label="Due Date" />
          </div>
          <Input v-model.number="editForm.estimated_hours" type="number" label="Estimated Hours" />
          <Input v-model="editForm.description" type="textarea" :rows="2" label="Description" />
        </div>
      </template>
      <template #actions="{ close }">
        <Button appearance="secondary" @click="close">Cancel</Button>
        <Button
          appearance="primary"
          :disabled="!editForm.title"
          :loading="savingTask"
          :loading-text="savingTask ? 'Saving...' : null"
          @click="saveTask"
        >Save Changes</Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, LoadingIndicator, Dialog, Input } from 'frappe-ui'
import { useTask, useTimeLogs, useProject } from '@/data/resources'
import { store } from '@/data/store.js'
import { statusColorMap } from '@/utils/statusColors'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'TaskDetail',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, Dialog, Input, FileUpload, CommentSection },
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
    assigneeOptions() {
      return [
        { label: 'Unassigned', value: '' },
        ...this.projectMembers.map(member => ({ label: member, value: member })),
      ]
    },
    priorityOptions() {
      return ['Low', 'Medium', 'High', 'Critical']
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
          useTask(this.taskId).fetch(),
          useTimeLogs(this.taskId).fetch(),
        ])
        this.task = taskRes
        this.timeLogs = logsRes || []

        if (this.task?.project) {
          const projectRes = await useProject(this.task.project).fetch()
          this.projectMembers = (projectRes?.project_members || []).map(m => m.user)
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
        await frappeRequest({
          url: 'project_management.api.client.update_task_status',
          method: 'POST',
          params: { name: this.taskId, status },
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
        await frappeRequest({
          url: 'project_management.api.client.create_time_log',
          method: 'POST',
          params: {
            task: this.taskId,
            project: this.task.project,
            date: this.timeLogForm.date,
            hours: this.timeLogForm.hours,
            description: this.timeLogForm.description,
          },
        })
        this.showTimeLogModal = false
        this.timeLogForm = { hours: null, date: new Date().toISOString().split('T')[0], description: '' }
        await this.loadAll()
        store.todayHours = (await frappeRequest({ url: 'project_management.api.client.get_today_hours', method: 'POST' })) || 0
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
        this.editForm.assigned_to = await frappeRequest({ url: 'project_management.api.client.get_session_user', method: 'POST' })
      } catch {
        console.error('Failed to get session user')
      }
    },
    async saveTask() {
      this.savingTask = true
      try {
        await frappeRequest({
          url: 'project_management.api.client.update_task',
          method: 'POST',
          params: { name: this.taskId, data: this.editForm },
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
