<template>
  <div class="s5-battle-page">
    <div class="bg-grid"></div>
    <div class="bg-glow bg-glow-left"></div>
    <div class="bg-glow bg-glow-right"></div>

    <GameConfig v-model:visible="showConfig" :initialPlanId="initialPlanId" @start-game="onConfigStart" />

    <header class="battle-hud">
      <div class="hud-left">
        <el-button @click="showConfig = true" link class="back-btn">
          <el-icon><Setting /></el-icon>
          推演配置
        </el-button>
        <h1 class="page-title">多智能体法律博弈推演 / COURT SIMULATION</h1>
      </div>
      <div class="hud-right">
        <el-button type="primary" class="new-round-btn" @click="executeNextRound" :disabled="roundLoading || gameStatus === 'completed'">
          <span v-if="!roundLoading">下一轮推演 <el-icon><Right /></el-icon></span>
          <span v-else>推演进行中 <el-icon class="is-loading"><Loading /></el-icon></span>
        </el-button>
      </div>
    </header>

    <div class="scenario-banner">
      <div class="banner-item">
        <span class="banner-label">关联事件</span>
        <span class="banner-value">{{ simulationConfig?.plan?.event?.name || simulationConfig?.plan?.event_name || '尚未启动推演' }}</span>
      </div>
      <div class="banner-item">
        <span class="banner-label">当前方案</span>
        <span class="banner-value mono">{{ simulationConfig?.selectedPlanId || '-' }}</span>
      </div>
      <div class="banner-item">
        <span class="banner-label">推演状态</span>
        <span class="banner-value">{{ statusLabel }}</span>
      </div>
      <div class="banner-item" v-if="lastRetrievalText">
        <span class="banner-label">当前阶段</span>
        <span class="banner-value retrieval">{{ lastRetrievalText }}</span>
      </div>
    </div>

    <div class="battle-layout">
      <aside class="col-side our-side">
        <div class="panel-header">
          <div class="ph-title">我方律师团</div>
          <div class="ph-sub">负责法律论证、证据组织与策略执行</div>
        </div>

        <div class="our-agent-list" v-if="ourAgents.length > 0">
          <div class="agent-status-card" v-for="agent in ourAgents" :key="agent.agent_id || agent.name">
            <div class="avatar-row">
              <el-avatar :size="48" shape="square" :src="agent.avatar || `https://api.dicebear.com/7.x/notionists/svg?seed=${agent.name || 'blue-agent'}`">B</el-avatar>
              <div class="agent-meta">
                <div class="name">{{ agent.name || '我方律师' }}</div>
                <div class="status-badge running" v-if="activeOurAgent?.agent_id === agent.agent_id && currentAgentAction === 'blue'">发言中</div>
                <div class="status-badge active" v-else-if="activeOurAgent?.agent_id === agent.agent_id">激活</div>
                <div class="status-badge" v-else>待命</div>
              </div>
            </div>
            <div class="duty-text">
              <div class="duty-title">核心任务</div>
              {{ agent.mission || '围绕当前方案完成论证、回应和证据组织。' }}
            </div>
          </div>
        </div>
        <div class="empty-agent" v-else>暂无已选我方智能体</div>

        <div class="stats-box">
          <div class="stat-row">
            <span class="label">法律论证</span>
            <el-progress :percentage="Number(agentMetrics.blue.legalReasoning.toFixed(0))" status="success" :stroke-width="6" class="stat-bar" />
          </div>
          <div class="stat-row">
            <span class="label">证据运用</span>
            <el-progress :percentage="Number(agentMetrics.blue.evidenceUsage.toFixed(0))" status="warning" :stroke-width="6" class="stat-bar" />
          </div>
          <div class="stat-row">
            <span class="label">策略执行</span>
            <el-progress :percentage="Number(agentMetrics.blue.strategyExecution.toFixed(0))" status="success" :stroke-width="6" class="stat-bar" />
          </div>
        </div>

        <div class="action-points-panel">
          <div class="score-display">
            <div class="score-val" :class="{ 'text-green': winRate >= 80 }">{{ winRate }}%</div>
            <div class="score-label">当前胜率预测</div>
          </div>
          <div class="metrics-grid">
            <div class="m-item">
              <span class="m-val">{{ currentRoundEvidence.pro }}</span>
              <span class="m-lbl">有效证据</span>
            </div>
            <div class="m-item">
              <span class="m-val">{{ currentRoundEvidence.con }}</span>
              <span class="m-lbl">争议证据</span>
            </div>
          </div>
          <div v-if="gameStatus === 'optimizing'" class="optimization-status">
            <el-icon class="is-loading"><Loading /></el-icon>
            正在生成优化建议...
          </div>
          <div v-else-if="gameStatus === 'completed'" class="optimization-status finished">
            <el-button type="primary" size="small" @click="goToOptimization">
              <el-icon><MagicStick /></el-icon>
              查看优化方案
            </el-button>
          </div>
          <div v-else class="manual-actions">
            <el-button size="small" class="cyber-btn" @click="triggerManualOptimization">手动优化</el-button>
            <el-button size="small" class="cyber-btn outline" @click="showConfig = true">调整配置</el-button>
          </div>
        </div>

        <div class="plan-info-box">
          <div class="pi-title">当前方案（来自 S4）</div>
          <div class="pi-content">{{ simulationConfig?.selectedPlanId || '-' }}</div>
          <div class="pi-desc">方案标题：{{ simulationConfig?.planTitle || '以当前已导入方案为准' }}</div>
        </div>
      </aside>

      <main class="col-center custom-scrollbar" ref="debateContainer">
        <div class="center-top">
          <div class="stream-header">推演过程 / SIMULATION STREAM</div>
          <div class="retrieval-banner" v-if="lastRetrievalText">
            <el-icon><Search /></el-icon>
            {{ lastRetrievalText }}
          </div>
        </div>

        <div v-if="rounds.length === 0 && !roundLoading" class="empty-state">
          <el-icon :size="40"><VideoPlay /></el-icon>
          <p>请点击右上角“下一轮推演”开始生成完整博弈过程。</p>
        </div>

        <div class="message-list">
          <template v-for="(msg, idx) in messageStream" :key="idx">
            <div v-if="msg.type === 'separator'" class="round-separator">
              <div class="sep-line"></div>
              <div class="sep-text">{{ msg.content }}</div>
              <div class="sep-line"></div>
            </div>

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

          <div v-if="streamingBuffer.content" class="streaming-buffer-bubble">
            <ArgumentBubble
              :side="streamingBuffer.side"
              :agentName="streamingBuffer.agentName"
              :content="streamingBuffer.content"
              timestamp="生成中..."
              :isStreaming="true"
            />
          </div>

          <div v-if="roundLoading && !streamingBuffer.content" class="loading-bubble">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
            <div class="loading-text">{{ loadingStatusText || '正在请求模型生成...' }}</div>
          </div>
        </div>
      </main>

      <aside class="col-side opp-side">
        <div class="panel-header">
          <div class="ph-title">对方 / 裁判视角</div>
          <div class="ph-sub red">模拟对手观点、外部压力与裁判反馈</div>
        </div>

        <div class="our-agent-list" v-if="opponentAgents.length > 0">
          <div class="agent-status-card red-theme" v-for="agent in opponentAgents" :key="agent.agent_id || agent.name">
            <div class="avatar-row">
              <el-avatar :size="48" shape="square" :src="agent.avatar || `https://api.dicebear.com/7.x/notionists/svg?seed=${agent.name}`">R</el-avatar>
              <div class="agent-meta">
                <div class="name">{{ agent.name || '对方代理' }}</div>
                <div class="status-badge active" v-if="currentAgentAction === 'red' && activeRedAgent?.agent_id === agent.agent_id">发言中</div>
                <div class="status-badge" v-else>待命</div>
              </div>
            </div>
            <div class="duty-text">
              <div class="duty-title red">核心任务</div>
              {{ agent.mission || '生成具有对抗性的回应、抗辩和质疑意见。' }}
            </div>
          </div>
        </div>
        <div class="empty-agent" v-else>暂无已选对方智能体</div>

        <div class="opp-stats placeholder-box">
          <div class="stat-big-num">{{ agentMetrics.red.activityLevel }}</div>
          <div class="stat-label">对抗活跃度</div>
        </div>

        <div class="opp-params-list">
          <div class="p-row"><span>反制强度</span><span class="dots gold">{{ '●'.repeat(agentMetrics.red.counterIntensity) }}</span></div>
          <div class="p-row"><span>舆情压力</span><span class="dots red">{{ '●'.repeat(agentMetrics.red.publicOpinion) }}</span></div>
          <div class="p-row"><span>证据争议</span><span class="dots gold">{{ '●'.repeat(agentMetrics.red.evidenceDispute) }}</span></div>
          <div class="p-row"><span>外部动作</span><span class="dots green">{{ '●'.repeat(agentMetrics.red.externalAction) }}</span></div>
        </div>

        <div class="strategy-log custom-scrollbar">
          <div class="log-title">对手策略摘要</div>
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
import { ref, nextTick, computed, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Setting, Right, VideoPlay, Loading, MagicStick, Search } from '@element-plus/icons-vue'
import ArgumentBubble from './components/ArgumentBubble.vue'
import GameConfig from './components/GameConfig.vue'
import { ElMessage, ElNotification } from 'element-plus'
import agentApi from '@/api/agents'
import simulationApi, { type RoundMessage } from '@/api/simulation'

const router = useRouter()
const route = useRoute()

const initialPlanId = computed(() => route.query.planId as string || '')
const showConfig = ref(true)
const simulationConfig = ref<any>(null)
const sessionId = ref<string>('')
const eventId = ref<string>('')
const gameStatus = ref<'pending' | 'running' | 'optimizing' | 'completed'>('pending')
const roundLoading = ref(false)
const loadingStatusText = ref('')
const lastRetrievalText = ref('')
const maxRounds = ref(10)
const rounds = ref<any[]>([])
const messageStream = ref<any[]>([])

const streamingBuffer = reactive({
  side: 'our' as 'our' | 'opponent' | 'judge',
  agentName: '',
  content: ''
})
const currentAgentAction = ref<'blue' | 'red' | 'judge' | null>(null)

const winRate = ref(50)
const currentRoundEvidence = ref({ pro: 0, con: 0 })

const agentMetrics = reactive({
  blue: {
    legalReasoning: 85,
    evidenceUsage: 70,
    strategyExecution: 90
  },
  red: {
    activityLevel: 7.2,
    counterIntensity: 3,
    publicOpinion: 5,
    evidenceDispute: 3,
    externalAction: 1
  }
})

const ourAgents = ref<any[]>([])
const opponentAgents = ref<any[]>([])
const judgeAgent = ref<string>('')

const activeOurAgent = computed(() => ourAgents.value[0] || null)
const activeRedAgent = computed(() => opponentAgents.value[0] || null)
const statusLabel = computed(() => {
  switch (gameStatus.value) {
    case 'pending': return '待启动'
    case 'running': return '推演中'
    case 'optimizing': return '优化中'
    case 'completed': return '已完成'
    default: return '未知'
  }
})

const opponentStrategyLogs = ref<string[]>([
  '围绕合同解释、证据完整性、程序合规和监管口径组织反制观点。'
])

const hydratePreviewAgents = async () => {
  try {
    const allAgents = await agentApi.listAgents({ is_active: true })
    const selectedRaw = localStorage.getItem('selected_agents')
    const selectedAgents = selectedRaw ? JSON.parse(selectedRaw) : []
    const selectedBlueIds = (selectedAgents || [])
      .filter((agent: any) => ['blue', 'analyst'].includes(String(agent.agent_type || agent.type || '')))
      .map((agent: any) => String(agent.agent_id || agent.id || ''))
      .filter(Boolean)

    ourAgents.value = allAgents.filter((agent: any) => selectedBlueIds.includes(agent.agent_id))
    if (!ourAgents.value.length) {
      ourAgents.value = allAgents.filter((agent: any) => ['blue', 'analyst'].includes(agent.agent_type)).slice(0, 3)
    }

    opponentAgents.value = allAgents.filter((agent: any) => agent.agent_type === 'red').slice(0, 2)
    if (!judgeAgent.value) {
      judgeAgent.value = allAgents.find((agent: any) => agent.agent_type === 'judge')?.agent_id || ''
    }
  } catch (error) {
    console.error('恢复预览律师团失败:', error)
  }
}

const onConfigStart = (config: any) => {
  simulationConfig.value = config
  sessionId.value = config.simulationId
  eventId.value = config.eventId

  if (config.agentObjects) {
    ourAgents.value = config.blueAgents.map((id: string) => config.agentObjects[id]).filter(Boolean)
    opponentAgents.value = config.redAgents.map((id: string) => config.agentObjects[id]).filter(Boolean)
  } else {
    ourAgents.value = config.blueAgents.map((id: string) => ({ agent_id: id, name: id }))
    opponentAgents.value = config.redAgents.map((id: string) => ({ agent_id: id, name: id }))
  }

  judgeAgent.value = config.judgeAgent
  maxRounds.value = config.maxRounds || 10
  opponentStrategyLogs.value = ['系统将基于当前事件事实和我方主张动态生成对手反制观点。']

  rounds.value = []
  messageStream.value = []
  winRate.value = 50
  lastRetrievalText.value = ''
  streamingBuffer.content = ''
  gameStatus.value = 'running'
  showConfig.value = false

  ElMessage.success('推演环境初始化完成')
}

const previousArgs = reactive({ blue: '', red: '' })

const executeNextRound = async () => {
  if (gameStatus.value !== 'running') return
  if (!sessionId.value) {
    ElMessage.error('请先完成推演配置并启动')
    return
  }

  roundLoading.value = true
  loadingStatusText.value = '正在准备本轮推演...'
  lastRetrievalText.value = ''
  const roundNum = rounds.value.length + 1

  messageStream.value.push({
    type: 'separator',
    content: `ROUND ${roundNum}`,
    timestamp: new Date().toLocaleTimeString()
  })
  scrollToBottom()
  streamingBuffer.content = ''

  try {
    await simulationApi.executeRoundStream(
      sessionId.value,
      roundNum,
      eventId.value,
      ourAgents.value.map(agent => agent.agent_id),
      opponentAgents.value.map(agent => agent.agent_id),
      judgeAgent.value,
      { blue: previousArgs.blue, red: previousArgs.red },
      (msg: RoundMessage) => {
        handleStreamMessage(msg)
      }
    )
  } catch (error: any) {
    console.error('Round execution failed:', error)
    ElMessage.error(`推演执行失败：${error.message}`)
    roundLoading.value = false
    currentAgentAction.value = null
  }
}

const handleStreamMessage = (msg: RoundMessage) => {
  scrollToBottom()

  switch (msg.type) {
    case 'status':
      loadingStatusText.value = msg.message || '正在思考...'
      if (msg.agent === 'blue') currentAgentAction.value = 'blue'
      else if (msg.agent === 'red') currentAgentAction.value = 'red'
      else if (msg.agent === 'judge') currentAgentAction.value = 'judge'
      break

    case 'retrieval': {
      const agentLabel = msg.agent === 'blue' ? '我方智能体' : msg.agent === 'red' ? '对方智能体' : '裁判智能体'
      if (msg.phase === 'start') {
        lastRetrievalText.value = msg.enabled === false
          ? `${agentLabel}跳过检索，直接进入生成`
          : `${agentLabel}开始执行类案检索 + 法规检索`
        loadingStatusText.value = msg.enabled === false ? '当前阶段未启用检索' : '正在执行得理类案 / 法规检索...'
        break
      }

      const caseCount = msg.source_map?.filter(item => item.includes('[Case-')).length || 0
      const lawCount = msg.source_map?.filter(item => item.includes('[Law-')).length || 0
      lastRetrievalText.value = msg.enabled === false
        ? `${agentLabel}跳过检索，直接进入生成`
        : (caseCount || lawCount)
          ? `${agentLabel}检索完成：类案 ${caseCount} 条，法规 ${lawCount} 条`
          : `${agentLabel}已完成类案检索 + 法规检索`
      loadingStatusText.value = '检索完成，进入论证生成...'
      break
    }

    case 'blue_argument':
      if (!streamingBuffer.content && msg.chunk) {
        streamingBuffer.side = 'our'
        streamingBuffer.agentName = activeOurAgent.value?.name || '我方智能体'
      }
      if (msg.chunk) streamingBuffer.content += msg.chunk
      break

    case 'blue_complete':
      addMessage('our', activeOurAgent.value?.name || '我方智能体', streamingBuffer.content || msg.argument || '')
      previousArgs.blue = streamingBuffer.content || msg.argument || ''
      currentRoundEvidence.value.pro += 1
      streamingBuffer.content = ''
      break

    case 'red_argument':
      if (!streamingBuffer.content && msg.chunk) {
        streamingBuffer.side = 'opponent'
        streamingBuffer.agentName = activeRedAgent.value?.name || '对方智能体'
      }
      if (msg.chunk) streamingBuffer.content += msg.chunk
      break

    case 'red_complete':
      addMessage('opponent', activeRedAgent.value?.name || '对方智能体', streamingBuffer.content || msg.argument || '')
      previousArgs.red = streamingBuffer.content || msg.argument || ''
      currentRoundEvidence.value.con += 1
      streamingBuffer.content = ''
      break

    case 'judge_comment':
      if (!streamingBuffer.content && msg.chunk) {
        streamingBuffer.side = 'judge'
        streamingBuffer.agentName = '裁判智能体'
      }
      if (msg.chunk) streamingBuffer.content += msg.chunk
      break

    case 'judge_complete':
      addMessage('judge', '裁判智能体', streamingBuffer.content || msg.comment || '')
      streamingBuffer.content = ''
      if (typeof msg.win_rate === 'number') winRate.value = msg.win_rate
      lastRetrievalText.value = '本轮裁判评议已完成'
      break

    case 'round_complete':
      roundLoading.value = false
      currentAgentAction.value = null
      rounds.value.push(msg.round)
      loadingStatusText.value = '本轮推演完成'
      if (rounds.value.length >= maxRounds.value) {
        handleSimulationEnd({ status: 'completed', final_result: { termination_reason: '达到最大回合数' } })
      }
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
      if (msg.data?.evidence?.length) {
        const isPositive = msg.data.impact === 'positive'
        ElNotification({
          title: isPositive ? '方案正向优化' : '方案风险预警',
          message: `关键证据 [${msg.data.evidence.join(', ')}] 对胜率产生 ${msg.data.delta > 0 ? '+' : ''}${msg.data.delta.toFixed(1)}% 的影响`,
          type: isPositive ? 'success' : 'warning',
          duration: 5000,
          position: 'bottom-right'
        })
      }
      break

    case 'error':
      ElMessage.error(msg.error || '未知错误')
      roundLoading.value = false
      currentAgentAction.value = null
      break
  }
}

const handleSimulationEnd = (simStatus: any) => {
  gameStatus.value = simStatus.status
  lastRetrievalText.value = ''

  if (simStatus.status === 'completed') {
    ElNotification({
      title: '推演完成',
      message: simStatus.final_result?.termination_reason || '推演已结束',
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
  ElMessage.info('手动优化功能开发中...')
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
    ElMessage.error('无法获取有效推演 ID')
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

onMounted(() => {
  hydratePreviewAgents()
})
</script>

<style scoped>
.s5-battle-page {
  position: relative;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at top, rgba(30, 41, 59, 0.35), #020617 55%);
  color: #fff;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}
.bg-grid {
  position: absolute;
  inset: 0;
  background-image: linear-gradient(rgba(59,130,246,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(59,130,246,0.08) 1px, transparent 1px);
  background-size: 32px 32px;
  opacity: 0.2;
  pointer-events: none;
}
.bg-glow {
  position: absolute;
  width: 520px;
  height: 520px;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.18;
  pointer-events: none;
}
.bg-glow-left { top: 120px; left: -160px; background: #2563eb; }
.bg-glow-right { bottom: -180px; right: -140px; background: #ef4444; }
.battle-hud,
.scenario-banner,
.battle-layout { position: relative; z-index: 1; }
.battle-hud {
  height: 60px;
  background: rgba(15, 23, 42, 0.86);
  border-bottom: 1px solid rgba(255,255,255,0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  backdrop-filter: blur(10px);
}
.hud-left { display: flex; align-items: center; gap: 20px; }
.back-btn { color: #94a3b8; }
.page-title { font-size: 16px; font-weight: 700; color: #fff; margin: 0; }
.new-round-btn {
  background: linear-gradient(90deg, #2563eb, #3b82f6);
  border: none;
  font-weight: 700;
  padding: 10px 20px;
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.35);
}
.scenario-banner {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 12px 20px;
  background: rgba(2, 6, 23, 0.48);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  backdrop-filter: blur(8px);
}
.banner-item {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(148,163,184,0.12);
  background: rgba(15, 23, 42, 0.55);
}
.banner-label { display: block; color: #64748b; font-size: 11px; margin-bottom: 6px; }
.banner-value { color: #e2e8f0; font-size: 13px; font-weight: 600; }
.banner-value.mono { font-family: monospace; color: #93c5fd; }
.banner-value.retrieval { color: #fde68a; }
.battle-layout { flex: 1; display: grid; grid-template-columns: 320px 1fr 340px; overflow: hidden; }
.col-side {
  background: rgba(15, 23, 42, 0.45);
  border-right: 1px solid rgba(255,255,255,0.05);
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  backdrop-filter: blur(8px);
}
.col-center {
  background: rgba(15, 23, 42, 0.64);
  position: relative;
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 20px;
  overflow-y: auto;
}
.opp-side { border-right: none; border-left: 1px solid rgba(255,255,255,0.05); }
.panel-header { margin-bottom: 10px; }
.ph-title { font-size: 14px; font-weight: 700; color: #e2e8f0; }
.ph-sub { font-size: 11px; color: #64748b; margin-top: 4px; }
.ph-sub.red { color: #fca5a5; }
.agent-status-card {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  padding: 12px;
  border-radius: 10px;
}
.agent-status-card.red-theme {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}
.avatar-row { display: flex; gap: 12px; align-items: center; margin-bottom: 8px; }
.agent-meta .name { font-weight: 700; font-size: 14px; }
.status-badge {
  font-size: 10px;
  background: #10b981;
  padding: 1px 6px;
  border-radius: 2px;
  display: inline-block;
  margin-top: 4px;
  font-weight: 700;
}
.status-badge.running { background: #3b82f6; }
.status-badge.active { background: #f59e0b; color: #000; }
.duty-title { font-weight: 700; margin-bottom: 4px; color: #e2e8f0; }
.duty-title.red { color: #fca5a5; }
.duty-text { font-size: 11px; color: #94a3b8; line-height: 1.5; }
.empty-agent {
  border: 1px dashed rgba(148,163,184,0.2);
  color: #64748b;
  padding: 18px;
  border-radius: 10px;
  text-align: center;
}
.stats-box, .action-points-panel, .plan-info-box, .opp-stats, .strategy-log {
  background: rgba(0,0,0,0.18);
  padding: 12px;
  border-radius: 10px;
}
.stat-row { margin-bottom: 10px; }
.stat-row:last-child { margin-bottom: 0; }
.stat-row .label { font-size: 11px; color: #94a3b8; display: block; margin-bottom: 4px; }
.stat-bar :deep(.el-progress-bar__outer) { background-color: rgba(255,255,255,0.1); }
.score-display { text-align: center; margin-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 8px; }
.score-val { font-size: 28px; font-weight: 700; color: #fff; }
.score-label { font-size: 10px; color: #64748b; }
.metrics-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 12px; }
.m-item { text-align: center; background: rgba(255,255,255,0.03); padding: 6px; border-radius: 4px; }
.m-val { display: block; font-weight: 700; font-size: 12px; }
.m-lbl { font-size: 10px; color: #64748b; }
.manual-actions { display: flex; gap: 10px; }
.cyber-btn { flex: 1; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); color: #fff; }
.cyber-btn.outline { background: transparent; }
.pi-title { color: #64748b; margin-bottom: 4px; }
.pi-content { color: #60a5fa; font-weight: 700; margin-bottom: 4px; font-family: monospace; }
.pi-desc { color: #94a3b8; }
.opp-stats { text-align: center; }
.stat-big-num { font-size: 32px; font-weight: 900; color: #f59e0b; }
.stat-label { font-size: 11px; color: #64748b; }
.opp-params-list { padding: 12px; }
.p-row { display: flex; justify-content: space-between; font-size: 12px; color: #94a3b8; margin-bottom: 8px; }
.dots { letter-spacing: 2px; font-size: 10px; }
.dots.red { color: #ef4444; }
.dots.gold { color: #f59e0b; }
.dots.green { color: #10b981; }
.log-title { color: #64748b; margin-bottom: 8px; }
.log-item { display: flex; gap: 6px; margin-bottom: 8px; color: #e2e8f0; }
.log-idx { color: #f59e0b; }
.center-top { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.stream-header { font-size: 12px; color: #64748b; letter-spacing: 1px; font-weight: 700; }
.retrieval-banner {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(234, 179, 8, 0.12);
  border: 1px solid rgba(234,179,8,0.28);
  color: #fde68a;
  font-size: 12px;
}
.round-separator { display: flex; align-items: center; gap: 12px; margin: 24px 0; color: #3b82f6; font-family: 'Orbitron'; }
.sep-line { flex: 1; height: 1px; background: linear-gradient(90deg, transparent, rgba(59, 130, 246, 0.3), transparent); }
.sep-text { font-size: 12px; font-weight: 700; letter-spacing: 2px; }
.message-list { flex: 1; display: flex; flex-direction: column; padding-bottom: 40px; }
.empty-state { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #64748b; }
.loading-bubble { text-align: center; color: #3b82f6; margin-top: 10px; display: flex; flex-direction: column; align-items: center; }
.loading-text { font-size: 12px; color: #94a3b8; margin-top: 4px; }
.dot { display: inline-block; width: 6px; height: 6px; background: #3b82f6; border-radius: 50%; margin: 0 4px; animation: bounce 1s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
.streaming-buffer-bubble { opacity: 0.86; }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.2); border-radius: 2px; }
.optimization-status {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #3b82f6;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  animation: pulse 2s infinite;
}
.optimization-status.finished {
  background: rgba(16, 185, 129, 0.2);
  border-color: rgba(16, 185, 129, 0.4);
  color: #34d399;
  animation: none;
}
.text-green { color: #34d399 !important; }
@keyframes bounce { 0%, 80%, 100% { transform: translateY(0); opacity: 0.6; } 40% { transform: translateY(-6px); opacity: 1; } }
@keyframes pulse { 0% { opacity: 0.8; } 50% { opacity: 1; } 100% { opacity: 0.8; } }
@media (max-width: 1500px) {
  .scenario-banner { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .battle-layout { grid-template-columns: 280px 1fr 300px; }
}
</style>
