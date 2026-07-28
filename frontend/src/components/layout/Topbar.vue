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
      <div class="relative">
        <feather-icon name="search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search projects, tasks..."
          class="pl-9 pr-4 py-2 w-72 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400 focus:ring-1 focus:ring-blue-400 bg-gray-50"
        />
      </div>
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
      <div class="flex items-center gap-2">
        <div class="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
          <span class="text-xs font-medium text-blue-700">{{ userInitials }}</span>
        </div>
        <span class="text-sm text-gray-700">{{ userName }}</span>
      </div>
    </div>
  </header>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'
import { useNotifications } from '@/data/resources'

export default {
  name: 'Topbar',
  components: { FeatherIcon },
  emits: ['toggle-sidebar'],
  data() {
    return {
      searchQuery: '',
      showNotifications: false,
      notifications: [],
      unreadCount: 0,
      notificationsResource: useNotifications(),
    }
  },
  computed: {
    userName() {
      return this.notificationsResource.data?.full_name || 'User'
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
  },
  mounted() {
    this.loadNotifications()
    document.addEventListener('click', this.handleClickOutside)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
  },
  methods: {
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
    },
  },
}
</script>
