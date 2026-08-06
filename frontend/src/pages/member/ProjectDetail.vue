<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button variant="ghost" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ project?.project_name || 'Loading...' }}</h1>
          <Badge v-if="project" :label="project.status" :theme="statusColorMap[project.status] || 'gray'" />
        </div>
        <p v-if="project?.client" class="text-sm text-gray-500 mt-0.5">Client: {{ project.client }}</p>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

    <template v-else-if="project">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <!-- Progress -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Progress</h2>
            <ProgressBar :value="project.progress || 0" />
            <div class="grid grid-cols-4 gap-4 mt-4">
              <div class="text-center p-3 bg-gray-50 rounded-lg">
                <p class="text-lg font-bold text-gray-900">{{ tasks.length }}</p>
                <p class="text-[10px] text-gray-500">Total Tasks</p>
              </div>
              <div class="text-center p-3 bg-green-50 rounded-lg">
                <p class="text-lg font-bold text-green-700">{{ completedTasks }}</p>
                <p class="text-[10px] text-gray-500">Completed</p>
              </div>
              <div class="text-center p-3 bg-blue-50 rounded-lg">
                <p class="text-lg font-bold text-blue-700">{{ workingTasks }}</p>
                <p class="text-[10px] text-gray-500">In Progress</p>
              </div>
              <div class="text-center p-3 bg-red-50 rounded-lg">
                <p class="text-lg font-bold text-red-600">{{ blockedTasks }}</p>
                <p class="text-[10px] text-gray-500">Blocked</p>
              </div>
            </div>
          </div>

          <!-- Deliverables -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-4">Deliverables</h2>
            <div v-if="deliverables.length === 0" class="text-xs text-gray-400 text-center py-4">
              No deliverables yet
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="d in deliverables"
                :key="d.name"
                @click="$router.push(`/member/deliverable/${d.name}`)"
                class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div class="min-w-0 flex-1 pr-4">
                  <p class="text-sm font-medium text-gray-800 truncate">{{ d.title }}</p>
                  <p class="text-xs text-gray-400">Due: {{ d.due_date || 'Not set' }}</p>
                </div>
                <div class="flex items-center gap-3 flex-shrink-0 w-40">
                  <ProgressBar :value="d.progress || 0" />
                  <Badge :label="d.status" :theme="statusColorMap[d.status] || 'gray'" />
                </div>
              </div>
            </div>
          </div>

          <!-- Tasks -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-4">Tasks</h2>
            <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">
              No tasks yet
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="task in tasks"
                :key="task.name"
                @click="$router.push(`/member/task/${task.name}`)"
                class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
                  <p class="text-xs text-gray-400">{{ task.assigned_to || 'Unassigned' }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <Badge :label="task.priority" :theme="statusColorMap[task.priority] || 'gray'" />
                  <Badge :label="task.status" :theme="statusColorMap[task.status] || 'gray'" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right column -->
        <div class="space-y-6">
          <!-- Description -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-2">Description</h2>
            <p class="text-sm text-gray-600">{{ project.description || 'No description' }}</p>
            <div class="mt-4 space-y-2 text-xs text-gray-500">
              <div v-if="project.start_date" class="flex justify-between">
                <span>Start Date</span>
                <span class="text-gray-700">{{ project.start_date }}</span>
              </div>
              <div v-if="project.end_date" class="flex justify-between">
                <span>End Date</span>
                <span class="text-gray-700">{{ project.end_date }}</span>
              </div>
              <div v-if="project.project_manager" class="flex justify-between">
                <span>Manager</span>
                <span class="text-gray-700">{{ project.project_manager }}</span>
              </div>
            </div>
          </div>

          <!-- Members -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Members</h2>
            <div v-if="!project.project_members?.length" class="text-xs text-gray-400 text-center py-2">
              No members
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="m in project.project_members"
                :key="m.name"
                class="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50"
              >
                <Avatar :label="m.user" size="sm" />
                <div class="min-w-0">
                  <p class="text-xs font-medium text-gray-800 truncate">{{ m.user }}</p>
                  <p class="text-[10px] text-gray-400">{{ m.project_role }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Vendors -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <h2 class="text-sm font-semibold text-gray-800 mb-3">Vendors</h2>
            <div v-if="!project.vendors?.length" class="text-xs text-gray-400 text-center py-2">
              No vendors
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="v in project.vendors"
                :key="v.name"
                class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50"
              >
                <div>
                  <p class="text-xs font-medium text-gray-800">{{ v.vendor }}</p>
                  <p class="text-[10px] text-gray-400">{{ v.company }}</p>
                </div>
                <Badge :label="v.status" :theme="statusColorMap[v.status] || 'gray'" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, Avatar, LoadingIndicator } from 'frappe-ui'
import { useProject, useTasks, useDeliverablesWithDetails } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'

export default {
  name: 'MemberProjectDetail',
  components: { FeatherIcon, Button, Badge, Avatar, LoadingIndicator, ProgressBar },
  data() {
    return {
      project: null,
      tasks: [],
      deliverables: [],
      loading: true,
    }
  },
  computed: {
    projectId() {
      return this.$route.params.id
    },
    completedTasks() {
      return this.tasks.filter(t => t.status === 'Completed').length
    },
    workingTasks() {
      return this.tasks.filter(t => t.status === 'Working').length
    },
    blockedTasks() {
      return this.tasks.filter(t => t.status === 'Blocked').length
    },
  },
  mounted() {
    this.loadAll()
  },
  methods: {
    async loadAll() {
      this.loading = true
      try {
        const isMember = await this.isLinkedMember()
        if (!isMember) {
          this.$router.replace('/member/dashboard')
          return
        }
        const [projectRes, tasksRes, deliverablesRes] = await Promise.all([
          useProject(this.projectId).fetch(),
          useTasks({ project: this.projectId }).fetch(),
          useDeliverablesWithDetails(this.projectId).fetch(),
        ])
        this.project = projectRes
        this.tasks = tasksRes || []
        this.deliverables = deliverablesRes || []
      } catch (err) {
        console.error('Failed to load project', err)
      } finally {
        this.loading = false
      }
    },
    async isLinkedMember() {
      try {
        const projects = await frappeRequest({ url: 'project_management.api.client.get_member_projects', method: 'POST' })
        return (projects || []).some(p => p.name === this.projectId)
      } catch {
        return false
      }
    },
  },
}
</script>
