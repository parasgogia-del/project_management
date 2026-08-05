<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm">
      <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <div class="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center mx-auto mb-4">
          <feather-icon name="shield-off" class="w-6 h-6 text-gray-500" />
        </div>
        <h1 class="text-lg font-semibold text-gray-800 mb-1">No Access</h1>
        <p class="text-xs text-gray-400 mb-6">
          Your account does not have access to this application.
        </p>
        <Button theme="blue" variant="solid" class="w-full" @click="logout">Logout</Button>
      </div>
    </div>
  </div>
</template>

<script>
import { FeatherIcon, Button, frappeRequest } from 'frappe-ui'

export default {
  name: 'NoAccess',
  components: { FeatherIcon, Button },
  methods: {
    async logout() {
      if (!window.confirm('Are you sure you want to logout?')) return
      try {
        await frappeRequest({ url: 'logout', method: 'POST' })
      } catch {}
      window.location.href = '/login'
    },
  },
}
</script>
