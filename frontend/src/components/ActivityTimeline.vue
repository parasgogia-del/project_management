<template>
  <div>
    <h4 class="text-sm font-semibold text-gray-700 mb-3">Activity</h4>
    <div v-if="items.length === 0" class="text-xs text-gray-400 py-4 text-center">
      No activity yet
    </div>
    <div v-else class="space-y-4">
      <div v-for="(item, idx) in items" :key="idx" class="flex gap-3">
        <div class="relative">
          <div class="w-2 h-2 rounded-full bg-blue-400 mt-1.5" />
          <div
            v-if="idx < items.length - 1"
            class="absolute left-[3px] top-3 w-px h-full bg-gray-200"
          />
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-xs text-gray-600">{{ item.text }}</p>
          <p class="text-[10px] text-gray-400 mt-0.5">{{ item.time }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActivityTimeline',
  props: {
    items: { type: Array, default: () => [] },
  },
}
</script>
