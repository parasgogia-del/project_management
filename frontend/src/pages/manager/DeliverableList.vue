<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <h1 class="text-xl font-bold text-gray-900">Deliverables</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
      <Button theme="blue" variant="solid" icon-left="plus" @click="showCreateModal = true">New Deliverable</Button>
    </div>

    <div class="flex items-center gap-3">
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

    <Dialog v-model="showCreateModal" :options="{ title: 'Create Deliverable', size: 'lg' }">
      <template #body-content>
        <div class="space-y-4">
          <Input v-model="newDeliverable.title" label="Title *" placeholder="Deliverable title" />
          <Input type="date" v-model="newDeliverable.due_date" label="Due Date" />
          <Input v-model="newDeliverable.description" type="textarea" :rows="3" label="Description" />
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Cancel</Button>
        <Button
          theme="blue" variant="solid"
          :disabled="!newDeliverable.title"
          :loading="creating"
          :loading-text="creating ? 'Creating...' : null"
          @click="createDeliverable"
        >Create Deliverable</Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, Avatar, LoadingIndicator, Dialog, Input } from 'frappe-ui'
import { useDeliverablesWithDetails } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'DeliverableList',
  components: { FeatherIcon, Button, Badge, Avatar, LoadingIndicator, Dialog, Input, ProgressBar, EmptyState },
  data() {
    return {
      deliverables: [],
      loading: true,
      statusFilter: '',
      showCreateModal: false,
      creating: false,
      newDeliverable: {
        title: '',
        due_date: '',
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
        { label: 'Draft', value: 'Draft' },
        { label: 'WIP', value: 'WIP' },
        { label: 'Ready for Approval', value: 'Ready for Approval' },
        { label: 'Awaiting Client Review', value: 'Awaiting Client Review' },
        { label: 'Approved', value: 'Approved' },
        { label: 'Changes Requested', value: 'Changes Requested' },
      ]
    },
    filteredDeliverables() {
      if (!this.statusFilter) return this.deliverables
      return this.deliverables.filter(d => d.status === this.statusFilter)
    },
  },
  mounted() {
    this.loadDeliverables()
  },
  methods: {
    async loadDeliverables() {
      this.loading = true
      try {
        this.deliverables = (await useDeliverablesWithDetails(this.projectId).fetch()) || []
      } catch {
        this.deliverables = []
      } finally {
        this.loading = false
      }
    },
    async createDeliverable() {
      this.creating = true
      try {
        await frappeRequest({
          url: 'project_management.api.client.create_deliverable',
          method: 'POST',
          params: {
            data: {
              ...this.newDeliverable,
              project: this.projectId,
            },
          },
        })
        this.showCreateModal = false
        this.newDeliverable = { title: '', due_date: '', description: '' }
        await this.loadDeliverables()
      } catch (err) {
        console.error('Failed to create deliverable', err)
      } finally {
        this.creating = false
      }
    },
  },
}
</script>
