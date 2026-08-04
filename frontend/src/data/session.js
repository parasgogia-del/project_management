import { computed, reactive } from 'vue'
import { createResource } from 'frappe-ui'

export const sessionUser = createResource({
  url: 'project_management.api.client.get_session_user',
  cache: 'SessionUser',
  onError(error) {
    console.error('Failed to get session user', error)
  },
})

export const session = reactive({
  user: computed(() => sessionUser.data?.user || 'Guest'),
  roles: computed(() => sessionUser.data?.roles || []),
  isLoggedIn: computed(() => !!sessionUser.data && sessionUser.data.user !== 'Guest'),
})

export function getPortal() {
  const roles = session.roles
  if (roles.includes('Project Manager')) return '/'
  if (roles.includes('Project Member')) return '/member/dashboard'
  if (roles.includes('Client')) return '/client/dashboard'
  if (roles.includes('Vendor')) return '/vendor/dashboard'
  return null
}

window.currentUser = session
