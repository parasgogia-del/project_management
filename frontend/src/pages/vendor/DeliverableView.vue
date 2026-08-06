<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ deliverable?.title || 'Loading...' }}</h1>
          <Badge v-if="deliverable" :label="deliverable.status" :theme="statusColorMap[deliverable.status] || 'gray'" />
        </div>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <template v-else-if="deliverable">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <!-- Details -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Details</h2>
            <p class="text-sm text-gray-600">{{ deliverable.description || 'No description' }}</p>
            <div class="grid grid-cols-2 gap-4 mt-4 text-sm">
              <div>
                <p class="text-xs text-gray-500">Due Date</p>
                <p class="text-gray-700">{{ deliverable.due_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">Delivery Date</p>
                <p class="text-gray-700">{{ deliverable.delivery_date || 'Not delivered' }}</p>
              </div>
              <div v-if="deliverable.access_link__notes">
                <p class="text-xs text-gray-500">Access Link / Notes</p>
                <p class="text-gray-700">{{ deliverable.access_link__notes }}</p>
              </div>
              <div v-if="deliverable.submitted_by">
                <p class="text-xs text-gray-500">Submitted By</p>
                <p class="text-gray-700">{{ deliverable.submitted_by }}</p>
              </div>
            </div>
          </div>

          <!-- Files -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <FileUpload doctype="Deliverable" :docname="deliverableId" />
          </div>

          <!-- Comments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <CommentSection doctype="Deliverable" :docname="deliverableId" />
          </div>
        </div>

        <div class="space-y-6">
          <!-- Vendor Actions -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Actions</h2>
            <div class="space-y-2">
              <Button
                v-if="deliverable.status === 'WIP'"
                @click="showDeliveryDialog = true"
                :disabled="updating"
                theme="blue" variant="solid"
                class="w-full"
              >Submit Delivery</Button>
              <Button
                v-for="action in availableActions"
                :key="action"
                @click="performAction(action)"
                :disabled="updating"
                theme="blue" variant="solid"
                class="w-full"
              >{{ action }}</Button>
              <p v-if="availableActions.length === 0 && deliverable.status !== 'WIP' && !updating" class="text-xs text-gray-400 text-center">No actions available</p>
              <p v-if="updateError" class="text-xs text-red-500">{{ updateError }}</p>
            </div>
          </div>

          <!-- Tasks in this deliverable -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Tasks</h2>
            <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">No tasks</div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="t in tasks"
                :key="t.name"
                @click="$router.push(`/vendor/task/${t.name}`)"
                class="flex items-center justify-between py-2 cursor-pointer hover:bg-gray-50 rounded transition-colors"
              >
                <p class="text-xs text-gray-800 truncate">{{ t.title }}</p>
                <Badge :label="t.status" :theme="statusColorMap[t.status] || 'gray'" />
              </div>
            </div>
          </div>

          <!-- Progress -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-2">Progress</h2>
            <div class="text-center py-4">
              <p class="text-3xl font-bold text-gray-900">{{ progress }}%</p>
              <p class="text-xs text-gray-400 mt-1">{{ completedTasks }}/{{ totalTasks }} tasks</p>
            </div>
          </div>
        </div>
      </div>

    </template>

    <Dialog v-model="showDeliveryDialog" :options="{ title: 'Submit Delivery', size: 'sm' }">
      <template #body-content>
        <div class="space-y-4">
          <div>
            <p class="text-xs text-gray-500 mb-1.5">Attach File</p>
            <div class="flex items-center gap-3">
              <label class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors">
                <feather-icon name="upload" class="w-3.5 h-3.5" />
                Upload
                <input type="file" class="hidden" @change="handleUpload" />
              </label>
              <span class="text-xs text-gray-600 truncate">{{ uploadedFile || 'No file selected' }}</span>
            </div>
            <div v-if="uploading" class="text-xs text-blue-600 mt-1.5">Uploading...</div>
          </div>
          <Input
            v-model="deliveryNotes"
            type="textarea"
            :rows="3"
            label="Delivery Note / Access Link"
            placeholder="e.g. https://drive.google.com/... or a note about this delivery"
          />
          <p v-if="deliveryError" class="text-xs text-red-500">{{ deliveryError }}</p>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Cancel</Button>
        <Button
          theme="blue" variant="solid"
          :disabled="submitting || (!uploadedFile && !deliveryNotes)"
          :loading="submitting"
          :loading-text="submitting ? 'Submitting...' : null"
          @click="submitDelivery"
        >Submit Delivery</Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, LoadingIndicator, Dialog, Input } from 'frappe-ui'
import { useDeliverable, useTasks } from '@/data/resources'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'

const VENDOR_ACTIONS = {
  'Draft': ['Start Work'],
  'WIP': [],
  'Ready for Approval': [],
  'Awaiting Client Review': [],
  'Approved': [],
  'Changes Requested': ['Start Rework'],
}

export default {
  name: 'VendorDeliverableView',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, Dialog, Input, FileUpload, CommentSection },
  data() {
    return {
      deliverable: null, tasks: [], loading: true, updating: false, updateError: '',
      showDeliveryDialog: false, uploading: false, submitting: false, deliveryError: '',
      uploadedFile: '', uploadedFileUrl: '', deliveryNotes: '',
    }
  },
  computed: {
    deliverableId() { return this.$route.params.id },
    availableActions() {
      if (!this.deliverable) return []
      return VENDOR_ACTIONS[this.deliverable.status] || []
    },
    totalTasks() { return this.tasks.length },
    completedTasks() { return this.tasks.filter(t => t.status === 'Completed').length },
    progress() { return this.totalTasks ? Math.round((this.completedTasks / this.totalTasks) * 100) : 0 },
  },
  mounted() { this.loadAll() },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const [d, t] = await Promise.all([
          useDeliverable(this.deliverableId).fetch(),
          useTasks({ deliverable: this.deliverableId }).fetch(),
        ])
        this.deliverable = d; this.tasks = t || []
      } catch {} finally { this.loading = false }
    },
    async performAction(action) {
      this.updating = true; this.updateError = ''
      try {
        await frappeRequest({
          url: 'project_management.api.client.update_deliverable_status',
          method: 'POST',
          params: { name: this.deliverableId, action },
        })
        await this.loadAll()
      } catch (err) {
        this.updateError = err.message || 'Failed'
      } finally { this.updating = false }
    },
    async handleUpload(e) {
      const file = e.target.files[0]
      if (!file) return
      this.uploading = true; this.deliveryError = ''
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('deliverable', this.deliverableId)
        const token = window.csrf_token || (typeof frappe !== 'undefined' && frappe.csrf_token) || ''
        if (token) formData.append('csrf_token', token)
        const resp = await fetch('/api/method/project_management.api.file.upload_deliverable_file', {
          method: 'POST',
          body: formData,
        })
        const data = await resp.json()
        if (!resp.ok) throw new Error(data?.message || 'Upload failed')
        this.uploadedFileUrl = data?.message?.file_url || ''
        this.uploadedFile = data?.message?.file_name || file.name
      } catch (err) {
        this.deliveryError = err.message || 'Upload failed'
      } finally {
        this.uploading = false
        e.target.value = ''
      }
    },
    async submitDelivery() {
      this.submitting = true; this.deliveryError = ''
      try {
        await frappeRequest({
          url: 'project_management.api.vendor.submit_deliverable',
          method: 'POST',
          params: { name: this.deliverableId, file_url: this.uploadedFileUrl, notes: this.deliveryNotes },
        })
        this.showDeliveryDialog = false
        this.uploadedFile = ''; this.uploadedFileUrl = ''; this.deliveryNotes = ''
        await this.loadAll()
      } catch (err) {
        this.deliveryError = err.message || 'Failed'
      } finally { this.submitting = false }
    },
  },
}
</script>
