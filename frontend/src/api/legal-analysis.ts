import request from './request'

export const legalAnalysisApi = {
    // 分析事件的法律框架
    analyzeEvent: (data: {
        event_id: string
        event_title: string
        event_type: string
        event_description: string
        location: { lat: number; lng: number }
        parties: string[]
    }) => request.post('/api/v1/legal-analysis/analyze', data)
}
