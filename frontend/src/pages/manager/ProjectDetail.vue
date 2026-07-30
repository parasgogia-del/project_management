<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ project?.project_name || 'Loading...' }}</h1>
          <StatusBadge v-if="project" :status="project.status" />
        </div>
        <p v-if="project?.client" class="text-sm text-gray-500 mt-0.5">Client: {{ project.client }}</p>
      </div>
      <div class="flex gap-2">
        <router-link
          v-if="project"
          :to="`/project/${projectId}/gantt`"
          class="px-3 py-2 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Gantt Chart
        </router-link>
        <router-link
          v-if="project"
          :to="`/project/${projectId}/reports`"
          class="px-3 py-2 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Reports
        </router-link>
        <router-link
          v-if="project"
          :to="`/project/${projectId}/edit`"
          class="px-3 py-2 text-xs font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors"
        >
          Edit
        </router-link>
        <button
          v-if="project"
          @click="showDeleteConfirm = true"
          class="px-3 py-2 text-xs font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
        >
          Delete
        </button>
      </div>
    </div>

    <SkeletonLoader v-if="loading" :lines="5" />

    <template v-else-if="project">
      <!-- Progress + description -->
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
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-sm font-semibold text-gray-800">Deliverables</h2>
              <router-link
                :to="`/project/${projectId}/deliverables`"
                class="text-xs text-blue-600 hover:underline"
              >View all</router-link>
            </div>
            <div v-if="deliverables.length === 0" class="text-xs text-gray-400 text-center py-4">
              No deliverables yet
            </div>
            <div v-else class="space-y-2">
              <div
                v-for="d in deliverables.slice(0, 5)"
                :key="d.name"
                @click="$router.push(`/deliverable/${d.name}`)"
                class="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm font-medium text-gray-800 truncate">{{ d.title }}</p>
                  <p class="text-xs text-gray-400">Due: {{ d.due_date || 'Not set' }}</p>
                </div>
                <StatusBadge :status="d.status" />
              </div>
            </div>
          </div>

          <!-- Recent Tasks -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-sm font-semibold text-gray-800">Tasks</h2>
              <router-link
                :to="`/project/${projectId}/tasks`"
                class="text-xs text-blue-600 hover:underline"
              >View all</router-link>
            </div>
            <div v-if="tasks.length === 0" class="text-xs text-gray-400 text-center py-4">
              No tasks yet
            </div>
            <div v-else class="divide-y divide-gray-50">
              <div
                v-for="task in tasks.slice(0, 5)"
                :key="task.name"
                @click="$router.push(`/task/${task.name}`)"
                class="flex items-center justify-between py-2.5 cursor-pointer hover:bg-gray-50 -mx-2 px-2 rounded transition-colors"
              >
                <div class="min-w-0 flex-1">
                  <p class="text-sm text-gray-800 truncate">{{ task.title }}</p>
                </div>
                <div class="flex items-center gap-2">
                  <StatusBadge :status="task.priority" />
                  <StatusBadge :status="task.status" />
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
                <div class="w-7 h-7 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <span class="text-[10px] font-medium text-blue-700">{{ getInitials(m.user) }}</span>
                </div>
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
                <StatusBadge :status="v.status" />
              </div>
            </div>
          </div>

          <!-- Attachments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <FileUpload doctype="Project Info" :docname="projectId" />
          </div>

          <!-- Comments -->
          <div class="bg-white rounded-xl border border-gray-200 p-5">
            <CommentSection doctype="Project Info" :docname="projectId" />
          </div>
        </div>
      </div>
    </template>

    <!-- Delete Confirmation Modal -->
    <div
      v-if="showDeleteConfirm"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/30"
      @click.self="showDeleteConfirm = false"
    >
      <div class="bg-white rounded-xl shadow-xl w-full max-w-sm mx-4 p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-2">Delete Project</h2>
        <p class="text-sm text-gray-500 mb-6">
          Are you sure you want to delete <strong>{{ project?.project_name }}</strong>? This action cannot be undone. All tasks, deliverables, and files associated with this project will also be removed.
        </p>
        <div class="flex justify-end gap-3">
          <button
            @click="showDeleteConfirm = false"
            class="px-4 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            @click="deleteProject"
            :disabled="deleting"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50"
          >
            {{ deleting ? 'Deleting...' : 'Delete Project' }}
          </button>
        </div>
      </div>
    </div>

    <Toast ref="toast" />
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'
import StatusBadge from '@/components/StatusBadge.vue'
import ProgressBar from '@/components/ProgressBar.vue'
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'
import Toast from '@/components/Toast.vue'

export default {
  name: 'ProjectDetail',
  components: { FeatherIcon, StatusBadge, ProgressBar, SkeletonLoader, FileUpload, CommentSection, Toast },
  data() {
    return {
      project: null,
      tasks: [],
      deliverables: [],
      loading: true,
      showDeleteConfirm: false,
      deleting: false,
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
        const [projectRes, tasksRes, deliverablesRes] = await Promise.all([
          call('project_management.api.client.get_project', { name: this.projectId }),
          call('project_management.api.client.get_tasks', { project: this.projectId }),
          call('project_management.api.client.get_deliverables_with_details', { project: this.projectId }),
        ])
        this.project = projectRes.message
        this.tasks = tasksRes.message || []
        this.deliverables = deliverablesRes.message || []
      } catch (err) {
        console.error('Failed to load project', err)
      } finally {
        this.loading = false
      }
    },
    getInitials(user) {
      if (!user) return '?'
      return user.split('@')[0].slice(0, 2).toUpperCase()
    },
    async deleteProject() {
      this.deleting = true
      try {
        await call('project_management.api.client.delete_project', { name: this.projectId })
        this.$refs.toast.show('Project deleted successfully', 'success')
        this.$router.push('/projects')
      } catch (err) {
        this.$refs.toast.show(err.message || 'Failed to delete project', 'error')
      } finally {
        this.deleting = false
        this.showDeleteConfirm = false
      }
    },
  },
}
</script>
