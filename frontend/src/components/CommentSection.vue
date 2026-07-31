<template>
  <div>
    <h4 class="text-sm font-semibold text-gray-700 mb-3">Comments</h4>

    <!-- Add comment -->
    <div class="flex gap-2 mb-4">
      <input
        v-model="newComment"
        @keydown.enter="addComment"
        type="text"
        placeholder="Add a comment..."
        class="flex-1 px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
      />
      <button
        @click="addComment"
        :disabled="!newComment.trim()"
        class="px-3 py-2 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Post
      </button>
    </div>

    <!-- Comments list -->
    <div v-if="comments.length === 0" class="text-xs text-gray-400 py-4 text-center">
      No comments yet
    </div>

    <div v-else class="space-y-3">
      <div
        v-for="comment in comments"
        :key="comment.name"
        class="flex gap-2 group"
      >
        <div class="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span class="text-[10px] font-medium text-gray-500">
            {{ getInitials(comment.comment_email || comment.owner) }}
          </span>
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2">
            <span class="text-xs font-medium text-gray-700">
              {{ comment.comment_email || comment.owner }}
            </span>
            <span class="text-[10px] text-gray-400">{{ formatDate(comment.creation) }}</span>
          </div>
          <div v-if="editingId !== comment.name" class="text-xs text-gray-600 mt-0.5">
            {{ comment.content }}
          </div>
          <div v-else class="flex gap-2 mt-1">
            <input
              v-model="editContent"
              class="flex-1 px-2 py-1 text-xs border border-gray-200 rounded focus:outline-none focus:border-blue-400"
            />
            <button @click="saveEdit(comment.name)" class="text-xs text-blue-600 hover:underline">Save</button>
            <button @click="editingId = null" class="text-xs text-gray-400 hover:underline">Cancel</button>
          </div>
          <div class="flex gap-3 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              @click="startEdit(comment)"
              class="text-[10px] text-gray-400 hover:text-blue-600"
            >Edit</button>
            <button
              @click="deleteComment(comment.name)"
              class="text-[10px] text-gray-400 hover:text-red-500"
            >Delete</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { frappeRequest } from 'frappe-ui'
import { useComments } from '@/data/resources'

export default {
  name: 'CommentSection',
  props: {
    doctype: { type: String, required: true },
    docname: { type: String, required: true },
  },
  data() {
    return {
      comments: [],
      newComment: '',
      editingId: null,
      editContent: '',
      commentsResource: useComments(this.doctype, this.docname),
    }
  },
  mounted() {
    this.loadComments()
  },
  methods: {
    async loadComments() {
      try {
        this.comments = (await this.commentsResource.fetch()) || []
      } catch {
        this.comments = []
      }
    },
    async addComment() {
      if (!this.newComment.trim()) return
      try {
        await frappeRequest({
          url: 'project_management.api.client.add_comment',
          method: 'POST',
          params: {
            reference_doctype: this.doctype,
            reference_name: this.docname,
            content: this.newComment.trim(),
          },
        })
        this.newComment = ''
        await this.loadComments()
      } catch (err) {
        console.error('Failed to add comment', err)
      }
    },
    startEdit(comment) {
      this.editingId = comment.name
      this.editContent = comment.content
    },
    async saveEdit(name) {
      try {
        await frappeRequest({
          url: 'project_management.api.client.edit_comment',
          method: 'POST',
          params: {
            name,
            content: this.editContent.trim(),
          },
        })
        this.editingId = null
        await this.loadComments()
      } catch (err) {
        console.error('Failed to edit comment', err)
      }
    },
    async deleteComment(name) {
      try {
        await frappeRequest({
          url: 'project_management.api.client.delete_comment',
          method: 'POST',
          params: { name },
        })
        await this.loadComments()
      } catch (err) {
        console.error('Failed to delete comment', err)
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
  },
}
</script>
