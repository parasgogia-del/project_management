<template>
  <div class="space-y-3">
    <div v-for="i in lines" :key="i" class="animate-pulse">
      <div class="h-4 bg-gray-200 rounded" :style="{ width: `${60 + Math.random() * 40}%` }" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'SkeletonLoader',
  props: {
    lines: { type: Number, default: 5 },
  },
}
</script>
