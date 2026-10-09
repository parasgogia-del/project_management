<template>
  <Sidebar
    :collapsed="collapsed"
    width="15rem"
    collapsed-width="3rem"
    class="border-r border-outline-gray-1"
  >
    <div class="flex h-full flex-col p-2">
      <!-- Logo -->
      <div class="flex h-12 shrink-0 items-center" :class="collapsed ? 'justify-center' : 'px-1'">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center flex-shrink-0">
            <span class="lucide-briefcase w-4 h-4 text-white" aria-hidden="true" />
          </div>
          <div v-if="!collapsed" class="leading-tight truncate">
            <span class="block text-base-medium text-ink-gray-8 truncate">Project Mgmt</span>
            <span class="block text-sm text-ink-gray-6 truncate">Workspace</span>
          </div>
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex-1 overflow-y-auto overflow-x-hidden pt-2">
        <SidebarItem
          v-for="item in navItems.primary"
          :key="item.route"
          :to="item.route"
          :icon="item.icon"
          :active="isActive(item.route)"
          :label="item.label"
        />

        <template v-if="navItems.portals.length">
          <SidebarLabel class="mt-4 mb-0.5">
            Portals
          </SidebarLabel>
          <SidebarItem
            v-for="item in navItems.portals"
            :key="item.route"
            :to="item.route"
            :icon="item.icon"
            :active="isActive(item.route)"
            :label="item.label"
          />
        </template>
      </div>

      <!-- Collapse toggle -->
      <div class="mt-auto border-t border-outline-gray-1 pt-1">
        <button
          @click="$emit('toggle')"
          class="flex h-7 w-full items-center justify-center rounded text-ink-gray-6 hover:bg-surface-gray-2 transition-colors"
        >
          <span
            :class="collapsed ? 'lucide-panel-left-open' : 'lucide-panel-left-close'"
            class="size-4"
            aria-hidden="true"
          />
        </button>
      </div>
    </div>
  </Sidebar>
</template>

<script>
import { Sidebar, SidebarItem, SidebarLabel } from 'frappe-ui'
import { session } from '@/data/session'

export default {
  name: 'AppSidebar',
  components: { Sidebar, SidebarItem, SidebarLabel },
  props: {
    collapsed: Boolean,
  },
  emits: ['toggle'],
  data() {
    return {
      managerNav: [
        { label: 'Dashboard', icon: 'lucide-home', route: '/' },
        { label: 'Projects', icon: 'lucide-folder', route: '/projects' },
        { label: 'Deliverables', icon: 'lucide-package', route: '/deliverables' },
        { label: 'Tasks', icon: 'lucide-list-todo', route: '/tasks' },
        { label: 'Support', icon: 'lucide-life-buoy', route: '/tickets' },
      ],
      portalNav: [
        { label: 'Member Portal', icon: 'lucide-users', route: '/member/dashboard' },
        { label: 'Client Portal', icon: 'lucide-user', route: '/client/dashboard' },
        { label: 'Vendor Portal', icon: 'lucide-truck', route: '/vendor/dashboard' },
      ],
      memberNav: [
        { label: 'Dashboard', icon: 'lucide-home', route: '/member/dashboard' },
        { label: 'Support', icon: 'lucide-life-buoy', route: '/tickets' },
      ],
      clientNav: [
        { label: 'Dashboard', icon: 'lucide-home', route: '/client/dashboard' },
        { label: 'Support', icon: 'lucide-life-buoy', route: '/tickets' },
      ],
      vendorNav: [
        { label: 'Dashboard', icon: 'lucide-home', route: '/vendor/dashboard' },
      ],
    }
  },
  computed: {
    navItems() {
      const roles = session.roles
      if (roles.includes('Project Manager')) {
        return { primary: this.managerNav, portals: this.portalNav }
      }
      if (roles.includes('Project Member')) {
        return { primary: this.memberNav, portals: [] }
      }
      if (roles.includes('Client')) {
        return { primary: this.clientNav, portals: [] }
      }
      if (roles.includes('Vendor')) {
        return { primary: this.vendorNav, portals: [] }
      }
      return { primary: [], portals: [] }
    },
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
