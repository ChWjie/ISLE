import request from './request'
import type { Agent, AgentAnalysisRequest } from '@/types'

export const agentApi = {
    // 获取智能体列表
    getAgents: () =>
        request.get<Agent[]>('/api/v1/agents'),

    // 获取智能体详情
    getAgentById: (id: string) =>
        request.get<Agent>(`/api/v1/agents/${id}`),

    // 配置智能体
    configureAgent: (data: any) =>
        request.post('/api/v1/agents/configure', data),

    // 启动智能体分析
    startAnalysis: (data: AgentAnalysisRequest) =>
        request.post('/api/v1/agents/analyze', data),

    // 查询任务状态
    getTaskStatus: (taskId: string) =>
        request.get(`/api/v1/agents/task/${taskId}`),
}
