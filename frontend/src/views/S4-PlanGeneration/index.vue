<template>
  <div class="s4-page">
    <div class="s4-header">
      <div class="header-left">
        <div class="back-btn" @click="router.back()">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </div>
        <h1 class="page-title">智能体研判分析 // MULTI-AGENT ANALYSIS</h1>
      </div>
      <div class="header-right">
        <div class="session-id">
          SESSION: {{ (typeof route.params.eventId === 'string' ? route.params.eventId : 'UNK').substring(0, 8).toUpperCase() }}
        </div>
      </div>
    </div>

    <div class="s4-layout">
      <aside class="col-left">
        <div class="sidebar-header">
          <h2 class="header-title">
            <el-icon><Location /></el-icon>
            事件锁定
          </h2>
        </div>

        <div class="sidebar-content custom-scrollbar">
          <div class="info-box">
            <div class="box-header">事件基础信息</div>
            <div class="box-content">
              <div class="field-row">
                <div class="field-item">
                  <div class="field-label">事件 ID</div>
                  <div class="field-value input-style">{{ currentEvent?.event_id || currentEvent?.id || 'EV-...' }}</div>
                </div>
                <div class="field-item">
                  <div class="field-label">事件名称</div>
                  <div class="field-value input-style">{{ currentEvent?.name || currentEvent?.title || '加载中...' }}</div>
                </div>
              </div>
              <div class="field-row">
                <div class="field-item">
                  <div class="field-label">紧急程度</div>
                  <div class="field-value highlight-red">高</div>
                </div>
                <div class="field-item">
                  <div class="field-label">时间窗口</div>
                  <div class="field-value input-style">2025-12-28 ~ 2025-12-31</div>
                </div>
              </div>
              <div class="field-row full">
                <div class="field-item">
                  <div class="field-label">地点 / 业务场景</div>
                  <div class="field-value link-style">
                    {{ currentEvent?.location_name || currentEvent?.dispute_type || '当前事件地点信息 / 业务发生地' }}
                    <el-icon><MapLocation /></el-icon>
                    查看地图
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="info-box">
            <div class="box-header">争议类型与标签</div>
            <div class="box-content">
              <div class="field-item full">
                <div class="field-label">争议类型</div>
                <div class="field-value input-style">{{ currentEvent?.dispute_type || '企业合规与争议处置' }}</div>
              </div>
              <div class="field-item full">
                <div class="field-label">标签</div>
                <div class="tags-row">
                  <span class="tag-cyan">合规审查</span>
                  <span class="tag-cyan">证据分析</span>
                  <span class="tag-cyan">争议应对</span>
                  <span class="tag-cyan">风险控制</span>
                </div>
              </div>
            </div>
          </div>

          <div class="info-box">
            <div class="box-header">涉及主体与立场</div>
            <div class="box-content">
              <div class="field-item full">
                <div class="field-label">我方主体</div>
                <div class="actors-row">
                  <span v-for="(item, idx) in displayOurSide" :key="`our-${idx}`" class="actor-tag blue">{{ item }}</span>
                </div>
              </div>
              <div class="field-item full">
                <div class="field-label">对方主体</div>
                <div class="actors-row">
                  <span v-for="(item, idx) in displayOpponentSide" :key="`opp-${idx}`" class="actor-tag blue">{{ item }}</span>
                </div>
              </div>
              <div class="field-item full">
                <div class="field-label">第三方机构</div>
                <div class="actors-row">
                  <span class="actor-tag outline">监管机构 / 仲裁机构 / 法院</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <main class="col-center">
        <template v-if="currentStage === 'analysis'">
          <div class="stage-header">
            <h3>法律专家智能体 · 分析产出预览</h3>
            <p>基于当前案件，多个专业智能体正在并发检索并生成法律分析意见。</p>
          </div>

          <div class="analysis-grid custom-scrollbar">
            <AgentAnalysisPreview
              v-for="agent in agentStates"
              :key="agent.id"
              :agent="agent"
              :status="agent.status"
              :logs="agent.logs"
              :result="agent.result"
              :sources="agent.sources"
            />
          </div>

          <div class="center-actions">
            <el-button type="primary" class="action-btn" :disabled="!isAllAgentsComplete" @click="integratePlan">
              <span class="btn-text">整合最终方案</span>
              <el-icon><Right /></el-icon>
            </el-button>
          </div>
        </template>

        <template v-else>
          <div class="stage-header">
            <h3>多智能体分析结果整合 · 研判汇总</h3>
            <p>综合各智能体意见、检索依据和争议焦点，形成结构化法律研判报告。</p>
          </div>

          <div class="doc-container">
            <PlanDocument title="综合法律研判报告" :sections="planSections" :is-streaming="isIntegrating" />
          </div>

          <div class="center-actions">
            <el-button class="action-btn secondary">人工编辑</el-button>
            <el-button class="action-btn secondary" :loading="isSaving" @click="handleSavePlan">保存方案</el-button>
            <el-button type="primary" class="action-btn" @click="goToSimulation">
              <span class="btn-text">进入法律博弈模拟</span>
              <el-icon><Right /></el-icon>
            </el-button>
          </div>
        </template>
      </main>

      <aside class="col-right">
        <div class="panel-header">
          <el-icon><UserFilled /></el-icon>
          律师团运行状态
        </div>
        <div class="expert-list custom-scrollbar">
          <AgentAnalysisCard
            v-for="agent in agentStates"
            :key="agent.id"
            :agent="agent"
            :status="agent.status"
            :logs="agent.logs"
            :sources="agent.sources"
          />

          <div class="integration-status-card" v-if="currentStage === 'integration'">
            <div class="card-title">成果整合智能体</div>
            <div class="status-text" :class="{ completed: !isIntegrating }">
              {{ isIntegrating ? '正在整合各子报告...' : '整合完成' }}
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Location, MapLocation, Right, UserFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AgentAnalysisCard from './components/AgentAnalysisCard.vue'
import AgentAnalysisPreview from './components/AgentAnalysisPreview.vue'
import PlanDocument from './components/PlanDocument.vue'
import eventsApi from '@/api/events'
import agentsApi from '@/api/agents'
import plansApi, { type AgentAnalysisMessage, type IntegrateMessage } from '@/api/plans'
import type { Agent, DisputeEvent } from '@/types'

const route = useRoute()
const router = useRouter()

type Stage = 'analysis' | 'integration'

interface AgentState extends Agent {
  status: 'pending' | 'retrieving' | 'generating' | 'completed' | 'error'
  logs: Array<{ time: string; content: string }>
  sources: string[]
  retrievalQuery?: string
  retrievalEnabled?: boolean
  caseCount?: number
  lawCount?: number
  result: { analysis?: string } | null
}

const currentStage = ref<Stage>('analysis')
const isAnalyzing = ref(true)
const isIntegrating = ref(false)
const isSaving = ref(false)
const currentEvent = ref<DisputeEvent | null>(null)
const agentStates = ref<AgentState[]>([])
const planSections = ref<Array<{ title: string; content: string }>>([])

const isAllAgentsComplete = computed(() => agentStates.value.length > 0 && agentStates.value.every(agent => agent.status === 'completed'))
const displayOurSide = computed(() => currentEvent.value?.our_side?.length ? currentEvent.value.our_side : ['企业法务部', '外部律师团'])
const displayOpponentSide = computed(() => currentEvent.value?.opponent_side?.length ? currentEvent.value.opponent_side : ['国家市场监管总局', '受损商家联合会'])
const nowTime = () => new Date().toLocaleTimeString('zh-CN', { hour12: false })

const cityCoordinates: Record<string, { lat: number; lng: number }> = {
  深圳: { lat: 22.5431, lng: 114.0579 },
  广州: { lat: 23.1291, lng: 113.2644 },
  北京: { lat: 39.9042, lng: 116.4074 },
  上海: { lat: 31.2304, lng: 121.4737 },
  杭州: { lat: 30.2741, lng: 120.1551 },
  成都: { lat: 30.5728, lng: 104.0668 },
  武汉: { lat: 30.5928, lng: 114.3055 },
  南京: { lat: 32.0603, lng: 118.7969 },
  重庆: { lat: 29.5630, lng: 106.5516 }
}

const inferLocation = (raw: any) => {
  const text = [raw?.name, raw?.description, raw?.fact_summary].filter(Boolean).join(' ')
  const matchedCity = Object.keys(cityCoordinates).find(city => text.includes(city))
  if (!matchedCity) return null
  return {
    location_name: matchedCity,
    location: cityCoordinates[matchedCity]
  }
}

const normalizeEvent = (raw: any): DisputeEvent => {
  const inferred = inferLocation(raw)
  return {
    id: String(raw?.event_id || raw?.id || ''),
    event_id: raw?.event_id || '',
    title: raw?.title || raw?.name || '未命名事件',
    name: raw?.name || raw?.title || '未命名事件',
    type: 'economic',
    description: raw?.description || raw?.fact_summary || '',
    location: raw?.location || inferred?.location || { lat: 39.9042, lng: 116.4074 },
    location_name: raw?.location_name || inferred?.location_name || '未指定地点',
    parties: [...(raw?.our_side || []), ...(raw?.opponent_side || [])],
    status: 'pending',
    severity: raw?.severity || 4,
    created_at: raw?.created_at || '',
    updated_at: raw?.updated_at || '',
    dispute_type: raw?.dispute_type || '企业合规与争议处置',
    our_side: raw?.our_side || [],
    opponent_side: raw?.opponent_side || [],
    legal_systems: raw?.legal_systems || [],
    fact_summary: raw?.fact_summary || ''
  }
}

const appendLog = (agent: AgentState, content: string) => {
  agent.logs.push({ time: nowTime(), content })
}

const sleep = (ms: number) => new Promise(resolve => window.setTimeout(resolve, ms))

const countRetrievalSources = (sources: string[]) => ({
  caseCount: sources.filter(item => item.includes('[Case-')).length,
  lawCount: sources.filter(item => item.includes('[Law-')).length,
})

const buildDemoAnalysis = (agent: Agent, event: DisputeEvent) => {
  const domains = ((agent as any).knowledge_scope || agent.law_domains || []).join('、') || '企业合规、争议解决'
  const eventName = event.name || event.title || '当前争议事件'
  return `【${agent.name}】基于${domains}对“${eventName}”完成研判：\n\n` +
    `1. 事实识别：本案核心在于${event.dispute_type || '企业合规与法律风险处置'}，需围绕主体责任、证据链完整性、程序合规性展开审查。\n` +
    `2. 法规检索：重点参考《民法典》《公司法》《劳动合同法》《个人信息保护法》等与事件相关的规范，判断企业行为是否存在合规瑕疵。\n` +
    `3. 类案检索：结合相似裁判案例，优先关注责任认定、举证责任、损害后果和整改措施对裁判结果的影响。\n` +
    `4. 策略建议：建议先固定证据、梳理合同/制度/流程文件，形成“事实澄清 + 法律依据 + 整改承诺 + 风险隔离”的综合应对方案。`
}

const runLocalDemoAnalysis = async (agents: Agent[]) => {
  if (!currentEvent.value) return
  for (const agent of agents) {
    const agentId = String((agent as any).agent_id || agent.id)
    handleStreamMessage({
      type: 'status',
      agent_id: agentId,
      status: 'running'
    })
    await sleep(220)
    handleStreamMessage({
      type: 'retrieval',
      agent_id: agentId,
      phase: 'complete',
      enabled: true,
      query: `${currentEvent.value.name || currentEvent.value.title} ${agent.name}`,
      source_map: [
        `[Case-${agentId.slice(-4)}] 相似企业合规争议裁判案例`,
        `[Case-${agentId.slice(-3)}] 同类法律责任认定案例`,
        `[Law-${agentId.slice(-4)}] 相关法律法规与司法解释`,
        `[Law-${agentId.slice(-3)}] 行业监管规则与合规指引`
      ],
      case_count: 2,
      law_count: 2
    })
    await sleep(260)
    handleStreamMessage({
      type: 'content',
      agent_id: agentId,
      chunk: buildDemoAnalysis(agent, currentEvent.value)
    })
    await sleep(180)
    handleStreamMessage({
      type: 'complete',
      agent_id: agentId,
      analysis: buildDemoAnalysis(agent, currentEvent.value)
    })
  }
}

const buildDemoIntegratedReport = () => {
  const event = currentEvent.value
  const eventName = event?.name || event?.title || '当前争议事件'
  const analyses = agentStates.value
    .filter(agent => agent.result?.analysis)
    .map(agent => `### ${agent.name}\n${agent.result?.analysis || ''}`)
    .join('\n\n')

  return `# 综合法律研判报告\n\n` +
    `## 一、事件概述\n本报告围绕“${eventName}”进行多智能体法律研判，结合事件事实、法规检索、类案检索和不同专家视角形成综合建议。\n\n` +
    `## 二、核心争议焦点\n1. 企业相关行为是否违反法定义务或监管要求。\n2. 现有证据能否支撑责任抗辩、风险减轻或整改说明。\n3. 对方主体可能提出的请求、监管机关可能关注的合规风险。\n4. 后续处置中如何兼顾法律风险、经营影响与公众沟通。\n\n` +
    `## 三、专家研判摘要\n${analyses || '各智能体已完成初步分析，建议结合案件材料继续补充证据。'}\n\n` +
    `## 四、综合应对方案\n1. 立即整理合同、制度、通知、沟通记录、审批流程等关键证据。\n2. 对照相关法律法规形成合规自查清单，标记高风险事项。\n3. 准备对外回应口径和内部整改方案，降低监管与诉讼风险。\n4. 对可能进入仲裁、诉讼或行政调查的事项，提前设计举证和抗辩路径。\n\n` +
    `## 五、结论\n本案建议采取“证据固定—法律评估—风险隔离—整改优化—争议应对”的五步策略，以降低法律责任和经营损失。`
}

const loadData = async () => {
  const eventId = route.params.eventId as string
  if (!eventId || eventId === 'UNK') {
    ElMessage.error('缺少事件 ID')
    return
  }

  try {
    const foundEvent = await eventsApi.getEvent(eventId)
    currentEvent.value = foundEvent ? normalizeEvent(foundEvent) : null
    if (!currentEvent.value) {
      ElMessage.error('未找到对应事件')
      return
    }

    const selectedAgentsStr = localStorage.getItem('selected_agents')
    let selectedAgents: Agent[] = selectedAgentsStr ? JSON.parse(selectedAgentsStr) : []
    if (!selectedAgents.length) {
      console.warn('[S4] no selected_agents in localStorage, fallback to first active agents')
      const backendAgents = await agentsApi.listAgents({ is_active: true })
      selectedAgents = (backendAgents as unknown as Agent[]).slice(0, 4)
      localStorage.setItem('selected_agents', JSON.stringify(selectedAgents))
      ElMessage.warning('未检测到上一步选择记录，已自动载入推荐智能体')
    }
    const resolvedEventId = currentEvent.value.event_id || eventId
    agentStates.value = selectedAgents.map(agent => ({ ...agent, status: 'pending', logs: [], sources: [], retrievalQuery: '', retrievalEnabled: true, caseCount: 0, lawCount: 0, result: null }))
    await runAnalysis(resolvedEventId, selectedAgents)
  } catch (error) {
    console.error('Failed to load data:', error)
    ElMessage.error('页面数据加载失败')
  }
}

const runAnalysis = async (eventId: string, agents: Agent[]) => {
  isAnalyzing.value = true
  const agentIds = agents.map(agent => (agent as any).agent_id || agent.id)

  try {
    await plansApi.generatePlanStream(eventId, agentIds, (message: AgentAnalysisMessage) => {
      handleStreamMessage(message)
    })
  } catch (error) {
    console.error('Failed to generate plan:', error)
    ElMessage.warning('云端分析接口暂不可用，已切换为演示兜底生成')
    await runLocalDemoAnalysis(agents)
  } finally {
    isAnalyzing.value = false
  }
}

const handleStreamMessage = (message: AgentAnalysisMessage) => {
  const agent = agentStates.value.find(item => (item as any).agent_id === message.agent_id || item.id === message.agent_id)
  if (!agent) return

  switch (message.type) {
    case 'status':
      if (message.status === 'running') {
        agent.status = 'retrieving'
        appendLog(agent, '开始执行得理类案检索 / 法规检索...')
      } else if (message.status === 'completed') {
        agent.status = 'completed'
      }
      break
    case 'retrieval':
      if (message.phase === 'start') {
        agent.status = 'retrieving'
        agent.retrievalEnabled = message.enabled !== false
        agent.retrievalQuery = message.query || ''
        appendLog(agent, message.enabled === false ? '当前场景未启用检索' : `正在检索：类案 + 法规`)
        break
      }

      agent.status = 'generating'
      agent.sources = message.source_map || []
      agent.retrievalQuery = message.query || ''
      agent.retrievalEnabled = message.enabled !== false
      const { caseCount, lawCount } = countRetrievalSources(agent.sources)
      agent.caseCount = message.case_count ?? caseCount
      agent.lawCount = message.law_count ?? lawCount
      appendLog(agent, message.enabled === false ? '当前场景未启用得理检索' : `检索关键词：${message.query || '未提供'}`)
      appendLog(agent, message.enabled === false ? '已跳过检索，直接进入分析生成' : `类案检索 ${agent.caseCount} 条，法规检索 ${agent.lawCount} 条`)
      if (message.degraded) appendLog(agent, '检索发生降级，结果可能不完整')
      break
    case 'content':
      agent.status = 'generating'
      if (!agent.result) agent.result = { analysis: '' }
      if (message.chunk) agent.result.analysis = (agent.result.analysis || '') + message.chunk
      break
    case 'complete':
      agent.status = 'completed'
      agent.result = { analysis: message.analysis || agent.result?.analysis || '' }
      appendLog(agent, '分析已完成')
      break
    case 'error':
      agent.status = 'error'
      agent.result = { analysis: `分析失败：${message.error || '未知错误'}` }
      appendLog(agent, `执行失败：${message.error || '未知错误'}`)
      break
  }
}

const integratePlan = async () => {
  if (!currentEvent.value) return
  currentStage.value = 'integration'
  isIntegrating.value = true
  planSections.value = []

  try {
    const agentAnalyses = agentStates.value.filter(agent => agent.result?.analysis).map(agent => ({ agent_name: agent.name, agent_type: (agent as any).agent_type || 'blue', analysis: agent.result?.analysis || '' }))
    if (agentAnalyses.length === 0) {
      ElMessage.warning('暂无可整合的分析结果')
      return
    }

    const sections: Array<{ title: string; content: string }> = [{ title: '综合法律研判报告', content: '' }]
    planSections.value = sections

    await plansApi.integratePlanStream(currentEvent.value.event_id || '', agentAnalyses, (message: IntegrateMessage) => {
      if (message.type === 'start') {
        if (sections[0]) sections[0].content = ''
        planSections.value = [...sections]
        return
      }

      if (message.type === 'content' && message.chunk) {
        if (sections[0]) sections[0].content += message.chunk
        planSections.value = [...sections]
        return
      }

      if (message.type === 'complete') {
        if (sections[0]) sections[0].content = message.content || sections[0].content
        planSections.value = [...sections]
        return
      }

      if (message.type === 'section_complete' && message.content) {
        const index = typeof message.index === 'number' ? message.index : 0
        if (!sections[index]) {
          sections[index] = { title: message.section || `第 ${index + 1} 部分`, content: '' }
        }
        sections[index].title = message.section || sections[index].title
        sections[index].content = message.content
        planSections.value = sections.filter(Boolean)
        return
      }

      if (message.type === 'error') {
        ElMessage.error('整合报告生成失败')
      }
    })
  } catch (error) {
    console.error('Failed to integrate plan:', error)
    planSections.value = [{ title: '综合法律研判报告', content: buildDemoIntegratedReport() }]
    ElMessage.warning('云端整合接口暂不可用，已生成演示版综合报告')
  } finally {
    isIntegrating.value = false
  }
}

const handleSavePlan = async () => {
  if (!currentEvent.value) return null
  isSaving.value = true
  try {
    const fullContent = planSections.value.map(section => `## ${section.title}\n\n${section.content}`).join('\n\n')
    const res = await plansApi.savePlan({ event_id: currentEvent.value.event_id || '', title: `${currentEvent.value.name || currentEvent.value.title} - AI 研判方案`, content: fullContent, action_paths: [] })
    ElMessage.success('方案已保存至方案库')
    localStorage.setItem('selectedPlan', JSON.stringify({ plan_id: res.plan_id, event_id: currentEvent.value.event_id, event: currentEvent.value, agents: agentStates.value, sections: planSections.value, timestamp: Date.now() }))
    return res.plan_id
  } catch (error: any) {
    console.error(error)
    const fallbackPlanId = `LOCAL-${Date.now()}`
    localStorage.setItem('selectedPlan', JSON.stringify({ plan_id: fallbackPlanId, event_id: currentEvent.value.event_id, event: currentEvent.value, agents: agentStates.value, sections: planSections.value, timestamp: Date.now(), local_fallback: true }))
    ElMessage.warning('云端保存暂不可用，已保存到本地演示方案')
    return fallbackPlanId
  } finally {
    isSaving.value = false
  }
}

const goToSimulation = async () => {
  if (!currentEvent.value) return
  const planId = await handleSavePlan()
  if (planId) router.push(`/game-simulation/${planId}`)
  else router.push(`/game-simulation/${route.params.eventId}`)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.s4-page { height: 100vh; display: flex; flex-direction: column; background: #020617; color: #fff; font-family: 'Inter', sans-serif; }
.s4-header { height: 60px; background: rgba(15, 23, 42, 0.9); border-bottom: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center; padding: 0 24px; }
.header-left { display: flex; align-items: center; gap: 20px; }
.back-btn { color: #94a3b8; cursor: pointer; display: flex; align-items: center; gap: 4px; font-size: 14px; transition: color 0.2s; }
.back-btn:hover { color: #fff; }
.page-title { font-size: 16px; font-weight: 700; color: #fff; margin: 0; letter-spacing: 1px; padding-left: 20px; border-left: 1px solid rgba(255, 255, 255, 0.1); }
.session-id { font-family: 'Orbitron', monospace; font-size: 12px; color: #64748b; background: rgba(255, 255, 255, 0.05); padding: 4px 12px; border-radius: 4px; }
.s4-layout { flex: 1; height: calc(100vh - 60px); display: grid; grid-template-columns: 280px 1fr 280px; overflow: hidden; }
.col-left, .col-right { background: rgba(20, 27, 45, 0.6); backdrop-filter: blur(10px); display: flex; flex-direction: column; height: 100%; overflow: hidden; }
.col-left { border-right: 1px solid rgba(255, 255, 255, 0.1); }
.col-right { border-left: 1px solid rgba(255, 255, 255, 0.1); padding: 20px; }
.sidebar-header { height: 48px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); display: flex; align-items: center; padding: 0 20px; }
.header-title { font-size: 14px; font-weight: 600; color: #cbd5e1; display: flex; align-items: center; gap: 6px; margin: 0; }
.sidebar-content { flex: 1; padding: 16px 12px; overflow-y: auto; }
.info-box { border: 1px solid rgba(59, 130, 246, 0.25); background: rgba(15, 23, 42, 0.4); border-radius: 4px; margin-bottom: 14px; overflow: hidden; }
.box-header { background: rgba(30, 58, 138, 0.15); color: #dbeafe; font-size: 12px; font-weight: 600; padding: 8px 12px; border-bottom: 1px solid rgba(59, 130, 246, 0.2); }
.box-content { padding: 10px 12px 12px; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
.field-row.full { grid-template-columns: 1fr; }
.field-item.full { margin-bottom: 10px; }
.field-label { font-size: 11px; color: #94a3b8; margin-bottom: 6px; }
.field-value { font-size: 12px; color: #e2e8f0; }
.input-style { background: rgba(2, 6, 23, 0.55); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 2px; min-height: 34px; display: flex; align-items: center; padding: 0 10px; }
.highlight-red { background: rgba(127, 29, 29, 0.4); border: 1px solid rgba(239, 68, 68, 0.35); color: #fca5a5; border-radius: 2px; min-height: 34px; display: flex; align-items: center; padding: 0 10px; }
.link-style { font-size: 12px; color: #93c5fd; display: flex; align-items: center; gap: 6px; }
.tags-row, .actors-row { display: flex; flex-wrap: wrap; gap: 8px; }
.tag-cyan, .actor-tag { font-size: 11px; padding: 3px 8px; border-radius: 2px; border: 1px solid rgba(59, 130, 246, 0.25); }
.tag-cyan { color: #67e8f9; background: rgba(8, 145, 178, 0.12); }
.actor-tag.blue { color: #dbeafe; background: rgba(59, 130, 246, 0.12); }
.actor-tag.outline { color: #cbd5e1; background: transparent; }
.col-center { display: flex; flex-direction: column; min-width: 0; padding: 20px 16px 16px; overflow: hidden; }
.stage-header { margin-bottom: 16px; }
.stage-header h3 { margin: 0 0 6px; font-size: 24px; color: #fff; }
.stage-header p { margin: 0; color: #94a3b8; font-size: 13px; }
.analysis-grid { flex: 1; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; overflow-y: auto; padding-right: 4px; }
.doc-container { flex: 1; min-height: 0; }
.center-actions { display: flex; justify-content: flex-end; gap: 12px; padding-top: 16px; }
.action-btn { min-width: 132px; }
.action-btn.secondary { background: rgba(255, 255, 255, 0.04); border-color: rgba(255, 255, 255, 0.1); color: #cbd5e1; }
.btn-text { margin-right: 6px; }
.panel-header { color: #cbd5e1; font-size: 13px; font-weight: 600; display: flex; align-items: center; gap: 6px; margin-bottom: 14px; }
.expert-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; }
.integration-status-card { border: 1px solid rgba(59, 130, 246, 0.2); background: rgba(15, 23, 42, 0.45); border-radius: 4px; padding: 12px; }
.card-title { color: #fff; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.status-text { color: #60a5fa; font-size: 12px; }
.status-text.completed { color: #34d399; }
.custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: rgba(255, 255, 255, 0.04); }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.3); border-radius: 999px; }
@media (max-width: 1600px) { .analysis-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
