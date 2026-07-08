import { createApp } from 'vue'
import DataV from '@kjgl77/datav-vue3'
import App from './App.vue'
import './style.css'

const app = createApp(App)
app.use(DataV)
app.mount('#app')
