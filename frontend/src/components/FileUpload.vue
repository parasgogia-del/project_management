<template>
  <div>
    <div class="flex items-center justify-between mb-3">
      <h4 class="text-sm font-semibold text-gray-700">Files</h4>
      <label class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 rounded-lg cursor-pointer hover:bg-blue-100 transition-colors">
        <feather-icon name="upload" class="w-3.5 h-3.5" />
        Upload
        <input type="file" class="hidden" @change="handleUpload" />
      </label>
    </div>

    <div v-if="uploading" class="flex items-center gap-2 text-xs text-blue-600 mb-2">
      <div class="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
      Uploading...
    </div>

    <div v-if="files.length === 0" class="text-xs text-gray-400 py-4 text-center">
      No files attached
    </div>

    <div v-else class="space-y-2">
      <div
        v-for="file in files"
        :key="file.name"
        class="flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 group"
      >
        <div class="flex items-center gap-2 min-w-0">
          <feather-icon name="file" class="w-4 h-4 text-gray-400 flex-shrink-0" />
          <a
            :href="file.file_url"
            target="_blank"
            class="text-xs text-blue-600 hover:underline truncate"
          >
            {{ file.file_name }}
          </a>
          <span class="text-[10px] text-gray-400 flex-shrink-0">{{ formatDate(file.creation) }}</span>
        </div>
        <button
          @click="handleDelete(file.name)"
          class="p-1 rounded hover:bg-red-50 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"
        >
          <feather-icon name="trash-2" class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { call } from '@/utils/api.js'

export default {
  name: 'FileUpload',
  components: { FeatherIcon },
  props: {
    doctype: { type: String, required: true },
    docname: { type: String, required: true },
  },
  emits: ['uploaded', 'deleted'],
  data() {
    return {
      files: [],
      uploading: false,
    }
  },
  mounted() {
    this.loadFiles()
  },
  methods: {
    async loadFiles() {
      try {
        let url, params
        if (this.doctype === 'Project Info') {
          url = 'project_management.api.file.get_project_files'
          params = { project: this.docname }
        } else if (this.doctype === 'Deliverable') {
          url = 'project_management.api.file.get_deliverable_files'
          params = { deliverable: this.docname }
        } else if (this.doctype === 'Project Task') {
          url = 'project_management.api.file.get_task_files'
          params = { task: this.docname }
        } else {
          this.files = []
          return
        }
        const result = await call(url, params)
        this.files = result.message || []
      } catch {
        this.files = []
      }
    },
    async handleUpload(e) {
      const file = e.target.files[0]
      if (!file) return

      this.uploading = true
      try {
        let paramName, url
        if (this.doctype === 'Project Info') {
          paramName = 'project'
          url = 'project_management.api.file.upload_project_file'
        } else if (this.doctype === 'Deliverable') {
          paramName = 'deliverable'
          url = 'project_management.api.file.upload_deliverable_file'
        } else if (this.doctype === 'Project Task') {
          paramName = 'task'
          url = 'project_management.api.file.upload_task_file'
        } else {
          return
        }

        const formData = new FormData()
        formData.append('file', file)
        formData.append(paramName, this.docname)

        const token = window.csrf_token || (typeof frappe !== 'undefined' && frappe.csrf_token) || ''
        if (token) formData.append('csrf_token', token)

        await fetch(`/api/method/${url}`, {
          method: 'POST',
          body: formData,
        })
        this.$emit('uploaded')
        await this.loadFiles()
      } catch (err) {
        console.error('Upload failed', err)
      } finally {
        this.uploading = false
        e.target.value = ''
      }
    },
    async handleDelete(fileName) {
      try {
        let url
        if (this.doctype === 'Project Info') {
          url = 'project_management.api.file.delete_project_file'
        } else if (this.doctype === 'Deliverable') {
          url = 'project_management.api.file.delete_deliverable_file'
        } else if (this.doctype === 'Project Task') {
          url = 'project_management.api.file.delete_task_file'
        } else {
          return
        }
        await call(url, { file_name: fileName })
        this.$emit('deleted')
        await this.loadFiles()
      } catch (err) {
        console.error('Delete failed', err)
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString()
    },
  },
}
</script>
