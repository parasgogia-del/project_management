<template>
  <div class="max-w-3xl mx-auto space-y-6">
    <div class="flex items-center gap-3">
      <button @click="$router.back()" class="p-2 rounded-lg hover:bg-gray-100 text-gray-500">
        <feather-icon name="arrow-left" class="w-5 h-5" />
      </button>
      <div>
        <h1 class="text-xl font-bold text-gray-900">{{ isEdit ? 'Edit Project' : 'Create Project' }}</h1>
        <p class="text-sm text-gray-500 mt-0.5">{{ isEdit ? 'Update project details' : 'Set up a new project' }}</p>
      </div>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <div class="space-y-5">
        <!-- Project Name -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
          <input
            v-model="form.project_name"
            type="text"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
            placeholder="Enter project name"
          />
        </div>

        <!-- Client & Manager row -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Client *</label>
            <input
              v-model="form.client"
              type="text"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              placeholder="Client name"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Project Manager</label>
            <input
              v-model="form.project_manager"
              type="text"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              placeholder="Manager email"
            />
          </div>
        </div>

        <!-- Status -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="form.status"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white"
          >
            <option value="Planning">Planning</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="On Hold">On Hold</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>

        <!-- Dates row -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
            <input
              v-model="form.start_date"
              type="date"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
            <input
              v-model="form.end_date"
              type="date"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
            />
          </div>
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 resize-none"
            placeholder="Project description..."
          />
        </div>
      </div>
    </div>

    <!-- Members section -->
    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-gray-800">Project Members</h2>
        <button
          @click="addMember"
          class="text-xs font-medium text-blue-600 hover:text-blue-700"
        >+ Add Member</button>
      </div>
      <div v-if="form.project_members.length === 0" class="text-xs text-gray-400 text-center py-4">
        No members added
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="(member, idx) in form.project_members"
          :key="idx"
          class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
        >
          <input
            v-model="member.user"
            type="text"
            placeholder="User email"
            class="flex-1 px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white"
          />
          <select
            v-model="member.project_role"
            class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white"
          >
            <option value="Project Manager">Project Manager</option>
            <option value="Developer">Developer</option>
            <option value="Designer">Designer</option>
            <option value="QA">QA</option>
            <option value="Business Analyst">Business Analyst</option>
            <option value="UI/UX Designer">UI/UX Designer</option>
            <option value="Client Reviewer">Client Reviewer</option>
          </select>
          <label class="flex items-center gap-1 text-xs text-gray-500">
            <input type="checkbox" v-model="member.is_active" class="rounded" /> Active
          </label>
          <button
            @click="removeMember(idx)"
            class="p-1 text-gray-400 hover:text-red-500 rounded"
          >
            <feather-icon name="x" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Vendors section -->
    <div class="bg-white rounded-xl border border-gray-200 p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-gray-800">Vendors</h2>
        <button
          @click="addVendor"
          class="text-xs font-medium text-blue-600 hover:text-blue-700"
        >+ Add Vendor</button>
      </div>
      <div v-if="form.vendors.length === 0" class="text-xs text-gray-400 text-center py-4">
        No vendors added
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="(vendor, idx) in form.vendors"
          :key="idx"
          class="flex items-center gap-3 p-3 bg-gray-50 rounded-lg"
        >
          <input
            v-model="vendor.vendor"
            type="text"
            placeholder="Vendor name"
            class="flex-1 px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white"
          />
          <select
            v-model="vendor.status"
            class="px-3 py-1.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 bg-white"
          >
            <option value="Active">Active</option>
            <option value="Inactive">Inactive</option>
            <option value="Suspended">Suspended</option>
          </select>
          <button
            @click="removeVendor(idx)"
            class="p-1 text-gray-400 hover:text-red-500 rounded"
          >
            <feather-icon name="x" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center justify-end gap-3">
      <button
        @click="$router.back()"
        class="px-4 py-2 text-sm font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
      >
        Cancel
      </button>
      <button
        @click="saveProject"
        :disabled="saving || !form.project_name || !form.client"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
      >
        {{ saving ? 'Saving...' : (isEdit ? 'Update Project' : 'Create Project') }}
      </button>
    </div>

    <p v-if="error" class="text-xs text-red-500 text-center">{{ error }}</p>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'

export default {
  name: 'ProjectForm',
  components: { FeatherIcon },
  data() {
    return {
      isEdit: false,
      saving: false,
      error: '',
      form: {
        project_name: '',
        client: '',
        project_manager: '',
        status: 'Planning',
        start_date: '',
        end_date: '',
        description: '',
        project_members: [],
        vendors: [],
      },
    }
  },
  mounted() {
    if (this.$route.params.id) {
      this.isEdit = true
      this.loadProject(this.$route.params.id)
    }
  },
  methods: {
    async loadProject(name) {
      try {
        const result = await call('project_management.api.client.get_project', { name })
        const project = result.message
        if (project) {
          this.form = {
            project_name: project.project_name,
            client: project.client,
            project_manager: project.project_manager || '',
            status: project.status || 'Planning',
            start_date: project.start_date || '',
            end_date: project.end_date || '',
            description: project.description || '',
            project_members: (project.project_members || []).map(m => ({
              name: m.name,
              user: m.user,
              project_role: m.project_role,
              is_active: m.is_active,
              assigned_on: m.assigned_on,
              notes: m.notes || '',
            })),
            vendors: (project.vendors || []).map(v => ({
              name: v.name,
              vendor: v.vendor,
              status: v.status || 'Active',
              contract_start: v.contract_start,
              contract_end: v.contract_end,
              notes: v.notes || '',
            })),
          }
        }
      } catch (err) {
        this.error = 'Failed to load project'
      }
    },
    addMember() {
      this.form.project_members.push({
        user: '',
        project_role: 'Developer',
        is_active: 1,
        assigned_on: new Date().toISOString().split('T')[0],
        notes: '',
      })
    },
    removeMember(idx) {
      this.form.project_members.splice(idx, 1)
    },
    addVendor() {
      this.form.vendors.push({
        vendor: '',
        status: 'Active',
        notes: '',
      })
    },
    removeVendor(idx) {
      this.form.vendors.splice(idx, 1)
    },
    async saveProject() {
      this.saving = true
      this.error = ''
      try {
        if (this.isEdit) {
          await call('project_management.api.client.update_project', {
            name: this.$route.params.id,
            data: this.form,
          })
        } else {
          await call('project_management.api.client.create_project', {
            data: this.form,
          })
        }
        this.$router.push('/projects')
      } catch (err) {
        this.error = err.message || 'Failed to save project'
      } finally {
        this.saving = false
      }
    },
  },
}
</script>
