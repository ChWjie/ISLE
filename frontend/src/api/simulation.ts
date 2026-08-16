/**
 * Simulation API Service - 前端调用
 */
import { repairMojibakeDeep } from './text'
import { apiUrl } from './config'

export interface RoundMessage {
    type: 'status' | 'retrieval' | 'blue_argument' | 'blue_complete' | 'red_argument' | 'red_complete' | 'judge_comment' | 'judge_complete' | 'round_complete' | 'termination' | 'optimization_update' | 'error'
    agent?: string
    phase?: 'start' | 'complete'
    message?: string
    chunk?: string
    argument?: string
    comment?: string
    win_rate?: number
    round?: number
    query?: string
    enabled?: boolean
    degraded?: boolean
    source_map?: string[]
    blue_argument?: string
    red_argument?: string
    judge_comment?: string
    error?: string
    // Termination fields
    reason?: string
    final_win_rate?: number
    total_rounds?: number
    // Optimization fields
    data?: {
        evidence: string[]
        impact: 'positive' | 'negative'
        delta: number
    }
}

const simulationApi = {
    /**
     * 启动推演
     */
    async startSimulation(data: {
        event_id: string
        plan_id: string
        blue_agent_ids: string[]
        red_agent_ids: string[]
        judge_agent_id: string
        max_rounds?: number
        target_win_rate?: number
    }): Promise<{ simulation_id: string; status: string; message: string }> {
        const response = await fetch(apiUrl('/api/v1/simulation/start'), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })

        if (!response.ok) {
            throw new Error(`Failed to start simulation: ${response.statusText}`)
        }

        return repairMojibakeDeep(await response.json())
    },

    /**
     * 执行一轮推演（Stream）
     */
    async executeRoundStream(
        simulationId: string,
        roundNum: number,
        eventId: string,
        blueAgents: string[],
        redAgents: string[],
        judgeAgent: string,
        previousArguments: { blue?: string; red?: string } | null,
        onMessage: (message: RoundMessage) => void
    ): Promise<void> {
        // Updated to use POST body for all arguments to avoid 422 errors and URL length limits
        const response = await fetch(apiUrl(`/api/v1/simulation/round/${simulationId}`), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                round_num: roundNum,
                event_id: eventId,
                blue_agents: blueAgents,
                red_agents: redAgents,
                judge_agent: judgeAgent,
                previous_arguments: previousArguments
            })
        })

        if (!response.ok) {
            throw new Error(`Failed to execute round: ${response.statusText}`)
        }

        if (!response.body) {
            throw new Error('No response body')
        }

        // 读取Stream
        const reader = response.body.getReader()
        const decoder = new TextDecoder()

        try {
            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const text = decoder.decode(value, { stream: true })
                const lines = text.split('\n').filter(line => line.trim())

                for (const line of lines) {
                    try {
                        const message = repairMojibakeDeep(JSON.parse(line)) as RoundMessage
                        onMessage(message)
                    } catch (e) {
                        console.error('Failed to parse message:', line, e)
                    }
                }
            }
        } finally {
            reader.releaseLock()
        }
    },

    /**
     * 获取推演状态
     */
    async getStatus(simulationId: string): Promise<{
        simulation_id: string
        status: string
        current_round: number
        max_rounds: number
        win_rate: number
    }> {
        const response = await fetch(apiUrl(`/api/v1/simulation/status/${simulationId}`))

        if (!response.ok) {
            throw new Error(`Failed to get status: ${response.statusText}`)
        }

        return repairMojibakeDeep(await response.json())
    },

    /**
     * 生成优化方案
     */
    async optimizePlan(simulationId: string): Promise<{
        original_plan: string
        optimized_plan: string
        changes_summary: string
        event_id?: string
    }> {
        const response = await fetch(apiUrl(`/api/v1/simulation/optimize/${simulationId}`), {
            method: 'POST'
        })

        if (!response.ok) {
            throw new Error(`Failed to optimize plan: ${response.statusText}`)
        }

        return repairMojibakeDeep(await response.json())
    }
}

export default simulationApi
