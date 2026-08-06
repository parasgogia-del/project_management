<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ project?.project_name || 'Loading...' }}</h1>
          <Badge v-if="project" :label="project.status" :theme="statusColorMap[project.status] || 'gray'" />
        </div>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <template v-else-if="project">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <!-- Overview -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Project Overview</h2>
            <p class="text-sm text-gray-600">{{ project.description || 'No description' }}</p>
            <div class="grid grid-cols-2 gap-4 mt-4 text-sm">
              <div>
                <p class="text-xs text-gray-500">Start Date</p>
                <p class="text-gray-700 mt-0.5">{{ project.start_date || 'Not set' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500">End Date</p>
                <p class="text-gray-700 mt-0.5">{{ project.end_date || 'Not set' }}</p>
              </div>
            </div>
          </div>

          <!-- Deliverables -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Deliverables</h2>
            <div v-if="deliverables.length === 0" class="text-xs text-gray-400 text-center py-4">
              No deliverables yet
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="d in deliverables"
                :key="d.name"
                @click="$router.push(`/vendor/deliverable/${d.name}`)"
                class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
              >
                <div class="min-w-0 flex-1 pr-4">
                  <p class="text-sm font-medium text-gray-800 truncate">{{ d.title }}</p>
                  <p class="text-xs text-gray-400">Due: {{ d.due_date || 'Not set' }}</p>
                </div>
                <Badge :label="d.status" :theme="statusColorMap[d.status] || 'gray'" />
              </div>
            </div>
          </div>

          <!-- Tasks -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Your Tasks</h2>
            <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">
              No tasks assigned to you in this project
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="t in tasks"
                :key="t.name"
                @click="$router.push(`/vendor/task/${t.name}`)"
                class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm text-gray-800 truncate">{{ t.title }}</p>
                  <p class="text-xs text-gray-400">{{ t.deliverable || 'No deliverable' }} | Due: {{ t.due_date || 'Not set' }}</p>
                </div>
                <Badge :label="t.status" :theme="statusColorMap[t.status] || 'gray'" />
              </div>
            </div>
          </div>
        </div>

        <!-- Right column -->
        <div class="space-y-6">
          <!-- Progress -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-2">Progress</h2>
            <ProgressBar :value="project.progress || 0" />
          </div>

          <!-- Summary -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Summary</h2>
            <div class="space-y-2 text-xs text-gray-500">
              <div class="flex justify-between">
                <span>Deliverables</span>
                <span class="text-gray-700">{{ deliverables.length }}</span>
              </div>
              <div class="flex justify-between">
                <span>Your Tasks</span>
                <span class="text-gray-700">{{ tasks.length }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, LoadingIndicator } from 'frappe-ui'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'

export default {
  name: 'VendorProjectView',
  components: { FeatherIcon, Button, Badge, LoadingIndicator, ProgressBar },
  data() {
    return {
      project: null,
      deliverables: [],
      tasks: [],
      loading: true,
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
  },
  mounted() {
    this.loadProject()
  },
  methods: {
    async loadProject() {
      this.loading = true
      try {
        const res = await frappeRequest({
          url: 'project_management.api.vendor.get_vendor_project',
          method: 'POST',
          params: { name: this.projectId },
        })
        this.project = res
        this.deliverables = res?.deliverables || []
        this.tasks = res?.tasks || []
      } catch (err) {
        console.error('Failed to load vendor project', err)
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
