import request from './request'

export const planApi = {
    // S4: 生成初步方案
    generatePlan(data: { event_id: string; agent_results: any[] }) {
        return request({
            url: '/api/v1/plans/generate',
            method: 'post',
            data
        })
    },

    // S5: 获取所有方案列表
    getPlans() {
        return request({
            url: '/api/v1/plans',
            method: 'get'
        })
    },

    // 获取方案详情
    getPlan(planId: string) {
        return request({
            url: `/api/v1/plans/${planId}`,
            method: 'get'
        })
    },

    // S6: 优化方案
    optimizePlan(planId: string, gameResult: any) {
        return request({
            url: `/api/v1/plans/${planId}/optimize`,
            method: 'post',
            data: gameResult
        })
    },

    // S6: 签发方案
    approvePlan(planId: string) {
        return request({
            url: `/api/v1/plans/${planId}/approve`,
            method: 'post'
        })
    },

    // S7: 部署方案
    deployPlan(planId: string) {
        return request({
            url: `/api/v1/plans/${planId}/deploy`,
            method: 'post'
        })
    }
}
