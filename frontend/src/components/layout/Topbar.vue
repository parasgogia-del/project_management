<template>
  <header class="flex items-center justify-between h-14 px-6 bg-white border-b border-gray-200">
    <!-- Left: hamburger + search -->
    <div class="flex items-center gap-4">
      <button
        @click="$emit('toggle-sidebar')"
        class="p-1 rounded hover:bg-gray-100 text-gray-500"
      >
        <feather-icon name="menu" class="w-5 h-5" />
      </button>
    </div>

    <!-- Right: notifications + profile -->
    <div class="flex items-center gap-4">
      <button
        @click="showNotifications = !showNotifications"
        class="relative p-2 rounded-lg hover:bg-gray-100 text-gray-500"
      >
        <feather-icon name="bell" class="w-5 h-5" />
        <span
          v-if="unreadCount > 0"
          class="absolute -top-0.5 -right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center"
        >
          {{ unreadCount > 9 ? '9+' : unreadCount }}
        </span>
      </button>

      <!-- Notifications dropdown -->
      <div
        v-if="showNotifications"
        class="absolute right-4 top-14 w-80 bg-white border border-gray-200 rounded-xl shadow-lg z-50 max-h-96 overflow-y-auto"
      >
        <div class="p-3 border-b border-gray-100">
          <p class="text-sm font-semibold text-gray-800">Notifications</p>
        </div>
        <div v-if="notifications.length === 0" class="p-4 text-center text-sm text-gray-400">
          No notifications
        </div>
        <div v-else>
          <div
            v-for="n in notifications"
            :key="n.name"
            class="px-3 py-2 border-b border-gray-50 hover:bg-gray-50 cursor-pointer"
          >
            <p class="text-xs text-gray-600" v-html="n.subject || n.message || 'Notification'" />
            <p class="text-[10px] text-gray-400 mt-0.5">{{ n.creation }}</p>
          </div>
        </div>
      </div>

      <!-- User profile -->
      <div class="relative" data-profile>
        <button
          @click="showProfile = !showProfile"
          class="flex items-center gap-2 rounded-lg hover:bg-gray-50 p-1.5"
        >
          <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span class="text-xs font-medium text-blue-700">{{ userInitials }}</span>
          </div>
          <div class="leading-tight text-left">
            <span class="block text-sm text-gray-700">{{ userName }}</span>
            <span class="block text-[10px] text-gray-400 uppercase tracking-wide">{{ userRole }}</span>
          </div>
          <feather-icon name="chevron-down" class="w-4 h-4 text-gray-400" />
        </button>

        <!-- Profile dropdown -->
        <div
          v-if="showProfile"
          class="absolute right-0 top-full mt-2 w-72 bg-white border border-gray-200 rounded-xl shadow-lg z-50"
        >
          <div class="p-4 border-b border-gray-100 flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <span class="text-sm font-semibold text-blue-700">{{ userInitials }}</span>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-800 truncate">{{ profile?.full_name || userName }}</p>
              <p class="text-xs text-gray-500 truncate">{{ profile?.email || currentUser }}</p>
            </div>
          </div>
          <div class="px-4 py-3 border-b border-gray-100 space-y-2">
            <p class="text-xs text-gray-500 flex items-center gap-2">
              <feather-icon name="user" class="w-3.5 h-3.5 text-gray-400" />
              <span class="truncate">{{ currentUser }}</span>
            </p>
            <p v-if="profile?.mobile_no" class="text-xs text-gray-500 flex items-center gap-2">
              <feather-icon name="phone" class="w-3.5 h-3.5 text-gray-400" />
              <span class="truncate">{{ profile.mobile_no }}</span>
            </p>
            <p v-if="profile?.location" class="text-xs text-gray-500 flex items-center gap-2">
              <feather-icon name="map-pin" class="w-3.5 h-3.5 text-gray-400" />
              <span class="truncate">{{ profile.location }}</span>
            </p>
            <p class="text-xs text-gray-500 flex items-center gap-2">
              <feather-icon name="shield" class="w-3.5 h-3.5 text-gray-400" />
              <span class="truncate">{{ userRole }}</span>
            </p>
            <p v-if="profile?.last_login" class="text-xs text-gray-500 flex items-center gap-2">
              <feather-icon name="clock" class="w-3.5 h-3.5 text-gray-400" />
              <span class="truncate">Last login: {{ formatDate(profile.last_login) }}</span>
            </p>
          </div>
          <button
            @click="logout"
            class="w-full text-left text-xs text-gray-600 hover:text-red-600 hover:bg-red-50 px-4 py-3 rounded-b-xl flex items-center gap-2 transition-colors"
          >
            <feather-icon name="log-out" class="w-3.5 h-3.5" />
            Logout
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { FeatherIcon, frappeRequest } from 'frappe-ui'
import { useNotifications, useProfile } from '@/data/resources'
import { session } from '@/data/session'

export default {
  name: 'Topbar',
  components: { FeatherIcon },
  emits: ['toggle-sidebar'],
  data() {
    return {
      showNotifications: false,
      showProfile: false,
      notifications: [],
      unreadCount: 0,
      notificationsResource: useNotifications(),
      profileResource: useProfile(),
    }
  },
  computed: {
    profile() {
      return this.profileResource.data
    },
    currentUser() {
      return session.user
    },
    userName() {
      return this.profile?.full_name || this.notificationsResource.data?.full_name || 'User'
    },
    userInitials() {
      const name = this.userName
      return name
        .split(' ')
        .map(w => w[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    },
    userRole() {
      const roles = session.roles
      if (roles.includes('Project Manager')) return 'Project Manager'
      if (roles.includes('Project Member')) return 'Member'
      if (roles.includes('Client')) return 'Client'
      if (roles.includes('Vendor')) return 'Vendor'
      return 'Guest'
    },
  },
  mounted() {
    this.loadNotifications()
    this.profileResource.fetch()
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString()
    },
    async logout() {
      if (!window.confirm('Are you sure you want to logout?')) return
      try {
        await frappeRequest({ url: 'logout', method: 'POST' })
      } catch {}
      window.location.href = '/login'
    },
    async loadNotifications() {
      try {
        await this.notificationsResource.fetch()
        this.notifications = this.notificationsResource.data || []
        this.unreadCount = this.notifications.length
      } catch {
        this.notifications = []
      }
    },
    handleClickOutside(e) {
      if (!e.target.closest('[data-notifications]')) {
        this.showNotifications = false
      }
      if (!e.target.closest('[data-profile]')) {
        this.showProfile = false
      }
    },
  },
}
</script>
