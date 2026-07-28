<template>
  <aside
    class="flex flex-col bg-white border-r border-gray-200 transition-all duration-300"
    :class="collapsed ? 'w-16' : 'w-60'"
  >
    <!-- Logo -->
    <div class="flex items-center h-14 px-4 border-b border-gray-200">
      <div class="flex items-center gap-2 min-w-0">
        <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
          <feather-icon name="briefcase" class="w-4 h-4 text-white" />
        </div>
        <span v-if="!collapsed" class="text-sm font-semibold text-gray-800 truncate">
          Project Mgmt
        </span>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-3 px-2 space-y-1 overflow-y-auto">
      <router-link
        v-for="item in managerNav"
        :key="item.route"
        :to="item.route"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors"
        :class="isActive(item.route) ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'"
      >
        <feather-icon :name="item.icon" class="w-4 h-4 flex-shrink-0" />
        <span v-if="!collapsed">{{ item.label }}</span>
      </router-link>

      <div v-if="!collapsed" class="pt-4 pb-2 px-3">
        <p class="text-xs font-medium text-gray-400 uppercase tracking-wider">Portals</p>
      </div>

      <router-link
        v-for="item in portalNav"
        :key="item.route"
        :to="item.route"
        class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors"
        :class="isActive(item.route) ? 'bg-blue-50 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'"
      >
        <feather-icon :name="item.icon" class="w-4 h-4 flex-shrink-0" />
        <span v-if="!collapsed">{{ item.label }}</span>
      </router-link>
    </nav>

    <!-- Collapse toggle -->
    <button
      @click="$emit('toggle')"
      class="flex items-center justify-center h-10 border-t border-gray-200 text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-colors"
    >
      <feather-icon
        :name="collapsed ? 'chevron-right' : 'chevron-left'"
        class="w-4 h-4"
      />
    </button>
  </aside>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'Sidebar',
  components: { FeatherIcon },
  props: {
    collapsed: Boolean,
  },
  emits: ['toggle'],
  data() {
    return {
      managerNav: [
        { label: 'Dashboard', icon: 'home', route: '/' },
        { label: 'Projects', icon: 'folder', route: '/projects' },
      ],
      portalNav: [
        { label: 'Member Portal', icon: 'users', route: '/member/dashboard' },
        { label: 'Client Portal', icon: 'user', route: '/client/dashboard' },
        { label: 'Vendor Portal', icon: 'truck', route: '/vendor/dashboard' },
      ],
    }
  },
  methods: {
    isActive(route) {
      if (route === '/') {
        return this.$route.path === '/'
      }
      return this.$route.path.startsWith(route)
    },
  },
}
</script>
