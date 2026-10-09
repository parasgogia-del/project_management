<template>
  <div class="bg-white rounded-xl border border-gray-200 p-5">
    <div class="flex items-center justify-between mb-3">
      <h2 class="text-sm font-semibold text-gray-800">Support Tickets</h2>
      <Button
        v-if="canCreate"
        theme="blue" variant="solid"
        size="sm"
        icon-left="plus"
        :disabled="loading"
        @click="openCreateModal"
      >New Ticket</Button>
    </div>

    <p v-if="error" class="text-xs text-red-500">{{ error }}</p>

    <div v-else-if="loading" class="text-xs text-gray-400 text-center py-4">
      Loading tickets...
    </div>

    <template v-else>
      <!-- Stats strip -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div
          v-for="s in statsStrip"
          :key="s.label"
          class="rounded-lg border border-gray-200 bg-gray-50/60 p-3 text-center"
        >
          <p class="text-lg font-bold text-gray-900">{{ s.count }}</p>
          <p class="text-[10px] text-gray-500 mt-0.5">{{ s.label }}</p>
        </div>
      </div>

      <!-- Tickets table -->
      <div v-if="tickets.length" class="rounded-lg border border-gray-200 overflow-hidden">
        <table class="w-full text-xs">
          <thead class="bg-gray-50 text-gray-500">
            <tr>
              <th class="text-left px-3 py-2 font-medium">#</th>
              <th class="text-left px-3 py-2 font-medium">Subject</th>
              <th class="text-left px-3 py-2 font-medium">Status</th>
              <th class="text-left px-3 py-2 font-medium">Priority</th>
              <th class="text-left px-3 py-2 font-medium">Raised By</th>
              <th class="text-left px-3 py-2 font-medium">Created</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100">
            <tr
              v-for="t in tickets"
              :key="t.name"
              @click="openTicketDetail(t.name)"
              class="cursor-pointer hover:bg-gray-50/60"
            >
              <td class="px-3 py-2 text-gray-600">{{ t.name }}</td>
              <td class="px-3 py-2 text-gray-800">{{ t.subject }}</td>
              <td class="px-3 py-2">
                <Badge :label="t.status" :theme="statusColorMap[t.status] || 'gray'" />
              </td>
              <td class="px-3 py-2">
                <Badge :label="t.priority" :theme="ticketPriorityColors[t.priority] || 'gray'" />
              </td>
              <td class="px-3 py-2 text-gray-600">{{ t.raised_by }}</td>
              <td class="px-3 py-2 text-gray-400">{{ formatDate(t.creation) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-xs text-gray-400 text-center py-4">No support tickets yet</p>
    </template>

    <!-- Create ticket modal -->
    <Dialog v-model="showCreateModal" :options="{ title: 'New Support Ticket', size: 'md' }">
      <template #body-content>
        <div class="space-y-4">
          <input
            v-model="createForm.subject"
            type="text"
            placeholder="Subject *"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
          />
          <textarea
            v-model="createForm.description"
            rows="4"
            placeholder="Describe the issue..."
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
          ></textarea>
          <Autocomplete
            v-model="createForm.priority"
            :options="['Urgent', 'High', 'Medium', 'Low']"
            label="Priority"
            placeholder="Select priority"
          />
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Cancel</Button>
        <Button
          theme="blue" variant="solid"
          :loading="working"
          :loading-text="working ? 'Creating...' : null"
          :disabled="!createForm.subject.trim()"
          @click="createTicket"
        >Create Ticket</Button>
      </template>
    </Dialog>

    <!-- Ticket detail modal -->
    <Dialog
      v-model="showDetailModal"
      :options="{ title: ticket?.name || 'Ticket Details', size: 'lg' }"
    >
      <template #body-content>
        <div v-if="detailLoading" class="text-xs text-gray-400 text-center py-8">
          Loading ticket...
        </div>
        <div v-else-if="ticket">
          <!-- Header -->
          <div class="flex items-start justify-between mb-4 pb-3 border-b border-gray-100">
            <div>
              <h3 class="text-sm font-semibold text-gray-900">{{ ticket.subject }}</h3>
              <p class="text-xs text-gray-500 mt-1">
                Raised by {{ ticket.raised_by }} on {{ formatDate(ticket.creation) }}
              </p>
            </div>
            <div class="flex items-center gap-2">
              <Badge :label="ticket.priority" :theme="ticketPriorityColors[ticket.priority] || 'gray'" />
              <Badge :label="ticket.status" :theme="statusColorMap[ticket.status] || 'gray'" />
            </div>
          </div>

          <!-- Status change (PM/SM only) -->
          <div v-if="canUpdate" class="space-y-2 mb-4">
            <p class="text-[10px] uppercase tracking-wide text-gray-400 mb-1">Update Status</p>
            <Button
              v-for="status in statusOptions"
              :key="status"
              @click="updateStatus(status)"
              :disabled="ticket.status === status || working"
              variant="ghost"
              :active="ticket.status === status"
              class="w-full"
            >
              <span class="flex w-full items-center gap-2">
                <span class="w-2 h-2 rounded-full" :class="statusDotColor(status)" />
                {{ status }}
                <span v-if="ticket.status === status" class="ml-auto text-[10px]">(current)</span>
              </span>
            </Button>
          </div>

          <!-- Description -->
          <div v-if="ticket.description" class="text-xs text-gray-700 mb-4 prose prose-sm max-w-none">
            <div v-html="ticket.description"></div>
          </div>

          <!-- Comments -->
          <p class="text-[10px] uppercase tracking-wide text-gray-400 mb-1.5">Activity</p>
          <div v-if="comments.length" class="space-y-3 mb-4">
            <div v-for="c in comments" :key="c.name" class="flex gap-2 group">
              <div class="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                <span class="text-[10px] font-medium text-gray-500">{{ getInitials(c.author) }}</span>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-medium text-gray-700">{{ c.author || 'System' }}</span>
                  <span class="text-[10px] text-gray-400">{{ formatDate(c.creation) }}</span>
                  <span v-if="c._type !== 'comment'" class="text-[10px] text-gray-300">{{ c._type }}</span>
                </div>
                <div v-if="editingId !== c.name" class="text-xs text-gray-600 mt-0.5" v-html="c.content"></div>
                <div v-else class="flex gap-2 mt-1">
                  <input
                    v-model="editContent"
                    class="flex-1 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:border-blue-400"
                    @keydown.enter="saveEditComment(c)"
                  />
                  <button @click="saveEditComment(c)" class="text-xs text-blue-600 hover:underline">Save</button>
                  <button @click="editingId = null" class="text-xs text-gray-400 hover:underline">Cancel</button>
                </div>
                <div v-if="c._type === 'comment' && c.author === currentUser && editingId !== c.name" class="flex gap-3 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button @click="startEditComment(c)" class="text-[10px] text-gray-400 hover:text-blue-600">Edit</button>
                  <button @click="deleteComment(c)" class="text-[10px] text-gray-400 hover:text-red-500">Delete</button>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="text-xs text-gray-400 text-center py-2 mb-4">No activity yet</p>

          <!-- Add comment (PM/SM/Member/Owner) -->
          <div v-if="canComment" class="flex gap-2">
            <input
              v-model="newComment"
              @keydown.enter="addComment"
              type="text"
              placeholder="Add a comment..."
              class="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
            />
            <button
              @click="addComment"
              :disabled="!newComment.trim() || commentWorking"
              class="px-3 py-2 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Post
            </button>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Close</Button>
        <a
          v-if="ticket"
          :href="helpdeskUrl(ticket.name)"
          target="_blank"
          rel="noopener"
          class="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-full"
        >Open in Helpdesk</a>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { frappeRequest, Button, Badge, Dialog, Autocomplete, toast } from 'frappe-ui'
import { statusColorMap, ticketPriorityColors } from '@/utils/statusColors'
import { useProjectTickets, useTicket, useTicketStats } from '@/data/resources'

export default {
  name: 'HelpdeskSection',
  components: { Button, Badge, Dialog, Autocomplete },
  props: {
    projectId: { type: String, required: true },
    canCreate: { type: Boolean, default: false },
    canUpdate: { type: Boolean, default: false },
    canComment: { type: Boolean, default: false },
  },
  data() {
    return {
      tickets: [],
      stats: {},
      comments: [],
      ticket: null,
      loading: true,
      error: '',
      working: false,
      commentWorking: false,
      detailLoading: false,
      showCreateModal: false,
      showDetailModal: false,
      newComment: '',
      editingId: null,
      editContent: '',
      currentUser: window.currentUser?.user || '',
      createForm: {
        subject: '',
        description: '',
        priority: 'Medium',
      },
      statusOptions: ['Open', 'Replied', 'Resolved', 'Closed'],
      ticketsResource: useProjectTickets(this.projectId),
      ticketResource: useTicket(),
      statsResource: useTicketStats(this.projectId),
      statusColorMap,
      ticketPriorityColors,
    }
  },
  computed: {
    statsStrip() {
      const labels = ['Open', 'Replied', 'Resolved', 'Closed']
      return labels.map((label) => ({
        label,
        count: this.stats[label] || 0,
      }))
    },
  },
  mounted() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loading = true
      this.error = ''
      try {
        const [ticketsRes, statsRes] = await Promise.all([
          this.ticketsResource.fetch(),
          this.statsResource.fetch(),
        ])
        this.tickets = ticketsRes || []
        this.stats = statsRes || {}
      } catch (err) {
        this.error = err.message || 'Failed to load tickets'
      } finally {
        this.loading = false
      }
    },
    openCreateModal() {
      this.showCreateModal = true
    },
    async createTicket() {
      if (!this.createForm.subject.trim()) return
      this.working = true
      try {
        const res = await frappeRequest({
          url: 'project_management.api.helpdesk.create_ticket',
          method: 'POST',
          params: {
            project: this.projectId,
            data: {
              subject: this.createForm.subject.trim(),
              description: this.createForm.description.trim(),
              priority: this.toValue(this.createForm.priority) || 'Medium',
            },
          },
        })
        this.showCreateModal = false
        this.createForm.subject = ''
        this.createForm.description = ''
        this.createForm.priority = 'Medium'
        toast({ title: 'Success', text: `Ticket ${res.name} created`, icon: 'check-circle', iconClasses: 'text-green-600' })
        await this.loadAll()
        this.$emit('ticket-created')
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to create ticket', icon: 'alert-circle', iconClasses: 'text-red-600' })
      } finally {
        this.working = false
      }
    },
    async openTicketDetail(name) {
      this.detailLoading = true
      this.showDetailModal = true
      this.ticket = null
      this.comments = []
      try {
        const res = await frappeRequest({
          url: 'project_management.api.helpdesk.get_ticket',
          method: 'POST',
          params: { name },
        })
        this.ticket = res.ticket
        this.comments = res.comments || []
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to load ticket', icon: 'alert-circle', iconClasses: 'text-red-600' })
        this.showDetailModal = false
      } finally {
        this.detailLoading = false
      }
    },
    async updateStatus(status) {
      if (!this.ticket) return
      this.working = true
      try {
        const res = await frappeRequest({
          url: 'project_management.api.helpdesk.update_ticket',
          method: 'POST',
          params: { name: this.ticket.name, data: { status } },
        })
        this.ticket.status = status
        toast({ title: 'Success', text: `Status updated`, icon: 'check-circle', iconClasses: 'text-green-600' })
        await this.loadAll()
        this.$emit('ticket-updated')
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to update status', icon: 'alert-circle', iconClasses: 'text-red-600' })
      } finally {
        this.working = false
      }
    },
    async addComment() {
      if (!this.newComment.trim()) return
      this.commentWorking = true
      try {
        await frappeRequest({
          url: 'project_management.api.helpdesk.add_ticket_comment',
          method: 'POST',
          params: { name: this.ticket.name, content: this.newComment.trim() },
        })
        this.newComment = ''
        const res = await frappeRequest({
          url: 'project_management.api.helpdesk.get_ticket',
          method: 'POST',
          params: { name: this.ticket.name },
        })
        this.ticket = res.ticket
        this.comments = res.comments || []
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to add comment', icon: 'alert-circle', iconClasses: 'text-red-600' })
      } finally {
        this.commentWorking = false
      }
    },
    startEditComment(comment) {
      this.editingId = comment.name
      this.editContent = comment.content
    },
    async saveEditComment(comment) {
      if (!this.editContent.trim()) return
      try {
        await frappeRequest({
          url: 'project_management.api.helpdesk.edit_ticket_comment',
          method: 'POST',
          params: { name: comment.name, content: this.editContent.trim() },
        })
        this.editingId = null
        this.editContent = ''
        const res = await frappeRequest({
          url: 'project_management.api.helpdesk.get_ticket',
          method: 'POST',
          params: { name: this.ticket.name },
        })
        this.ticket = res.ticket
        this.comments = res.comments || []
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to update comment', icon: 'alert-circle', iconClasses: 'text-red-600' })
      }
    },
    async deleteComment(comment) {
      try {
        await frappeRequest({
          url: 'project_management.api.helpdesk.delete_ticket_comment',
          method: 'POST',
          params: { name: comment.name },
        })
        const res = await frappeRequest({
          url: 'project_management.api.helpdesk.get_ticket',
          method: 'POST',
          params: { name: this.ticket.name },
        })
        this.ticket = res.ticket
        this.comments = res.comments || []
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to delete comment', icon: 'alert-circle', iconClasses: 'text-red-600' })
      }
    },
    getInitials(email) {
      if (!email) return '?'
      return email.split('@')[0].slice(0, 2).toUpperCase()
    },
    statusDotColor(status) {
      const colors = {
        Open: 'bg-green-500',
        Replied: 'bg-blue-500',
        Resolved: 'bg-blue-400',
        Closed: 'bg-gray-400'
      }
      return colors[status] || 'bg-gray-400'
    },
    toValue(value) {
      if (value && typeof value === 'object' && 'value' in value) {
        return value.value
      }
      return value
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    helpdeskUrl(name) {
      // Backend origin in dev (Vite :8080 -> Frappe :8000), same-origin in prod.
      // Uses Helpdesk's canonical "/tickets/" link (the ticket's real URL). The
      // route guard shows the agent view for agents and auto-redirects Clients
      // to the customer view (/my-tickets), so one URL works for all roles.
      const currentPort = Number(window.location.port) || (window.location.protocol === 'https:' ? 443 : 80)
      // Vite dev server ports start at 8080 (webserver 8000); their backend is -80.
      if (currentPort >= 8080) {
        return `${window.location.protocol}//${window.location.hostname}:${currentPort - 80}/helpdesk/tickets/${name}`
      }
      return `/helpdesk/tickets/${name}`
    },
  },
}
</script>