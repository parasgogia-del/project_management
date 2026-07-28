<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div>
        <h1 class="text-xl font-bold text-gray-900">Deliverables</h1>
        <p class="text-sm text-gray-500 mt-0.5">Project: {{ projectId }}</p>
      </div>
    </div>

    <SkeletonLoader v-if="loading" :lines="4" />

    <div v-else-if="deliverables.length === 0" class="bg-white rounded-xl border border-gray-200">
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
            v-for="d in deliverables"
            :key="d.name"
            @click="$router.push(`/deliverable/${d.name}`)"
            class="hover:bg-gray-50 cursor-pointer transition-colors"
          >
            <td class="px-5 py-3">
              <p class="text-sm font-medium text-gray-800">{{ d.title }}</p>
              <p class="text-xs text-gray-400">{{ d.description?.slice(0, 60) || 'No description' }}</p>
            </td>
            <td class="px-5 py-3"><StatusBadge :status="d.status" /></td>
            <td class="px-5 py-3 w-40">
              <ProgressBar :value="d.progress || 0" />
              <p class="text-[10px] text-gray-400 mt-0.5">{{ d.completed_tasks || 0 }}/{{ d.total_tasks || 0 }} tasks</p>
            </td>
            <td class="px-5 py-3 text-xs text-gray-600">{{ d.due_date || '-' }}</td>
            <td class="px-5 py-3">
              <div class="flex -space-x-1">
                <div
                  v-for="(m, i) in (d.members || []).slice(0, 3)"
                  :key="i"
                  class="w-6 h-6 rounded-full bg-blue-100 border-2 border-white flex items-center justify-center"
                  :title="m"
                >
                  <span class="text-[8px] font-medium text-blue-700">{{ m?.split('@')[0]?.slice(0, 2)?.toUpperCase() }}</span>
                </div>
                <div
                  v-if="(d.members || []).length > 3"
                  class="w-6 h-6 rounded-full bg-gray-100 border-2 border-white flex items-center justify-center"
                >
                  <span class="text-[8px] font-medium text-gray-500">+{{ d.members.length - 3 }}</span>
                </div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import EmptyState from '@/components/EmptyState.vue'

export default {
  name: 'DeliverableList',
  components: { FeatherIcon, StatusBadge, ProgressBar, SkeletonLoader, EmptyState },
  data() {
    return {
      deliverables: [],
      loading: true,
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
  },
  mounted() {
    this.loadDeliverables()
  },
  methods: {
    async loadDeliverables() {
      this.loading = true
      try {
        const result = await call('project_management.api.client.get_deliverables_with_details', {
          project: this.projectId,
        })
        this.deliverables = result.message || []
      } catch {
        this.deliverables = []
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
