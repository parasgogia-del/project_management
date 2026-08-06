<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <h1 class="text-xl font-bold text-gray-900">Tasks</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
      <Button theme="blue" variant="solid" icon-left="plus" @click="showCreateModal = true">New Task</Button>
    </div>

    <div class="flex items-center gap-3">
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

    <Dialog v-model="showCreateModal" :options="{ title: 'Create Task', size: 'lg' }">
      <template #body-content>
        <div class="space-y-4">
          <Input v-model="newTask.title" label="Title *" placeholder="Task title" />
          <Input
            type="select"
            v-model="newTask.deliverable"
            label="Deliverable *"
            :options="deliverableOptions"
          />
          <div class="grid grid-cols-2 gap-4">
            <div>
              <Input
                type="select"
                v-model="newTask.assigned_to"
                label="Assigned To"
                :options="memberOptions"
              />
              <Button variant="ghost" @click="assignToMe" class="mt-1">Assign to me</Button>
            </div>
            <Input
              type="select"
              v-model="newTask.priority"
              label="Priority"
              :options="priorityOptions"
            />
          </div>
          <Input
            type="select"
            v-model="newTask.assigned_vendor"
            label="Assigned Vendor"
            :options="vendorOptions"
          />
          <div class="grid grid-cols-2 gap-4">
            <Input type="date" v-model="newTask.start_date" label="Start Date" />
            <Input type="date" v-model="newTask.due_date" label="Due Date" />
          </div>
          <Input v-model.number="newTask.estimated_hours" type="number" label="Estimated Hours" />
          <Input v-model="newTask.description" type="textarea" :rows="2" label="Description" />
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Cancel</Button>
        <Button
          theme="blue" variant="solid"
          :disabled="!newTask.title || !newTask.deliverable"
          :loading="creating"
          :loading-text="creating ? 'Creating...' : null"
          @click="createTask"
        >Create Task</Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, LoadingIndicator, Dialog, Input } from 'frappe-ui'
import { useTasks, useProject, useDeliverables } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'TaskList',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, Dialog, Input, EmptyState },
  data() {
    return {
      tasks: [],
      projectMembers: [],
      projectVendors: [],
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
        assigned_vendor: '',
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
    deliverableOptions() {
      return [
        { label: 'Select deliverable', value: '' },
        ...this.projectDeliverables.map(d => ({ label: d.title, value: d.name })),
      ]
    },
    memberOptions() {
      return [
        { label: 'Unassigned', value: '' },
        ...this.projectMembers.map(member => ({ label: member, value: member })),
      ]
    },
    vendorOptions() {
      return [
        { label: 'No vendor', value: '' },
        ...this.projectVendors.map(vendor => ({ label: vendor, value: vendor })),
      ]
    },
    priorityOptions() {
      return ['Low', 'Medium', 'High', 'Critical']
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
          useTasks({ project: this.projectId }).fetch(),
          useProject(this.projectId).fetch(),
          useDeliverables(this.projectId).fetch(),
        ])
        this.tasks = tasksRes || []
        this.projectMembers = (projectRes?.project_members || []).map(m => m.user)
        this.projectVendors = (projectRes?.vendors || []).map(v => v.vendor).filter(Boolean)
        this.projectDeliverables = deliverablesRes || []
      } catch {
        this.tasks = []
        this.projectMembers = []
        this.projectVendors = []
        this.projectDeliverables = []
      } finally {
        this.loading = false
      }
    },
    async createTask() {
      this.creating = true
      try {
        await frappeRequest({
          url: 'project_management.api.client.create_task',
          method: 'POST',
          params: {
            data: {
              ...this.newTask,
              project: this.projectId,
              status: 'Open',
            },
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
        this.newTask.assigned_to = await frappeRequest({ url: 'project_management.api.client.get_session_user', method: 'POST' })
      } catch {
        console.error('Failed to get session user')
      }
    },
    resetNewTask() {
      this.newTask = { title: '', deliverable: '', assigned_to: '', assigned_vendor: '', priority: 'Medium', start_date: '', due_date: '', estimated_hours: null, description: '' }
    },
  },
}
</script>
