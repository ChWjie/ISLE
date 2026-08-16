import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { DisputeEvent, AgentConfig } from '@/types'

export const useGameStore = defineStore('game', () => {
    // 当前处理的事件
    const currentEvent = ref<DisputeEvent | null>(null)

    // S3: 选中的智能体配置
    const selectedAgents = ref<AgentConfig[]>([])

    // S4: 生成的方案ID
    const currentPlanId = ref<string | null>(null)

    // S5: 当前博弈会话ID
    const currentSessionId = ref<string | null>(null)

    // Actions
    function setEvent(event: DisputeEvent) {
        currentEvent.value = event
    }

    function setAgents(agents: AgentConfig[]) {
        selectedAgents.value = agents
    }

    function setPlanId(id: string) {
        currentPlanId.value = id
    }

    function setSessionId(id: string) {
        currentSessionId.value = id
    }

    function resetGame() {
        selectedAgents.value = []
        currentPlanId.value = null
        currentSessionId.value = null
    }

    return {
        currentEvent,
        selectedAgents,
        currentPlanId,
        currentSessionId,
        setEvent,
        setAgents,
        setPlanId,
        setSessionId,
        resetGame
    }
})
