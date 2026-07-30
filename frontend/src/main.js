import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { setConfig, frappeRequest, resourcesPlugin } from 'frappe-ui'

document.addEventListener('click', async () => {
  try {
    const data = await frappeRequest({ url: 'project_management.api.client.get_session_user' })
    console.log('Current user:', data)
  } catch (e) {
    console.log('Could not fetch user:', e)
  }
})

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.use(router)
app.use(resourcesPlugin)

app.mount('#app')
