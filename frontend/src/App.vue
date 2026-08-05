<template>
  <router-view />
  <ToastProvider />
</template>

<script>
import { ToastProvider } from 'frappe-ui'

export default {
  name: 'App',
  components: { ToastProvider },
}
</script>
