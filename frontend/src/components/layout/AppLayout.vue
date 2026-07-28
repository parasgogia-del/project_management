<template>
  <div class="flex h-screen bg-gray-50">
    <Sidebar :collapsed="sidebarCollapsed" @toggle="sidebarCollapsed = !sidebarCollapsed" />
    <div class="flex flex-col flex-1 min-w-0">
      <Topbar @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed" />
      <main class="flex-1 overflow-auto p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import Sidebar from './Sidebar.vue'
import Topbar from './Topbar.vue'

export default {
  name: 'AppLayout',
  components: { Sidebar, Topbar },
  data() {
    return {
      sidebarCollapsed: false,
    }
  },
}
</script>
