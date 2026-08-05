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
            theme="blue" variant="solid"
            class="w-full"
            :loading="loading"
            :loading-text="loading ? 'Signing in...' : null"
            @click="login"
          >Sign In</Button>
        </div>

        <div class="mt-4 text-center space-y-2">
          <div>
            <a class="text-xs text-blue-600 hover:underline" :href="`/login#forgot`">Forgot password?</a>
          </div>
          <div>
            <span class="text-xs text-gray-400">Don't have an account? </span>
            <a class="text-xs text-blue-600 hover:underline cursor-pointer" @click="$router.push('/register')">Create a new account</a>
          </div>
        </div>
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
        // no-op
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
