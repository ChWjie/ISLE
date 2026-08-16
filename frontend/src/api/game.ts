import request from './request'

export interface AgentConfig {
    llm_model?: string
    temperature?: number
    custom_prompt?: string
    max_tokens?: number
}

export const gameApi = {
    // 开始游戏
    startGame: (data: {
        event_id: string
        plan_id: string
        max_rounds?: number
        our_agent_config?: AgentConfig
        opponent_agent_config?: AgentConfig
    }) => request.post('/api/v1/game/start', data),

    // 执行一轮
    executeRound: (sessionId: string) =>
        request.post(`/api/v1/game/${sessionId}/round`),

    // 获取游戏会话
    getSession: (sessionId: string) =>
        request.get(`/api/v1/game/${sessionId}`),

    // 获取结果
    getResult: (sessionId: string) =>
        request.get(`/api/v1/game/${sessionId}/result`)
}
