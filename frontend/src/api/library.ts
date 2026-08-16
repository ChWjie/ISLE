import request from './request'

export const lawApi = {
    // 获取法律列表
    getLaws: (params?: {
        category?: string
        search?: string
        skip?: number
        limit?: number
    }) => request.get('/api/v1/laws', { params }),

    // 获取单个法律
    getLaw: (code: string) => request.get(`/api/v1/laws/${code}`),

    // 获取分类列表
    getCategories: () => request.get('/api/v1/laws/categories/list')
}

export const caseApi = {
    // 保存案例
    saveCase: (data: any) => request.post('/api/v1/cases', data),

    // 获取案例列表
    getCases: (params?: {
        event_type?: string
        skip?: number
        limit?: number
    }) => request.get('/api/v1/cases', { params }),

    // 获取单个案例
    getCase: (caseId: string) => request.get(`/api/v1/cases/${caseId}`),

    // 删除案例
    deleteCase: (caseId: string) => request.delete(`/api/v1/cases/${caseId}`)
}
