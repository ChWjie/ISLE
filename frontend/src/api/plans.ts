/**
 * Plans API Service - 鏂规鐢熸垚
 */
import apiClient from './client'
import { repairMojibakeDeep } from './text'
import { apiUrl } from './config'

export interface AgentAnalysisMessage {
    type: 'status' | 'retrieval' | 'content' | 'complete' | 'error'
    agent_id: string
    agent_name?: string
    status?: 'pending' | 'running' | 'completed' | 'error'
    enabled?: boolean
    phase?: 'start' | 'complete'
    query?: string
    reason?: string
    degraded?: boolean
    retrieval_types?: string[]
    case_count?: number
    law_count?: number
    source_map?: string[]
    chunk?: string
    analysis?: string
    error?: string
}

export interface IntegrateMessage {
    type: 'start' | 'section_start' | 'content' | 'section_complete' | 'complete' | 'error'
    section?: string
    index?: number
    chunk?: string
    content?: string
    message?: string
    error?: string
}

export interface Plan {
    plan_id: string
    title: string
    content: string
    created_at?: string
    event_id?: string
    event?: any
    status?: string
}

async function readJsonLineStream<T>(
    body: ReadableStream<Uint8Array>,
    onMessage: (message: T) => void
): Promise<void> {
    const reader = body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    const handleLine = (rawLine: string, label: string) => {
        const line = rawLine.trim()
        if (!line) return
        try {
            onMessage(repairMojibakeDeep(JSON.parse(line)) as T)
        } catch (e) {
            console.error(label, line, e)
        }
    }

    try {
        while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''

            for (const line of lines) {
                handleLine(line, 'Failed to parse message:')
            }
        }

        buffer += decoder.decode()
        handleLine(buffer, 'Failed to parse trailing message:')
    } finally {
        reader.releaseLock()
    }
}

const plansApi = {
    /**
     * 鐢熸垚娉曞緥鍒嗘瀽鏂规锛圫tream锛?     * @param eventId 浜嬩欢ID
     * @param agentIds 鏅鸿兘浣揑D鍒楄〃
     * @param onMessage Stream娑堟伅鍥炶皟
     */
    async generatePlanStream(
        eventId: string,
        agentIds: string[],
        onMessage: (message: AgentAnalysisMessage) => void
    ): Promise<void> {
        const response = await fetch(apiUrl('/api/v1/plans/generate'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event_id: eventId,
                agent_ids: agentIds
            })
        })

        if (!response.ok) {
            throw new Error(`Failed to generate plan: ${response.statusText}`)
        }

        if (!response.body) {
            throw new Error('No response body')
        }

        await readJsonLineStream<AgentAnalysisMessage>(response.body, onMessage)
    },

    /**
     * 鏁村悎鍚勬櫤鑳戒綋鍒嗘瀽鐢熸垚缁煎悎鏂规锛圫tream锛?     */
    async integratePlanStream(
        eventId: string,
        agentAnalyses: Array<{ agent_name: string, agent_type: string, analysis: string }>,
        onMessage: (message: IntegrateMessage) => void
    ): Promise<void> {
        const response = await fetch(apiUrl('/api/v1/plans/integrate'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                event_id: eventId,
                agent_analyses: agentAnalyses
            })
        })

        if (!response.ok) {
            throw new Error(`Failed to integrate plan: ${response.statusText}`)
        }

        if (!response.body) {
            throw new Error('No response body')
        }

        await readJsonLineStream<IntegrateMessage>(response.body, onMessage)
    },

    /**
     * 淇濆瓨鐢熸垚鐨勬柟妗?     */
    async savePlan(data: {
        event_id: string
        title: string
        content: string
        action_paths?: any[]
    }): Promise<{ plan_id: string, message: string }> {
        const response = await fetch(apiUrl('/api/v1/plans/save'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) {
            throw new Error(`Failed to save plan: ${response.statusText}`)
        }

        return repairMojibakeDeep(await response.json())
    },

    // 鑾峰彇鏂规鍒楄〃 (Adding missing method)
    async listPlans(params?: { event_id?: number }): Promise<any[]> {
        const data = await apiClient.get('/api/v1/plans', { params })
        return Array.isArray(data) ? data : []
    }
}

export default plansApi
