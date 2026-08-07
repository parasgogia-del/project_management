<template>
  <header class="flex items-center justify-between h-14 px-6 bg-surface-base border-b border-outline-gray-1">
    <!-- Left: hamburger -->
    <div class="flex items-center gap-4">
      <button
        @click="$emit('toggle-sidebar')"
        class="p-1 rounded hover:bg-surface-gray-2 text-ink-gray-5 transition-colors"
      >
        <feather-icon name="menu" class="w-5 h-5" />
      </button>
    </div>

    <!-- Right: notifications + profile -->
    <div class="flex items-center gap-4">
      <div class="relative" data-notifications>
        <button
          @click="toggleNotifications"
          class="relative p-2 rounded-lg hover:bg-surface-gray-2 text-ink-gray-5 transition-colors"
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
          class="absolute right-0 top-full mt-2 w-80 bg-surface-base border border-outline-gray-1 rounded-xl shadow-xl z-50 max-h-96 overflow-y-auto"
        >
        <div class="p-3 border-b border-outline-gray-1">
          <p class="text-base-medium text-ink-gray-8">Notifications</p>
        </div>
        <div v-if="notifications.length === 0" class="p-4 text-center text-sm text-ink-gray-4">
          No notifications
        </div>
        <div v-else>
          <div
            v-for="n in notifications"
            :key="n.name"
            class="px-3 py-2 border-b border-outline-gray-1 hover:bg-surface-gray-2 cursor-pointer"
          >
            <p class="text-xs text-ink-gray-6">{{ n.from_user }}</p>
            <p class="text-xs text-ink-gray-7" v-html="n.subject || n.message || 'Notification'" />
            <p class="text-[10px] text-ink-gray-4 mt-0.5">{{ formatNotificationDate(n.creation) }}</p>
          </div>
        </div>
      </div>
      </div>

      <!-- User profile -->
      <div class="relative" data-profile>
        <button
          @click="showProfile = !showProfile"
          class="flex items-center gap-2 rounded-lg hover:bg-surface-gray-2 p-1.5 transition-colors"
        >
          <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
            <span class="text-xs font-medium text-blue-700">{{ userInitials }}</span>
          </div>
          <div class="leading-tight text-left">
            <span class="block text-sm text-ink-gray-8">{{ userName }}</span>
            <span class="block text-[10px] text-ink-gray-5 uppercase tracking-wide">{{ userRole }}</span>
          </div>
          <feather-icon name="chevron-down" class="w-4 h-4 text-ink-gray-4" />
        </button>

        <!-- Profile dropdown -->
        <div
          v-if="showProfile"
          class="absolute right-0 top-full mt-2 w-72 bg-surface-base border border-outline-gray-1 rounded-xl shadow-xl z-50"
        >
          <div class="p-4 border-b border-outline-gray-1 flex items-center gap-3">
            <div class="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center shrink-0">
              <span class="text-sm font-semibold text-blue-700">{{ userInitials }}</span>
            </div>
            <div class="min-w-0">
              <p class="text-sm font-semibold text-ink-gray-8 truncate">{{ profile?.full_name || userName }}</p>
              <p class="text-xs text-ink-gray-5 truncate">{{ profile?.email || currentUser }}</p>
            </div>
          </div>
          <div class="px-4 py-3 border-b border-outline-gray-1 space-y-2">
            <p class="text-xs text-ink-gray-6 flex items-center gap-2">
              <feather-icon name="user" class="w-3.5 h-3.5 text-ink-gray-4" />
              <span class="truncate">{{ currentUser }}</span>
            </p>
            <p v-if="profile?.mobile_no" class="text-xs text-ink-gray-6 flex items-center gap-2">
              <feather-icon name="phone" class="w-3.5 h-3.5 text-ink-gray-4" />
              <span class="truncate">{{ profile.mobile_no }}</span>
            </p>
            <p v-if="profile?.location" class="text-xs text-ink-gray-6 flex items-center gap-2">
              <feather-icon name="map-pin" class="w-3.5 h-3.5 text-ink-gray-4" />
              <span class="truncate">{{ profile.location }}</span>
            </p>
            <p class="text-xs text-ink-gray-6 flex items-center gap-2">
              <feather-icon name="shield" class="w-3.5 h-3.5 text-ink-gray-4" />
              <span class="truncate">{{ userRole }}</span>
            </p>
            <p v-if="profile?.last_login" class="text-xs text-ink-gray-6 flex items-center gap-2">
              <feather-icon name="clock" class="w-3.5 h-3.5 text-ink-gray-4" />
              <span class="truncate">Last login: {{ formatDate(profile.last_login) }}</span>
            </p>
          </div>
          <button
            @click="logout"
            class="w-full text-left text-xs text-ink-gray-7 hover:text-red-600 hover:bg-red-50 px-4 py-3 rounded-b-xl flex items-center gap-2 transition-colors"
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
    this.pollTimer = setInterval(this.loadNotifications, 30000)
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    clearInterval(this.pollTimer)
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString()
    },
    formatNotificationDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleString()
    },
    toggleNotifications() {
      this.showNotifications = !this.showNotifications
      if (this.showNotifications && this.unreadCount > 0) {
        this.notifications.forEach(n => { n.read = 1 })
        this.unreadCount = 0
        frappeRequest({ url: 'frappe.desk.doctype.notification_log.notification_log.mark_all_as_read', method: 'POST' }).catch(() => {})
      }
    },
    async logout() {
      if (!window.confirm('Are you sure you want to logout?')) return
      try {
        await frappeRequest({ url: 'logout', method: 'POST' })
      } catch {}
      window.location.href = '/project_management/login'
    },
    async loadNotifications() {
      try {
        await this.notificationsResource.fetch()
        this.notifications = this.notificationsResource.data || []
        this.unreadCount = this.notifications.filter(n => !n.read).length
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
