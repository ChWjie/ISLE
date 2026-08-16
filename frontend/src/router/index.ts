import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            redirect: '/situation'
        },
        {
            path: '/situation',
            name: 'Situation',
            component: () => import('@/views/S1-Situation/index.vue'),
            meta: { title: 'S1 态势挖掘' }
        },
        {
            path: '/event/:id',
            name: 'EventDetail',
            component: () => import('@/views/S2-EventDetail/index.vue'),
            meta: { title: 'S2 事件详情' }
        },
        // 智能体配置入口页（无参数）
        {
            path: '/agent-config',
            name: 'AgentConfigEntry',
            component: () => import('@/views/AgentConfigEntry/index.vue'),
            meta: { title: '智能律师团配置' }
        },
        // 智能体配置页（带eventId参数）
        {
            path: '/agent-config/:id',
            name: 'AgentConfig',
            component: () => import('@/views/S3-AgentConfig/index.vue'),
            meta: { title: 'S3 智能体配置' }
        },
        {
            path: '/plan-generation/:eventId',
            name: 'PlanGeneration',
            component: () => import('@/views/S4-PlanGeneration/index.vue'),
            meta: { title: 'S4 方案生成' }
        },
        {
            path: '/game-simulation/:planId',
            name: 'GameSimulation',
            component: () => import('@/views/S5-GameSimulation/index.vue'),
            meta: { title: 'S5 博弈推演' }
        },
        {
            path: '/plan-optimize/:planId',
            name: 'PlanOptimize',
            component: () => import('@/views/S6-PlanOptimize/index.vue'),
            meta: { title: 'S6 方案优化' }
        },
        {
            path: '/deployment/:planId',
            name: 'Deployment',
            component: () => import('@/views/S7-Deployment/index.vue'),
            meta: { title: 'S7 方案落地' }
        },
        {
            path: '/deployment/:planId',
            name: 'Deployment',
            component: () => import('@/views/S7-Deployment/index.vue'),
            meta: { title: 'S7 方案落地' }
        },
        // S6 Plan Optimization Standalone
        {
            path: '/simulation/optimization/:id',
            name: 'SimulationPlanOptimization',
            component: () => import('@/views/S6-PlanOptimization/index.vue'),
            meta: { title: 'S6 方案优化' }
        },
        // 法庭博弈模拟入口页（无参数）
        {
            path: '/simulation',
            name: 'SimulationEntry',
            component: () => import('@/views/SimulationEntry/index.vue'),
            meta: { title: '法庭博弈模拟' }
        },
        // 原有的simulation子路由（保留用于从首页流程访问）
        {
            path: '/simulation-flow',
            name: 'SimulationFlow',
            component: () => import('@/views/Simulation/index.vue'),
            meta: { title: '法庭博弈模拟' },
            redirect: '/simulation-flow/plan-generation',
            children: [
                {
                    path: 'plan-generation/:eventId?',
                    name: 'SimulationPlanGeneration',
                    component: () => import('@/views/S4-PlanGeneration/index.vue'),
                    meta: { title: '方案生成' }
                },
                {
                    path: 'game/:planId',
                    name: 'SimulationGame',
                    component: () => import('@/views/S5-GameSimulation/index.vue'),
                    meta: { title: '博弈推演' }
                },
                {
                    path: 'optimize/:planId',
                    name: 'SimulationOptimize',
                    component: () => import('@/views/S6-PlanOptimize/index.vue'),
                    meta: { title: '方案优化' }
                }
            ]
        },
        {
            path: '/law-library',
            name: 'LawLibrary',
            component: () => import('@/views/LawLibrary/index.vue'),
            meta: { title: '法律库' }
        },
        {
            path: '/plan-library',
            name: 'PlanLibrary',
            component: () => import('@/views/PlanLibrary/index.vue'),
            meta: { title: '方案库' }
        }
    ]
})

router.beforeEach((to, _, next) => {
    // 设置页面标题
    if (to.meta.title) {
        document.title = `${to.meta.title} - 法律博弈智能分析平台`
    }
    next()
})

export default router
