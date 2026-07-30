import { frappeRequest } from 'frappe-ui'

function getCsrfToken() {
  const match = document.cookie.match(/frappe-csrf-token=([^;]+)/)
  if (match) return match[1]

  const tokenMeta = document.querySelector('meta[name="csrf_token"]')
  if (tokenMeta) return tokenMeta.content

  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    console.log('Using window.csrf_token:', window.csrf_token)
    return window.csrf_token
  }

  console.warn('No CSRF token found')
  return ''
}

export async function call(method, params = {}) {
  const result = await frappeRequest({
    url: method,
    method: 'POST',
    params: params,
    headers: {
      'X-Frappe-CSRF-Token': getCsrfToken(),
    },
  })
  return { message: result }
}
