import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'
import router from '@/router'

export const sessionUser = createResource({
  url: 'project_management.api.client.get_session_user',
  cache: 'SessionUser',
  onError(error) {
    console.error('Failed to get session user', error)
  },
})

export const session = reactive({
  user: computed(() => sessionUser.data),
  isLoggedIn: computed(() => !!sessionUser.data && sessionUser.data !== 'Guest'),
})
