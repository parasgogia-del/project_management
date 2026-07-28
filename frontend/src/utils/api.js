import { frappeRequest } from 'frappe-ui'

export async function call(method, params = {}) {
  const result = await frappeRequest({
    url: method,
    method: 'POST',
    params: params,
  })
  return { message: result }
}
