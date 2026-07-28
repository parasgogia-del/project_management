<template>
  <div class="flex items-center gap-2">
    <div class="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
      <div
        class="h-full rounded-full transition-all duration-500"
        :class="barColor"
        :style="{ width: `${value}%` }"
      />
    </div>
    <span class="text-xs font-medium text-gray-600 min-w-[2rem] text-right">
      {{ value }}%
    </span>
  </div>
</template>

<script>
export default {
  name: 'ProgressBar',
  props: {
    value: { type: Number, default: 0 },
  },
  computed: {
    barColor() {
      if (this.value >= 80) return 'bg-green-500'
      if (this.value >= 50) return 'bg-blue-500'
      if (this.value >= 25) return 'bg-yellow-500'
      return 'bg-red-400'
    },
  },
}
</script>
