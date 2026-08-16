import request from './request'

export const caseApi = {
    // 保存S4生成的方案到数据库
    savePlan(data: {
        event_id: string
        title: string
        event_type: string
        event_description: string
        location?: any
        parties?: string[]
        plan_data: any
    }) {
        return request({
            url: '/api/v1/cases/save-plan',
            method: 'post',
            data
        })
    },

    // 获取方案列表
    getPlans(params?: { skip?: number; limit?: number; event_type?: string }) {
        return request({
            url: '/api/v1/plans',
            method: 'get',
            params
        })
    },

    // 获取单个方案详情
    getPlanDetail(caseId: string) {
        return request({
            url: `/api/v1/plans/${caseId}`,
            method: 'get'
        })
    },

    // 删除方案
    deletePlan(caseId: string) {
        return request({
            url: `/api/v1/plans/${caseId}`,
            method: 'delete'
        })
    }
}
