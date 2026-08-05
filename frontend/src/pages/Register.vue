<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm">
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <div class="flex items-center justify-center gap-2 mb-6">
          <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center">
            <feather-icon name="user-plus" class="w-5 h-5 text-white" />
          </div>
        </div>
        <h1 class="text-center text-lg font-semibold text-gray-800 mb-1">Create Account</h1>
        <p class="text-center text-xs text-gray-400 mb-6">Join to start collaborating</p>

        <div class="space-y-4">
          <Input v-model="form.full_name" type="text" label="Full Name" placeholder="John Doe" />
          <Input v-model="form.email" type="email" label="Email" placeholder="you@example.com" />
          <Input v-model="form.password" type="password" label="Password" placeholder="At least 6 characters" />
          <Input v-model="confirmPassword" type="password" label="Confirm Password" placeholder="Re-enter password" />

          <Select
            v-model="form.role"
            label="I am a"
            :options="roleOptions"
            class="w-full"
          />

          <Button
            theme="blue" variant="solid"
            class="w-full"
            :loading="loading"
            :loading-text="loading ? 'Creating account...' : null"
            @click="register"
          >Create Account</Button>
        </div>

        <p v-if="error" class="text-xs text-red-500 text-center mt-3">{{ error }}</p>

        <div class="text-center mt-4">
          <span class="text-xs text-gray-400">Already have an account? </span>
          <a class="text-xs text-blue-600 hover:underline" @click="$router.push('/login')">Sign in</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, frappeRequest, Input, Select, Button } from 'frappe-ui'

export default {
  name: 'Register',
  components: { FeatherIcon, Input, Select, Button },
  data() {
    return {
      form: {
        full_name: '',
        email: '',
        password: '',
        role: 'Project Member',
      },
      confirmPassword: '',
      roleOptions: [
        { label: 'Project Member', value: 'Project Member' },
        { label: 'Client', value: 'Client' },
        { label: 'Vendor', value: 'Vendor' },
      ],
      loading: false,
      error: '',
    }
  },
  methods: {
    async register() {
      this.error = ''
      const { full_name, email, password, role } = this.form

      if (!full_name || !email || !password) {
        this.error = 'Please fill in all fields'
        return
      }
      if (password !== this.confirmPassword) {
        this.error = 'Passwords do not match'
        return
      }

      this.loading = true
      try {
        await frappeRequest({
          url: 'project_management.api.auth.create_portal_user',
          method: 'POST',
          params: { full_name, email, password, role },
        })
        this.$router.push('/login')
      } catch (err) {
        this.error = err.message || 'Failed to create account'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
