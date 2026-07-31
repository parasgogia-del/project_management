import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'

import { setConfig, frappeRequest, resourcesPlugin, Tooltip, Dropdown } from 'frappe-ui'
import { statusColorMap } from './utils/statusColors'

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

app.config.globalProperties.statusColorMap = statusColorMap
app.component('Tooltip', Tooltip)
app.component('Dropdown', Dropdown)

app.use(router)
app.use(resourcesPlugin)

app.mount('#app')
