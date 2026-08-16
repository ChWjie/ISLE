import request from './request'

export const planGenerationApi = {
    // 生成四方向法律分析方案
    generatePlan: (data: {
        event_id: string
        event_title: string
        event_type: string
        event_description: string
        location: { lat: number; lng: number }
        parties: string[]
        agent_configs?: any[]
    }) => request.post('/api/v1/plan-generation/generate', data)
}
