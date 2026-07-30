<template>
  <teleport to="body">
    <transition name="toast">
      <div
        v-if="visible"
        class="fixed bottom-6 right-6 z-[9999] max-w-sm"
      >
        <div
          class="flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border text-sm font-medium"
          :class="typeClasses"
        >
          <feather-icon :name="iconName" class="w-4 h-4 flex-shrink-0" />
          <span>{{ message }}</span>
          <button @click="hide" class="ml-2 opacity-60 hover:opacity-100">
            <feather-icon name="x" class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'Toast',
  components: { FeatherIcon },
  data() {
    return {
      visible: false,
      message: '',
      type: 'success',
      timer: null,
    }
  },
  computed: {
    typeClasses() {
      const map = {
        success: 'bg-green-50 border-green-200 text-green-800',
        error: 'bg-red-50 border-red-200 text-red-800',
        warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
        info: 'bg-blue-50 border-blue-200 text-blue-800',
      }
      return map[this.type] || map.info
    },
    iconName() {
      const map = {
        success: 'check-circle',
        error: 'alert-circle',
        warning: 'alert-triangle',
        info: 'info',
      }
      return map[this.type] || 'info'
    },
  },
  methods: {
    show(msg, toastType = 'success', duration = 3000) {
      this.message = msg
      this.type = toastType
      this.visible = true
      if (this.timer) clearTimeout(this.timer)
      this.timer = setTimeout(() => this.hide(), duration)
    },
    hide() {
      this.visible = false
      if (this.timer) clearTimeout(this.timer)
    },
  },
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateY(-12px);
}
</style>
