<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button appearance="minimal" icon="arrow-left" @click="$router.back()" />
      <div>
        <h1 class="text-xl font-bold text-gray-900">{{ task?.title || 'Loading...' }}</h1>
        <p class="text-sm text-gray-500 mt-0.5">{{ task?.project }}</p>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <template v-else-if="task">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <!-- Task Info -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <div class="flex items-center gap-3 mb-4">
              <Badge :label="task.status" :color-map="statusColorMap" />
              <Badge :label="task.priority" :color-map="statusColorMap" />
            </div>
            <p class="text-sm text-gray-600">{{ task.description || 'No description' }}</p>
            <div class="grid grid-cols-3 gap-4 mt-4 text-sm">
              <div>
                <p class="text-xs text-gray-500">Due Date</p>
                <p class="text-gray-700">{{ task.due_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Estimated</p>
                <p class="text-gray-700">{{ task.estimated_hours || '-' }}h</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Actual Hours</p>
                <p class="text-gray-700 font-semibold">{{ task.actual_hours || 0 }}h</p>
              </div>
            </div>
            <div v-if="deliverable" class="mt-3 pt-3 border-t border-gray-100">
              <a @click="$router.push(`/vendor/deliverable/${deliverable.name}`)" class="text-xs text-blue-600 hover:underline cursor-pointer">
                View Deliverable: {{ deliverable.title }}
              </a>
            </div>
          </div>

          <!-- Time Logs -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <div class="flex items-center justify-between mb-3">
              <h2 class="text-sm font-semibold text-gray-800">Time Logs</h2>
              <Button appearance="minimal" icon-left="plus" @click="showTimeLogModal = true">Log Time</Button>
            </div>
            <div v-if="timeLogs.length === 0" class="text-xs text-gray-400 text-center py-4">No time logged</div>
            <div v-else class="space-y-2">
              <div v-for="log in timeLogs" :key="log.name" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p class="text-sm text-gray-800">{{ log.hours }}h - {{ log.description || 'No description' }}</p>
                  <p class="text-xs text-gray-400">{{ log.date }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="space-y-6">
          <!-- Status Update -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Update Status</h2>
            <div class="space-y-2">
              <Button
                v-for="s in ['Open', 'Working', 'Blocked', 'Completed']"
                :key="s"
                @click="updateStatus(s)"
                :disabled="task.status === s || updating"
                appearance="minimal"
                :active="task.status === s"
                class="w-full"
              >
                <span class="flex w-full items-center gap-2">
                  <span class="w-2 h-2 rounded-full" :class="statusDotColor(s)" />
                  {{ s }} <span v-if="task.status === s" class="ml-auto text-[10px]">(current)</span>
                </span>
              </Button>
            </div>
          </div>

          <!-- Files -->
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
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, LoadingIndicator, Dialog, Input } from 'frappe-ui'
import { useTask, useTimeLogs } from '@/data/resources'
import { store } from '@/data/store.js'
import FileUpload from '@/components/FileUpload.vue'

export default {
  name: 'VendorTaskPage',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, Dialog, Input, FileUpload },
  data() {
    return {
      task: null, deliverable: null, timeLogs: [], loading: true, updating: false,
      showTimeLogModal: false, loggingTime: false,
      timeLogForm: { hours: null, date: new Date().toISOString().split('T')[0], description: '' },
    }
  },
  computed: { taskId() { return this.$route.params.id } },
  mounted() { this.loadAll() },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [t, l, d] = await Promise.all([
          useTask(this.taskId).fetch(),
          useTimeLogs(this.taskId).fetch(),
          frappeRequest({ url: 'project_management.api.client.get_deliverable_for_task', method: 'POST', params: { task: this.taskId } }),
        ])
        this.task = t; this.timeLogs = l || []; this.deliverable = d?.found ? d : null
      } catch {} finally { this.loading = false }
    },
    async updateStatus(status) {
      this.updating = true
      try {
        await frappeRequest({ url: 'project_management.api.client.update_task_status', method: 'POST', params: { name: this.taskId, status } })
        await this.loadAll()
      } catch {} finally { this.updating = false }
    },
    async createTimeLog() {
      this.loggingTime = true
      try {
        await frappeRequest({
          url: 'project_management.api.client.create_time_log',
          method: 'POST',
          params: {
            task: this.taskId, project: this.task.project,
            date: this.timeLogForm.date, hours: this.timeLogForm.hours, description: this.timeLogForm.description,
          },
        })
        this.showTimeLogModal = false
        this.timeLogForm = { hours: null, date: new Date().toISOString().split('T')[0], description: '' }
        await this.loadAll()
        store.todayHours = (await frappeRequest({ url: 'project_management.api.client.get_today_hours', method: 'POST' })) || 0
      } catch {} finally { this.loggingTime = false }
    },
    statusDotColor(status) {
      const colors = { Open: 'bg-gray-400', Working: 'bg-blue-500', Blocked: 'bg-red-500', Completed: 'bg-green-500' }
      return colors[status] || 'bg-gray-400'
    },
  },
}
</script>
