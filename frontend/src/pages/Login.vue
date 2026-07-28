<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm">
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div class="flex items-center justify-center gap-2 mb-6">
          <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
            <feather-icon name="briefcase" class="w-5 h-5 text-white" />
          </div>
        </div>
        <h1 class="text-center text-lg font-semibold text-gray-800 mb-1">Project Management</h1>
        <p class="text-center text-xs text-gray-400 mb-6">Sign in to your account</p>

        <div class="space-y-4">
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Email</label>
            <input
              v-model="email"
              type="email"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label class="block text-xs font-medium text-gray-600 mb-1">Password</label>
            <input
              v-model="password"
              type="password"
              class="w-full px-3 py-2 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400"
              placeholder="Password"
            />
          </div>
          <button
            @click="login"
            :disabled="loading"
            class="w-full py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {{ loading ? 'Signing in...' : 'Sign In' }}
          </button>
        </div>

        <p v-if="error" class="text-xs text-red-500 text-center mt-3">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'Login',
  components: { FeatherIcon },
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: '',
    }
  },
  methods: {
    async login() {
      this.error = ''
      this.loading = true
      try {
        await frappe.call('login', {
          usr: this.email,
          pwd: this.password,
        })
        window.location.reload()
      } catch (err) {
        this.error = err.message || 'Login failed'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
