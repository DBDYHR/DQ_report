import { createApp } from 'vue'
import { createPinia } from 'pinia' // 1. 引入 Pinia
import './style.css'
import App from './App.vue'
import router from './router'
import { useReportStore } from './stores/useReportStore'

const app = createApp(App)

const pinia = createPinia()
app.use(pinia) // 2. 挂载 Pinia
app.use(router)

// 启动应用时，从后端初始化报告列表（若后端为空则同步内置示例）
const reportStore = useReportStore()
reportStore.initReports()

app.mount('#app')