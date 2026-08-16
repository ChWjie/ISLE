<template>
  <div class="s5-battle-page">
    <!-- Config Overlay -->
     <GameConfig
         v-model:visible="showConfig"
         :initialPlanId="initialPlanId"
         @start-game="onConfigStart"
       />

    <!-- 1. Top HUD -->
    <header class="battle-hud">
      <div class="hud-left">
        <el-button @click="showConfig = true" link class="back-btn">
           <el-icon><Setting /></el-icon>
        </el-button>
        <h1 class="page-title">ͥģ / COURT SIMULATION</h1>
      </div>
      <div class="hud-right">
         <el-button type="primary" class="new-round-btn" @click="executeNextRound" :disabled="roundLoading || gameStatus === 'completed'">
            <span v-if="!roundLoading">
               һ (NEXT ROUND) <el-icon><Right /></el-icon>
            </span>
            <span v-else>
               ݽ... <el-icon class="is-loading"><Loading /></el-icon>
            </span>
         </el-button>
      </div>
    </header>

    <!-- 2. Main 3-Column Layout -->
    <div class="battle-layout">

       <!-- LEFT: Our Agent Panel -->
       <aside class="col-side our-side">
          <div class="panel-header">
             <div class="ph-title">ҷ (Blue Team)</div>
             <div class="ph-sub">ִ壬ܹԼ</div>
          </div>

          <div class="our-agent-list" v-if="ourAgents.length > 0">
             <div class="agent-status-card" v-for="agent in ourAgents" :key="agent.agent_id || agent.name">
                <div class="avatar-row">
                   <el-avatar :size="48" shape="square" :src="agent.avatar || 'https://api.dicebear.com/7.x/notionists/svg?seed=' + (agent.name || 'blue-agent')">B</el-avatar>
                   <div class="agent-meta">
                      <div class="name">{{ agent.name || 'ҷʦ' }}</div>
                      <div class="status-badge running" v-if="activeOurAgent?.agent_id === agent.agent_id && currentAgentAction === 'blue'">SPEAKING</div>
                      <div class="status-badge active" v-else-if="activeOurAgent?.agent_id === agent.agent_id">ACTIVE</div>
                      <div class="status-badge" v-else>IDLE</div>
                   </div>
                </div>
                <div class="duty-text">
                   <div style="font-weight:bold; margin-bottom:4px; color:#E2E8F0">ʹ:</div>
                   {{ agent.mission || 'ƶж·' }}
                </div>
             </div>
          </div>
          <div class="empty-agent" v-else>޼</div>

          <div class="stats-box">
             <div class="stat-row">
                <span class="label">֤</span>
                <el-progress :percentage="Number(agentMetrics.blue.legalReasoning.toFixed(0))" status="success" :stroke-width="6" class="stat-bar" />
             </div>
             <div class="stat-row">
                <span class="label">֤</span>
                <el-progress :percentage="Number(agentMetrics.blue.evidenceUsage.toFixed(0))" status="warning" :stroke-width="6" class="stat-bar" />
             </div>
             <div class="stat-row">
                <span class="label">ִ</span>
                <el-progress :percentage="Number(agentMetrics.blue.strategyExecution.toFixed(0))" status="success" :stroke-width="6" class="stat-bar" />
             </div>
          </div>

          <div class="action-points-panel">
             <div class="score-display">
                <div class="score-val" :class="{ 'text-green': winRate >= 80 }">{{ winRate }}%</div>
                <div class="score-label">ǰʤԤ (Win Rate)</div>
             </div>
             <div class="metrics-grid">
                <div class="m-item">
                   <span class="m-val">{{ currentRoundEvidence.pro }}</span>
                   <span class="m-lbl">Ч֤</span>
                </div>
                <div class="m-item">
                   <span class="m-val">{{ currentRoundEvidence.con }}</span>
                   <span class="m-lbl"></span>
                </div>
             </div>

             <!-- Optimization Status Overlay -->
             <div v-if="gameStatus === 'optimizing'" class="optimization-status">
                 <el-icon class="is-loading"><Loading /></el-icon> Ż...
             </div>
             <div v-else-if="gameStatus === 'completed'" class="optimization-status finished">
                 <el-button type="primary" size="small" @click="goToOptimization">
                    <el-icon><MagicStick /></el-icon> Ż
                 </el-button>
             </div>
             <div v-else class="manual-actions">
                <el-button size="small" class="cyber-btn" @click="triggerManualOptimization">ֶŻ</el-button>
                <el-button size="small" class="cyber-btn outline">ͣ</el-button>
             </div>
          </div>

          <div class="plan-info-box">
             <div class="pi-title">Ѽط ( S4)</div>
             <div class="pi-content">{{ simulationConfig?.selectedPlanId || '-' }}</div>
             <div class="pi-desc">ж·: {{ simulationConfig?.planTitle || 'ԵǰΪ׼' }}</div>
          </div>
       </aside>

       <!-- CENTER: Simulation Progress Stream -->
       <main class="col-center custom-scrollbar" ref="debateContainer">
          <div class="stream-header">ݽ // SIMULATION STREAM</div>

          <div v-if="rounds.length === 0" class="empty-state">
             <el-icon :size="40"><VideoPlay /></el-icon>
             <p>Ͻ"һ"ʼ</p>
          </div>

          <div class="message-list">
             <template v-for="(msg, idx) in messageStream" :key="idx">
                <!-- Separator -->
                <div v-if="msg.type === 'separator'" class="round-separator">
                   <div class="sep-line"></div>
                   <div class="sep-text">{{ msg.content }}</div>
                   <div class="sep-line"></div>
                </div>

                <!-- Bubble -->
                <ArgumentBubble
                   v-else
                   :side="msg.side"
                   :agentName="msg.agentName"
                   :content="msg.content"
                   :legalBasis="msg.legalBasis"
                   :risks="msg.risks"
                   :timestamp="msg.timestamp"
                />
             </template>

             <!-- Streaming Pending Bubble -->
             <div v-if="streamingBuffer.content" class="streaming-buffer-bubble">
                 <ArgumentBubble
                   :side="streamingBuffer.side"
                   :agentName="streamingBuffer.agentName"
                   :content="streamingBuffer.content"
                   timestamp="Streaming..."
                   :isStreaming="true"
                />
             </div>

             <div v-if="roundLoading && !streamingBuffer.content" class="loading-bubble">
                <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                <div class="loading-text">{{ loadingStatusText }}</div>
             </div>
          </div>
       </main>

       <!-- RIGHT: Opponent Agent Panel -->
       <aside class="col-side opp-side">
          <div class="panel-header">
             <div class="ph-title">ִ (Simulated)</div>
             <div class="ph-sub red">Դ</div>
          </div>

          <div class="agent-status-card red-theme" v-if="activeRedAgent">
             <div class="avatar-row">
                <el-avatar :size="48" shape="square" :src="activeRedAgent.avatar || 'https://api.dicebear.com/7.x/notionists/svg?seed=' + activeRedAgent.name">R</el-avatar>
                <div class="agent-meta">
                   <div class="name">{{ activeRedAgent.name || 'ʦ' }}</div>
                   <div class="status-badge active" v-if="currentAgentAction === 'red'">SPEAKING</div>
                   <div class="status-badge" v-else>WAITING</div>
                </div>
             </div>
             <div class="duty-text">
                <div style="font-weight:bold; margin-bottom:4px; color:#FCA5A5">ʹ:</div>
                {{ activeRedAgent.mission || 'ɺӦ' }}
             </div>
          </div>
          <div class="empty-agent" v-else>޼</div>

          <div class="opp-stats placeholder-box">
             <div class="stat-big-num">{{ agentMetrics.red.activityLevel }}</div>
             <div class="stat-label">ԿԾ (οָ)</div>
          </div>

          <div class="opp-params-list">
             <div class="p-row">
                <span>ɷǿ</span>
                <span class="dots gold">{{ ''.repeat(agentMetrics.red.counterIntensity) }}</span>
             </div>
             <div class="p-row">
                <span>۲</span>
                <span class="dots red">{{ ''.repeat(agentMetrics.red.publicOpinion) }}</span>
             </div>
             <div class="p-row">
                <span>֤</span>
                <span class="dots gold">{{ ''.repeat(agentMetrics.red.evidenceDispute) }}</span>
             </div>
             <div class="p-row">
               <span>ⲿ</span>
               <span class="dots green">{{ ''.repeat(agentMetrics.red.externalAction) }}</span>
            </div>
          </div>

          <div class="strategy-log custom-scrollbar">
             <div class="log-title">ַƲժҪ (̬)</div>
             <div class="log-item" v-for="(log, i) in opponentStrategyLogs" :key="i">
                <div class="log-idx">{{ i + 1 }}.</div>
                <div class="log-text">{{ log }}</div>
             </div>
          </div>
       </aside>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Setting, Right, VideoPlay, Loading, MagicStick } from '@element-plus/icons-vue'
import ArgumentBubble from './components/ArgumentBubble.vue'
import GameConfig from './components/GameConfig.vue'
import { ElMessage, ElNotification } from 'element-plus'
import simulationApi, { type RoundMessage } from '@/api/simulation'

const router = useRouter()
const route = useRoute()

const initialPlanId = computed(() => route.query.planId as string || '')

// --- State ---
const showConfig = ref(true)
const simulationConfig = ref<any>(null)
const sessionId = ref<string>('')
const eventId = ref<string>('')
const gameStatus = ref('pending') // pending, running, optimizing, completed
const roundLoading = ref(false)
const loadingStatusText = ref('')
const maxRounds = ref(10)
const rounds = ref<any[]>([])
const messageStream = ref<any[]>([])

// Streaming Buffer
const streamingBuffer = reactive({
    side: 'our' as 'our' | 'opponent' | 'judge',
    agentName: '',
    content: ''
})
const currentAgentAction = ref<'blue' | 'red' | 'judge' | null>(null)

// Simulation Metrics
const winRate = ref(50)
const currentRoundEvidence = ref({ pro: 0, con: 0 })

// Dynamic Agent Metrics
const agentMetrics = reactive({
    blue: {
        legalReasoning: 85,
        evidenceUsage: 70,
        strategyExecution: 90
    },
    red: {
        activityLevel: 7.2, // 0-10
        counterIntensity: 3, // 1-5 dots
        publicOpinion: 5, // 1-5 dots
        evidenceDispute: 3, // 1-5 dots
        externalAction: 1 // 1-5 dots
    }
})

// Agents Data
const ourAgents = ref<any[]>([]) // IDs
const opponentAgents = ref<any[]>([]) // IDs
const judgeAgent = ref<string>('')

// Mock display agents (In real app, fetch agent details by ID)
const activeOurAgent = computed(() => {
    if (ourAgents.value.length > 0) {
        return ourAgents.value[0]
    }
    return null
})

const activeRedAgent = computed(() => {
    if (opponentAgents.value.length > 0) {
        return opponentAgents.value[0]
    }
    return null
})

const opponentStrategyLogs = ref<string[]>([
   "Χƺ֤ͬ͡ԡϹܿھ"
])

// --- Logic ---
const onConfigStart = (config: any) => {
  console.log('Simulation Started with Config:', config)
  simulationConfig.value = config
  sessionId.value = config.simulationId
  eventId.value = config.eventId

  // Here config should pass full agent objects, or we need to look them up.
  // GameConfig emits 'start-game' with { ...form, simulationId (if added), etc }
  // Actually GameConfig only emits the API response? No, usually it emits the form payload or result.
  // Let's assume onConfigStart receives the payload + simulationId AND the agent details.
  // But wait, GameConfig.js emits `emitStart` which just calls `emit('start-game', result)`.

  // We need to inject the full agent objects into the config object passed up,
  // OR we need to fetch them here.
  // For simplicity, let's assume GameConfig was updated to include full agent objects in the emit,
  // OR we find them from the ID if we had a global store.
  // Since we don't have a global store here, let's just use the partial data we have
  // and maybe rely on the fact that GameConfig has the data.

  // BEST FIX: GameConfig should pass the full agent objects.
  // But since I can't easily edit the emit payload in the previous step (I only edited UI),
  // I will make index.vue capable of displaying what it has.
  // ACTUALLY, config.blueAgents is just IDs.
  // I should update `onConfigStart` to fetch agent details if needed,
  // OR update GameConfig to emit full objects.
  // Let's update index.vue to fetch agent details by ID.

  // For now, let's trust that we can fetch or we passed them.
  // Wait, `GameConfig` emits whatever `emitStart` passes.
  // I will update GameConfig to pass `agentObjects` map.

  // But first, let's update this file to use `config.agentObjects` if available.

  if (config.agentObjects) {
      ourAgents.value = config.blueAgents.map((id: string) => config.agentObjects[id]).filter(Boolean)
      opponentAgents.value = config.redAgents.map((id: string) => config.agentObjects[id]).filter(Boolean)
  } else {
      // Fallback
       ourAgents.value = config.blueAgents.map((id: string) => ({ name: id, detailedConfig: {} }))
       opponentAgents.value = config.redAgents.map((id: string) => ({ name: id, detailedConfig: {} }))
  }

  judgeAgent.value = config.judgeAgent
  maxRounds.value = config.maxRounds || 10
  opponentStrategyLogs.value = ['ϵͳڵǰ¼ʵ̬ɶַƹ۵']

  // Reset State
  rounds.value = []
  messageStream.value = []
  winRate.value = 50
  gameStatus.value = 'running'
  showConfig.value = false

  ElMessage.success('Battle Environment Initialized')
}

// Previous round arguments context
const previousArgs = reactive({
    blue: '',
    red: ''
})

const executeNextRound = async () => {
   if (gameStatus.value !== 'running') return
   if (!sessionId.value) {
     ElMessage.error('No active simulation session. Please configure and start first.')
     return
   }

   roundLoading.value = true
   const roundNum = rounds.value.length + 1

   // Add Round Separator
   messageStream.value.push({
      type: 'separator',
      content: `ROUND ${roundNum}`,
      timestamp: new Date().toLocaleTimeString()
   })
   scrollToBottom()

   // Reset Streaming Buffer
   streamingBuffer.content = ''

   try {
     await simulationApi.executeRoundStream(
        sessionId.value,
        roundNum,
        eventId.value,
        ourAgents.value.map(a => a.agent_id),
        opponentAgents.value.map(a => a.agent_id),
        judgeAgent.value,
        { blue: previousArgs.blue, red: previousArgs.red },
        (msg: RoundMessage) => {
            handleStreamMessage(msg)
        }
     )

     // Round Completed Logic (handled in handleStreamMessage 'round_complete')

   } catch (error: any) {
     console.error('Round execution failed:', error)
     ElMessage.error('ִʧ: ' + error.message)
     roundLoading.value = false
     currentAgentAction.value = null
   }
}

const handleStreamMessage = (msg: RoundMessage) => {
    scrollToBottom()

    switch (msg.type) {
        case 'status':
            loadingStatusText.value = msg.message || 'Thinking...'
            if (msg.agent === 'blue') currentAgentAction.value = 'blue'
            else if (msg.agent === 'red') currentAgentAction.value = 'red'
            else if (msg.agent === 'judge') currentAgentAction.value = 'judge'
            break

        case 'blue_argument':
            if (!streamingBuffer.content && msg.chunk) {
                // Start streaming blue
                streamingBuffer.side = 'our'
                streamingBuffer.agentName = activeOurAgent.value?.name || 'ҷ'
            }
            if (msg.chunk) streamingBuffer.content += msg.chunk
            break

        case 'blue_complete':
            // Finalize Blue
            addMessage('our', activeOurAgent.value?.name || 'ҷ', streamingBuffer.content || msg.argument || '')
            previousArgs.blue = streamingBuffer.content || msg.argument || ''
            streamingBuffer.content = '' // Clear
            break

        case 'red_argument':
            if (!streamingBuffer.content && msg.chunk) {
                 // Start streaming red
                streamingBuffer.side = 'opponent'
                streamingBuffer.agentName = activeRedAgent.value.name
            }
            if (msg.chunk) streamingBuffer.content += msg.chunk
            break

        case 'red_complete':
             // Finalize Red
            addMessage('opponent', activeRedAgent.value.name, streamingBuffer.content || msg.argument || '')
            previousArgs.red = streamingBuffer.content || msg.argument || ''
            streamingBuffer.content = '' // Clear
            break

        case 'judge_comment':
            if (!streamingBuffer.content && msg.chunk) {
                 // Start streaming judge
                streamingBuffer.side = 'judge'
                streamingBuffer.agentName = '󷨹'
            }
            if (msg.chunk) streamingBuffer.content += msg.chunk
            break

        case 'judge_complete':
            // Finalize Judge
             addMessage('judge', '󷨹', streamingBuffer.content || msg.comment || '')
             streamingBuffer.content = '' // Clear
             if (msg.win_rate) winRate.value = msg.win_rate
             break

        case 'round_complete':
            roundLoading.value = false
            currentAgentAction.value = null
            rounds.value.push(msg.round)

            // Check max rounds
            if (rounds.value.length >= maxRounds.value) {
                handleSimulationEnd({ status: 'completed', final_result: { termination_reason: 'ﵽغ' } })
            }
            break

        case 'error':
            ElMessage.error(msg.error || 'Unknown Error')
            roundLoading.value = false
            currentAgentAction.value = null
            break

        case 'termination':
            roundLoading.value = false
            currentAgentAction.value = null
            handleSimulationEnd({
                status: 'completed',
                final_result: {
                    termination_reason: msg.reason,
                    final_win_rate: msg.final_win_rate,
                    total_rounds: msg.total_rounds
                }
            })
            break

        case 'optimization_update':
            // Show Optimization Feedback
            if (msg.data && msg.data.evidence && msg.data.evidence.length > 0) {
               const isPositive = msg.data.impact === 'positive'
               ElNotification({
                 title: isPositive ? 'Ż' : 'Ԥ',
                 message: `ؼ֤ [${msg.data.evidence.join(', ')}] ʤʲ ${msg.data.delta > 0 ? '+' : ''}${msg.data.delta.toFixed(1)}% Ӱ`,
                 type: isPositive ? 'success' : 'warning',
                 duration: 5000,
                 position: 'bottom-right'
               })
            }
            break
    }
}

const handleSimulationEnd = (simStatus: any) => {
  gameStatus.value = simStatus.status

  if (simStatus.status === 'completed') {
    ElNotification({
      title: '',
      message: simStatus.final_result?.termination_reason || 'ѽ',
      type: 'success',
      duration: 5000
    })

    messageStream.value.push({
      type: 'separator',
      content: `SIMULATION COMPLETED - ${simStatus.final_result?.termination_reason || 'DONE'}`,
    })
    scrollToBottom()
  }
}

const triggerManualOptimization = () => {
    ElMessage.info('ֶŻܿ...')
}

const addMessage = (side: 'our'|'opponent'|'judge', name: string, content: string, basis?: string[], risks?: string[]) => {
   messageStream.value.push({
      type: 'message',
      side,
      agentName: name,
      content,
      legalBasis: basis,
      risks,
      timestamp: new Date().toLocaleTimeString()
   })
}

const debateContainer = ref<HTMLElement | null>(null)
const goToOptimization = () => {
    if (!sessionId.value) {
        ElMessage.error('޷ȡЧID')
        return
    }
    router.push(`/simulation/optimization/${sessionId.value}`)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (debateContainer.value) {
        debateContainer.value.scrollTo({
            top: debateContainer.value.scrollHeight,
            behavior: 'smooth'
        })
    }
  })
}
</script>

<style scoped>
.s5-battle-page {
  height: 100vh; display: flex; flex-direction: column;
  background: #020617; color: #fff; font-family: 'Inter', sans-serif;
  overflow: hidden;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* HUD */
.battle-hud {
  height: 60px; background: rgba(15, 23, 42, 0.9); border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex; justify-content: space-between; align-items: center; padding: 0 24px;
}
.hud-left { display: flex; align-items: center; gap: 20px; }
.back-btn { color: #94A3B8; }
.page-title { font-size: 16px; font-weight: 700; color: #fff; margin: 0; }
.new-round-btn {
   background: #3B82F6; border: none; font-weight: bold; padding: 10px 20px;
   box-shadow: 0 0 15px rgba(59, 130, 246, 0.4);
}

/* Layout */
.battle-layout {
  flex: 1; display: grid; grid-template-columns: 320px 1fr 340px; overflow: hidden;
}

/* Col Common */
.col-side { background: rgba(20, 30, 50, 0.5); border-right: 1px solid rgba(255,255,255,0.05); padding: 16px; display: flex; flex-direction: column; gap: 16px; }
.col-center { background: #0F172A; position: relative; display: flex; flex-direction: column; padding: 20px; gap: 20px; overflow-y: auto; }
.opp-side { border-right: none; border-left: 1px solid rgba(255,255,255,0.05); }

/* Sidebars Panel */
.panel-header { margin-bottom: 10px; }
.ph-title { font-size: 14px; font-weight: 700; color: #E2E8F0; }
.ph-sub { font-size: 11px; color: #64748B; margin-top: 4px; }
.ph-sub.red { color: #FCA5A5; }

/* Agent Card Small */
.agent-status-card {
   background: rgba(59, 130, 246, 0.1); border: 1px solid rgba(59, 130, 246, 0.3);
   padding: 12px; border-radius: 6px;
}
.agent-status-card.red-theme {
   background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3);
}
.avatar-row { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; }
.agent-meta .name { font-weight: bold; font-size: 14px; }
.status-badge {
   font-size: 10px; background: #10B981; padding: 1px 6px; border-radius: 2px;
   display: inline-block; margin-top: 4px; font-weight: bold;
}
.status-badge.running { background: #3B82F6; }
.status-badge.active { background: #F59E0B; color: #000; }
.duty-text { font-size: 11px; color: #94A3B8; line-height: 1.4; }

/* Stats Bar */
.stats-box { background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; }
.stat-row { margin-bottom: 10px; }
.stat-row:last-child { margin-bottom: 0; }
.stat-row .label { font-size: 11px; color: #94A3B8; display: block; margin-bottom: 4px; }
.stat-bar :deep(.el-progress-bar__outer) { background-color: rgba(255,255,255,0.1); }

/* Action Points Panel */
.action-points-panel { background: rgba(0,0,0,0.2); padding: 12px; border-radius: 6px; }
.score-display { text-align: center; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; }
.score-val { font-size: 28px; font-weight: 700; color: #fff; }
.score-label { font-size: 10px; color: #64748B; }
.metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
.m-item { text-align: center; background: rgba(255,255,255,0.03); padding: 6px; border-radius: 4px; }
.m-val { display: block; font-weight: bold; font-size: 12px; }
.m-lbl { font-size: 10px; color: #64748B; }
.manual-actions { display: flex; gap: 10px; }
.cyber-btn { flex: 1; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; }
.cyber-btn.outline { background: transparent; }

/* Plan Info */
.plan-info-box { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 6px; font-size: 12px; margin-top: auto; }
.pi-title { color: #64748B; margin-bottom: 4px; }
.pi-content { color: #60A5FA; font-weight: bold; margin-bottom: 4px; font-family: monospace; }
.pi-desc { color: #94A3B8; }

/* Opponent Specific */
.opp-stats { text-align: center; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 6px; }
.stat-big-num { font-size: 32px; font-weight: 900; color: #F59E0B; }
.stat-label { font-size: 11px; color: #64748B; }
.opp-params-list { padding: 12px; }
.p-row { display: flex; justify-content: space-between; font-size: 12px; color: #94A3B8; margin-bottom: 8px; }
.dots { letter-spacing: 2px; font-size: 10px; }
.dots.red { color: #EF4444; }
.dots.gold { color: #F59E0B; }
.dots.green { color: #10B981; }

.strategy-log { flex: 1; background: rgba(0,0,0,0.3); border-radius: 6px; padding: 12px; overflow-y: auto; font-size: 11px; }
.log-title { color: #64748B; margin-bottom: 8px; }
.log-item { display: flex; gap: 6px; margin-bottom: 8px; color: #E2E8F0; }
.log-idx { color: #F59E0B; }

/* Center Stream */
.stream-header { font-size: 12px; color: #64748B; margin-bottom: 20px; letter-spacing: 1px; font-weight: bold; }

.round-separator {
   display: flex; align-items: center; gap: 12px; margin: 24px 0; color: #3B82F6; font-family: 'Orbitron';
}
.sep-line { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent); }
.sep-text { font-size: 12px; font-weight: bold; letter-spacing: 2px; }

.message-list { flex: 1; display: flex; flex-direction: column; padding-bottom: 40px; }
.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #334155; }
.loading-bubble { text-align: center; color: #3B82F6; margin-top: 10px; display: flex; flex-direction: column; align-items: center;}
.loading-text { font-size: 12px; color: #64748B; margin-top: 4px; }
.dot { display: inline-block; width: 6px; height: 6px; background: #3B82F6; border-radius: 50%; margin: 0 4px; animation: bounce 1s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }

/* Streaming Buffer */
.streaming-buffer-bubble {
    opacity: 0.8;
}

/* Scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.2); border-radius: 2px; }
/* Optimization UI */
.optimization-status {
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.4);
    color: #3B82F6;
    padding: 10px;
    border-radius: 4px;
    text-align: center;
    font-size: 13px;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    animation: pulse 2s infinite;
}
.optimization-status.finished {
    background: rgba(16, 185, 129, 0.2);
    border-color: rgba(16, 185, 129, 0.4);
    color: #34D399;
    animation: none;
}
.text-green { color: #34D399 !important; }

@keyframes pulse {
    0% { opacity: 0.8; }
    50% { opacity: 1; }
    100% { opacity: 0.8; }
}
</style>
