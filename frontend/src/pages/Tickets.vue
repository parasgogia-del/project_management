<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <div class="flex-1">
        <h1 class="text-xl font-bold text-gray-900">Support Tickets</h1>
        <p class="text-sm text-gray-500 mt-0.5">Issues raised across my projects</p>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <Input
        type="select"
        v-model="statusFilter"
        :options="statusFilterOptions"
        class="w-44"
      />
      <Input
        type="select"
        v-model="priorityFilter"
        :options="priorityFilterOptions"
        class="w-44"
      />
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <div v-else-if="filteredTickets.length === 0" class="bg-white rounded-xl border border-gray-200">
      <EmptyState icon="life-buoy" title="No tickets found" description="No support tickets match your filters" />
    </div>

    <div v-else class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <table class="w-full">
        <thead>
          <tr class="border-b border-gray-100">
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Ticket</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Project</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Status</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Priority</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Raised By</th>
            <th class="text-left px-5 py-3 text-xs font-medium text-gray-500">Created</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr
            v-for="t in filteredTickets"
            :key="t.name"
            @click="openTicket(t.name)"
            class="hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <td class="px-5 py-3">
              <p class="text-sm font-medium text-gray-800">
                <span class="text-xs text-gray-400 mr-1">#{{ t.name }}</span>{{ t.subject }}
              </p>
            </td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ t.custom_project || '-' }}</td>
            <td class="px-5 py-3"><Badge :label="t.status" :theme="statusColorMap[t.status] || 'gray'" /></td>
            <td class="px-5 py-3"><Badge :label="t.priority" :theme="ticketPriorityColors[t.priority] || 'gray'" /></td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ t.raised_by || '-' }}</td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ formatDate(t.creation) }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <Dialog v-model="showDetailModal" :options="{ title: 'Ticket Details', size: 'lg' }">
      <template #body-content>
        <div v-if="detailLoading" class="py-10 text-center">
          <LoadingIndicator class="mx-auto h-6 w-6 text-gray-400" />
        </div>
        <div v-else-if="ticket">
          <div class="flex items-start justify-between gap-3 mb-4">
            <div class="min-w-0">
              <h3 class="text-sm font-semibold text-gray-900">
                <span class="text-gray-400">#{{ ticket.name }}</span> {{ ticket.subject }}
              </h3>
              <div class="flex items-center gap-2 mt-2">
                <Badge :label="ticket.status" :theme="statusColorMap[ticket.status] || 'gray'" />
                <Badge :label="ticket.priority" :theme="ticketPriorityColors[ticket.priority] || 'gray'" />
              </div>
            </div>
            <a
              :href="helpdeskUrl(ticket.name)"
              target="_blank"
              rel="noopener"
              class="inline-flex items-center px-3 py-1.5 text-xs font-medium text-blue-600 hover:bg-blue-50 rounded-lg whitespace-nowrap"
            >Open in Helpdesk</a>
          </div>

          <div v-if="ticket.description" v-html="ticket.description" class="text-xs text-gray-600 border border-gray-100 rounded-lg p-3 mb-4"></div>

          <div class="mb-2">
            <p class="text-xs font-medium text-gray-500 uppercase tracking-wide mb-2">Activity</p>
            <div v-if="comments.length" class="space-y-3">
              <div v-for="c in comments" :key="c.name" class="flex gap-2">
                <div class="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <span class="text-[10px] font-medium text-gray-500">{{ getInitials(c.author) }}</span>
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="text-xs font-medium text-gray-700">{{ c.author || 'System' }}</span>
                    <span class="text-[10px] text-gray-400">{{ formatDate(c.creation) }}</span>
                  </div>
                  <div class="text-xs text-gray-600 mt-0.5" v-html="c.content"></div>
                </div>
              </div>
            </div>
            <p v-else class="text-xs text-gray-400 text-center py-2">No activity yet</p>
          </div>

          <div class="flex gap-2 pt-3 border-t border-gray-100">
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
            >Post</button>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <Button variant="outline" @click="close">Close</Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { frappeRequest, Button, Badge, Dialog, Input, LoadingIndicator, toast } from 'frappe-ui'
import { useMyTickets } from '@/data/resources'
import { statusColorMap, ticketPriorityColors } from '@/utils/statusColors'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'Tickets',
  components: { Button, Badge, Dialog, Input, LoadingIndicator, EmptyState },
  data() {
    return {
      tickets: [],
      loading: true,
      statusFilter: '',
      priorityFilter: '',
      showDetailModal: false,
      detailLoading: false,
      ticket: null,
      comments: [],
      newComment: '',
      commentWorking: false,
      ticketsResource: useMyTickets(),
      statusColorMap,
      ticketPriorityColors,
    }
  },
  computed: {
    statusFilterOptions() {
      return [
        { label: 'All Status', value: '' },
        { label: 'Open', value: 'Open' },
        { label: 'Replied', value: 'Replied' },
        { label: 'Resolved', value: 'Resolved' },
        { label: 'Closed', value: 'Closed' },
      ]
    },
    priorityFilterOptions() {
      return [
        { label: 'All Priority', value: '' },
        { label: 'Urgent', value: 'Urgent' },
        { label: 'High', value: 'High' },
        { label: 'Medium', value: 'Medium' },
        { label: 'Low', value: 'Low' },
      ]
    },
    filteredTickets() {
      return this.tickets.filter(t => {
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
        this.tickets = await this.ticketsResource.fetch() || []
      } catch (err) {
        this.tickets = []
        toast({ title: 'Error', text: err.message || 'Failed to load tickets', icon: 'alert-circle', iconClasses: 'text-red-600' })
      } finally {
        this.loading = false
      }
    },
    async openTicket(name) {
      this.detailLoading = true
      this.showDetailModal = true
      this.ticket = null
      this.comments = []
      this.newComment = ''
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
    getInitials(email) {
      if (!email) return '?'
      return email.split('@')[0].slice(0, 2).toUpperCase()
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const d = new Date(dateStr)
      return d.toLocaleDateString() + ' ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    },
    helpdeskUrl(name) {
      const currentPort = Number(window.location.port) || (window.location.protocol === 'https:' ? 443 : 80)
      if (currentPort >= 8080) {
        return `${window.location.protocol}//${window.location.hostname}:${currentPort - 80}/helpdesk/tickets/${name}`
      }
      return `/helpdesk/tickets/${name}`
    },
  },
}
</script>