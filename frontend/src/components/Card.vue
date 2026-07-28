<template>
  <div class="border border-gray-200 rounded-xl bg-white">
    <div v-if="$slots.header" class="px-4 py-3 border-b border-gray-100">
      <slot name="header" />
    </div>
    <div class="p-4">
      <slot />
    </div>
    <div v-if="$slots.footer" class="px-4 py-3 border-t border-gray-100">
      <slot name="footer" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'Card',
}
</script>
