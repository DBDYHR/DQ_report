import { createRouter, createWebHistory } from 'vue-router'

// 引入刚才创建的组件
import ChatMode from '../views/ChatMode.vue'
import PlatformMode from '../views/PlatformMode.vue'
import EditorView from '../views/EditorView.vue'
import TemplatesView from '../views/TemplatesView.vue'
import ReportWizard from '../views/ReportWizard.vue';

const routes = [
    {
        path: '/',
        redirect: '/chat' // 默认跳到 chat
    },
    {
        path: '/chat',
        name: 'Chat',
        component: ChatMode
    },
    {
        path: '/platform',
        name: 'Platform',
        component: PlatformMode
    },
    {
        path: '/templates',
        name: 'Templates',
        component: TemplatesView
    },
    {
        path: '/wizard',
        name: 'Wizard',
        component: ReportWizard
    },
    {
        path: '/new-report',
        name: 'NewReport',
        component: () => import('../views/NewReportView.vue')
    },
    {
        path: '/editor/:id', // :id 是动态参数，代表报告ID
        name: 'Editor',
        component: EditorView
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router