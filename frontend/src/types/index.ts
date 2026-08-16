// ==================== 事件相关类型 ====================

// ==================== 事件相关类型 ====================

export const EventType = {
    TERRITORY: 'territory',      // 领土主权
    MARITIME: 'maritime',         // 海洋权益
    DIPLOMATIC: 'diplomatic',     // 外交摩擦
    MILITARY: 'military',         // 军事安全
    ECONOMIC: 'economic',         // 经济贸易
} as const
export type EventType = typeof EventType[keyof typeof EventType]

export const EventStatus = {
    PENDING: 'pending',           // 待处理
    ANALYZING: 'analyzing',       // 分析中
    GAMING: 'gaming',             // 博弈中
    COMPLETED: 'completed',       // 已完成
    ARCHIVED: 'archived',         // 已归档
} as const
export type EventStatus = typeof EventStatus[keyof typeof EventStatus]

export interface DisputeEvent {
    id: string
    title: string
    type: EventType
    description: string
    location: { lat: number; lng: number }
    location_name?: string
    parties: string[]
    status: EventStatus
    severity: number
    created_at: string
    updated_at: string
    // Optional UI fields for S1 dashboard
    riskLevel?: 'high' | 'medium' | 'low'
    tags?: string[]
    // Optional backend fields
    event_id?: string
    name?: string
    dispute_type?: string
    our_side?: string[]
    opponent_side?: string[]
    legal_systems?: string[]
    fact_summary?: string
    imageUrl?: string  // 事件配图 URL 1
    imageUrl2?: string // 事件配图 URL 2
}

export interface EventStats {
    total: number
    by_type: Record<string, number>
    by_status: Record<string, number>
    by_severity: Record<string, number>
}

// ==================== 智能体相关类型 ====================

export interface Agent {
    id: string
    agent_id?: string
    name: string
    type: string
    role?: string
    avatar?: string
    is_expert?: boolean
    law_domains: string[]
    description?: string
    mission?: string
    responsibilities?: string
    level?: string
    knowledge_scope?: string[]
    config?: Record<string, any>
    created_at: string
}

export interface AgentConfig {
    agent_id: string
    model_config?: Record<string, any>
    tools?: string[]
    custom_prompt?: string
}

export interface AgentAnalysisRequest {
    event_id: string
    agent_configs: AgentConfig[]
}

export interface AgentAnalysisResult {
    agent_id: string
    agent_name: string
    analysis: string
    legal_basis: string[]
    recommendations: string[]
    confidence: number
}

// ==================== 博弈相关类型 ====================

export const GameStatus = {
    PENDING: 'pending',
    RUNNING: 'running',
    PAUSED: 'paused',
    COMPLETED: 'completed',
    FAILED: 'failed',
} as const
export type GameStatus = typeof GameStatus[keyof typeof GameStatus]

export const RuleType = {
    PERMISSION: 'permission',      // 行动许可规则
    RISK: 'risk',                  // 风险触发规则
    PREMISE: 'premise',            // 前提失效规则
    TERMINATION: 'termination',    // 终止与回退规则
} as const
export type RuleType = typeof RuleType[keyof typeof RuleType]

export interface GameRule {
    type: RuleType
    condition: string
    action: string
    priority?: number
}

export interface GameRound {
    round: number
    our_action: string
    their_action: string
    risks: string[]
    state: Record<string, any>
    timestamp?: string
}

export interface GameStartRequest {
    event_id: string
    plan_id: string
    rules: GameRule[]
    max_rounds?: number
}

export interface GameSession {
    id: string
    event_id: string
    plan_id: string
    status: GameStatus
    current_round: number
    max_rounds: number
    rounds: GameRound[]
    created_at: string
}

export interface GameResult {
    session_id: string
    total_rounds: number
    outcome: 'success' | 'failure' | 'uncertain'
    risk_score: number
    recommendations: string[]
    summary: string
}

// ==================== 法律相关类型 ====================

export interface LawSystem {
    id: string
    name: string
    category: string
    description: string
}

export interface LawDocument {
    id: string
    system: string
    title: string
    content: string
    relevance?: number
}

// ==================== 方案相关类型 ====================

export interface Plan {
    id: string
    event_id: string
    title: string
    content: string
    analysis_results: any[]
    status: 'draft' | 'pending_approval' | 'approved' | 'deployed'
    created_at: string
    updated_at: string
}
