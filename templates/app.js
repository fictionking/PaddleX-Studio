import { createApp, createRouter, createWebHashHistory } from 'vue'
const { ElMessage, ElIcon, Document, Folder, ElCard, ElForm } = ElementPlus

// 定义路由
const router = createRouter({
    history: createWebHashHistory(),
    routes: [
        { path: '/model', component: () => import('./components/ModelList.vue') },
        { path: '/dataset', component: () => import('./components/DatasetList.vue') },
        { path: '/model/detail/:modelId', component: () => import('./components/ModelDetail.vue') }
    ]
})

createApp({
    components: {
        ElIcon, Document, Folder, ElCard, ElForm,  // 注册ElForm及ElCard组件（已正确导入）
        'ico_helpfilled': ElementPlusIconsVue.HelpFilled,
        'ico_menu': ElementPlusIconsVue.Menu,
        'ico_delete': ElementPlusIconsVue.Delete
    }
}).use(ElementPlus).mount('#app')