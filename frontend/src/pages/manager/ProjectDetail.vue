<template>
  <div class="space-y-6">
    <div class="flex items-center gap-3">
      <Button appearance="minimal" icon="arrow-left" @click="$router.back()" />
      <div class="flex-1">
        <div class="flex items-center gap-3">
          <h1 class="text-xl font-bold text-gray-900">{{ project?.project_name || 'Loading...' }}</h1>
          <Badge v-if="project" :label="project.status" :color-map="statusColorMap" />
        </div>
        <p v-if="project?.client" class="text-sm text-gray-500 mt-0.5">Client: {{ project.client }}</p>
      </div>
      <div class="flex gap-2">
        <Button v-if="project" appearance="secondary" :route="`/project/${projectId}/gantt`">Gantt Chart</Button>
        <Button v-if="project" appearance="secondary" :route="`/project/${projectId}/reports`">Reports</Button>
        <Button v-if="project" appearance="secondary" :route="`/project/${projectId}/edit`">Edit</Button>
        <Button v-if="project" appearance="danger" @click="showDeleteConfirm = true">Delete</Button>
      </div>
    </div>

    <LoadingIndicator v-if="loading" class="mx-auto my-16 h-8 w-8 text-gray-400" />

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
                <Badge :label="d.status" :color-map="statusColorMap" />
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
                  <Badge :label="task.priority" :color-map="statusColorMap" />
                  <Badge :label="task.status" :color-map="statusColorMap" />
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
                <Badge :label="v.status" :color-map="statusColorMap" />
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

    <Dialog v-model="showDeleteConfirm" :options="{ title: 'Delete Project', size: 'sm' }">
      <template #body-content>
        <p class="text-sm text-gray-500">
          Are you sure you want to delete <strong>{{ project?.project_name }}</strong>? This action cannot be undone. All tasks, deliverables, and files associated with this project will also be removed.
        </p>
      </template>
      <template #actions="{ close }">
        <Button appearance="secondary" @click="close">Cancel</Button>
        <Button
          appearance="danger"
          :loading="deleting"
          :loading-text="deleting ? 'Deleting...' : null"
          @click="deleteProject"
        >Delete Project</Button>
      </template>
    </Dialog>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Button, Badge, Avatar, LoadingIndicator, Dialog, toast } from 'frappe-ui'
import { useProject, useTasks, useDeliverablesWithDetails } from '@/data/resources'
import { statusColorMap } from '@/utils/statusColors'
import ProgressBar from '@/components/ProgressBar.vue'
import FileUpload from '@/components/FileUpload.vue'
import CommentSection from '@/components/CommentSection.vue'

export default {
  name: 'ProjectDetail',
  components: { FeatherIcon, Button, Badge, Avatar, LoadingIndicator, Dialog, ProgressBar, FileUpload, CommentSection },
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
    async deleteProject() {
      this.deleting = true
      try {
        await frappeRequest({ url: 'project_management.api.client.delete_project', method: 'POST', params: { name: this.projectId } })
        toast({ title: 'Success', text: 'Project deleted successfully', icon: 'check-circle', iconClasses: 'text-green-600' })
        this.$router.push('/projects')
      } catch (err) {
        toast({ title: 'Error', text: err.message || 'Failed to delete project', icon: 'alert-circle', iconClasses: 'text-red-600' })
      } finally {
        this.deleting = false
        this.showDeleteConfirm = false
      }
    },
  },
}
</script>
