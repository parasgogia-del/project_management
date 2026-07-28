<template>
  <div class="flex flex-col items-center justify-center py-12 px-4">
    <div class="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
      <feather-icon :name="icon" class="w-8 h-8 text-gray-400" />
    </div>
    <p class="text-sm font-medium text-gray-600 mb-1">{{ title }}</p>
    <p v-if="description" class="text-xs text-gray-400">{{ description }}</p>
    <slot />
  </div>
</template>

<script>
import { FeatherIcon } from 'frappe-ui'

export default {
  name: 'EmptyState',
  components: { FeatherIcon },
  props: {
    icon: { type: String, default: 'inbox' },
    title: { type: String, default: 'No data found' },
    description: { type: String, default: '' },
  },
}
</script>
