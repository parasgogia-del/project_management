<template>
  <router-view />
  <Toasts />
</template>

<script>
import { Toasts } from 'frappe-ui'

export default {
  name: 'App',
  components: { Toasts },
}
</script>
