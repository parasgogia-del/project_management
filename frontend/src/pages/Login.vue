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
          <Input v-model="email" type="email" label="Email" placeholder="you@example.com" />
          <Input v-model="password" type="password" label="Password" placeholder="Password" />
          <Button
            appearance="primary"
            class="w-full"
            :loading="loading"
            :loading-text="loading ? 'Signing in...' : null"
            @click="login"
          >Sign In</Button>
        </div>

        <p v-if="error" class="text-xs text-red-500 text-center mt-3">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Input, Button } from 'frappe-ui'

export default {
  name: 'Login',
  components: { FeatherIcon, Input, Button },
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
        await frappeRequest({
          url: 'login',
          method: 'POST',
          params: { usr: this.email, pwd: this.password },
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
