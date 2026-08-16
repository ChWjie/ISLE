/**
 * Agent API Service
 */
import apiClient from './client'
import { apiUrl } from './config'

export interface Agent {
    id: number
    agent_id: string
    name: string
    agent_type: 'blue' | 'red' | 'judge' | 'analyst'
    system_prompt?: string
    stance?: string
    goals?: string[]
    strategy_orientation?: string
    legal_priority?: string
    model_config?: any
    template_id?: string
    event_id?: number
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface AgentTemplate {
    template_id: string
    name: string
    agent_type: string
    description: string
    system_prompt: string
    default_config: any
    suitable_scenarios: string[]
}

export interface CreateAgentRequest {
    name: string
    agent_type: string
    system_prompt?: string
    stance?: string
    goals?: string[]
    strategy_orientation?: string
    legal_priority?: string
    model_config?: any
    template_id?: string
    event_id?: number
}

const agentApi = {
    // 获取Agent模板
    async getTemplates(agentType?: string): Promise<AgentTemplate[]> {
        const params = agentType ? { agent_type: agentType } : {}
        return apiClient.get('/api/v1/agents/templates', { params })
    },

    // 获取Agent列表
    async listAgents(params?: {
        agent_type?: string
        event_id?: number
        is_active?: boolean
    }): Promise<Agent[]> {
        try {
            return await apiClient.get('/api/v1/agents', { params })
        } catch (error) {
            const query = new URLSearchParams()
            if (params?.agent_type) query.set('agent_type', params.agent_type)
            if (params?.event_id !== undefined) query.set('event_id', String(params.event_id))
            if (params?.is_active !== undefined) query.set('is_active', String(params.is_active))
            const url = apiUrl(`/api/v1/agents${query.toString() ? `?${query}` : ''}`)
            console.warn('[agents] apiClient failed, fallback fetch:', url, error)
            const response = await fetch(url)
            if (!response.ok) throw new Error(`加载智能体失败：${response.status}`)
            const result = await response.json()
            return Array.isArray(result) ? result : (result?.data || [])
        }
    },

    // 创建Agent
    async createAgent(data: CreateAgentRequest): Promise<Agent> {
        return apiClient.post('/api/v1/agents', data)
    },

    // 获取单个Agent
    async getAgent(agentId: string): Promise<Agent> {
        return apiClient.get(`/api/v1/agents/${agentId}`)
    },

    // 更新Agent
    async updateAgent(agentId: string, data: Partial<CreateAgentRequest>): Promise<Agent> {
        return apiClient.put(`/api/v1/agents/${agentId}`, data)
    },

    // 删除Agent
    async deleteAgent(agentId: string): Promise<void> {
        return apiClient.delete(`/api/v1/agents/${agentId}`)
    }
}

export default agentApi
