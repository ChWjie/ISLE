<template>
  <el-drawer
    v-model="visible"
    title="推演配置 / Simulation Config"
    size="960px"
    class="game-config-drawer"
    direction="rtl"
    :before-close="handleClose"
    destroy-on-close
  >
    <div class="drawer-layout" v-loading="loading">
      <div class="header-desc">
        围绕当前事件选择研判方案、我方律师团、对方代理与裁判角色，并设置本轮博弈参数。
      </div>

      <div class="overview-grid">
        <div class="overview-card">
          <div class="overview-label">当前事件</div>
          <div class="overview-value">{{ currentPlan?.event?.name || currentPlan?.event_name || '待选择方案' }}</div>
          <div class="overview-hint">{{ currentPlan?.event_description || '请先选择与当前事件绑定的综合研判方案。' }}</div>
        </div>
        <div class="overview-card">
          <div class="overview-label">方案数量</div>
          <div class="overview-value">{{ plans.length }}</div>
          <div class="overview-hint">优先展示当前事件的方案与本地缓存方案。</div>
        </div>
        <div class="overview-card">
          <div class="overview-label">可用智能体</div>
          <div class="overview-value">{{ allAgents.length }}</div>
          <div class="overview-hint">已按我方 / 对方 / 裁判角色自动分组。</div>
        </div>
      </div>

      <div class="config-grid">
        <section class="config-card span-2">
          <div class="card-title">方案选择</div>
          <el-select v-model="form.selectedPlanId" placeholder="请选择推演方案" style="width: 100%" filterable>
            <el-option
              v-for="plan in plans"
              :key="plan.plan_id"
              :label="`${plan.title}（${plan.plan_id}）`"
              :value="plan.plan_id"
            />
          </el-select>
          <div class="card-hint">S4 生成并保存的综合研判报告会自动进入这里，避免推演与研判脱节。</div>
        </section>

        <section class="config-card">
          <div class="card-title">我方律师团</div>
          <el-select v-model="form.blueAgents" multiple collapse-tags collapse-tags-tooltip placeholder="请选择我方智能体" style="width: 100%">
            <el-option v-for="agent in blueAgents" :key="agent.agent_id" :label="agent.name" :value="agent.agent_id" />
          </el-select>
          <div class="selected-tags">
            <span v-for="agent in selectedBlueAgents" :key="agent.agent_id" class="role-chip blue">{{ agent.name }}</span>
          </div>
          <div class="card-hint">支持多名我方智能体共同辩护，S5 左侧将按你选择的数量展示。</div>
        </section>

        <section class="config-card">
          <div class="card-title">对方角色</div>
          <el-select v-model="form.redAgents" multiple collapse-tags collapse-tags-tooltip placeholder="请选择对方智能体" style="width: 100%">
            <el-option v-for="agent in redAgents" :key="agent.agent_id" :label="agent.name" :value="agent.agent_id" />
          </el-select>
          <div class="selected-tags">
            <span v-for="agent in selectedRedAgents" :key="agent.agent_id" class="role-chip red">{{ agent.name }}</span>
          </div>
          <div class="card-hint">可同时加入监管方、对方代理等多种对抗视角。</div>
        </section>

        <section class="config-card">
          <div class="card-title">裁判角色</div>
          <el-select v-model="form.judgeAgent" placeholder="请选择裁判智能体" style="width: 100%">
            <el-option v-for="agent in judgeAgents" :key="agent.agent_id" :label="agent.name" :value="agent.agent_id" />
          </el-select>
          <div class="selected-tags">
            <span v-if="selectedJudgeAgent" class="role-chip judge">{{ selectedJudgeAgent.name }}</span>
          </div>
          <div class="card-hint">用于输出裁判意见、胜率评估和终局判断。</div>
        </section>

        <section class="config-card">
          <div class="card-title">推演参数</div>
          <div class="param-row">
            <span>最大轮次</span>
            <el-input-number v-model="form.maxRounds" :min="1" :max="10" />
          </div>
          <div class="param-row">
            <span>目标胜率</span>
            <el-input-number v-model="form.targetWinRate" :min="50" :max="100" />
          </div>
          <div class="param-row">
            <span>我方人数</span>
            <strong>{{ form.blueAgents.length }}</strong>
          </div>
          <div class="param-row">
            <span>对方人数</span>
            <strong>{{ form.redAgents.length }}</strong>
          </div>
        </section>

        <section class="config-card span-2" v-if="currentPlan">
          <div class="card-title">方案摘要</div>
          <div class="plan-meta">
            <span>方案标题：{{ currentPlan.title }}</span>
            <span>关联事件：{{ currentPlan.event?.name || currentPlan.event_name || currentPlan.event_id || '-' }}</span>
          </div>
          <pre class="plan-preview">{{ currentPlan.content || currentPlan.event_description || '暂无方案内容' }}</pre>
        </section>
      </div>

      <div class="drawer-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="starting" @click="emitStart">开始推演</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import agentApi, { type Agent } from '@/api/agents'
import planApi, { type Plan } from '@/api/plans'
import simulationApi from '@/api/simulation'

type DrawerPlan = Plan & {
  id?: number | string
  event_name?: string
  event_description?: string
}

const props = defineProps<{
  visible: boolean
  initialPlanId?: string
}>()

const emit = defineEmits(['update:visible', 'start-game'])
const route = useRoute()

const visible = computed({
  get: () => props.visible,
  set: (value: boolean) => emit('update:visible', value)
})

const loading = ref(false)
const starting = ref(false)
const plans = ref<DrawerPlan[]>([])
const allAgents = ref<Agent[]>([])

const form = reactive({
  selectedPlanId: props.initialPlanId || '',
  blueAgents: [] as string[],
  redAgents: [] as string[],
  judgeAgent: '',
  maxRounds: 3,
  targetWinRate: 80,
})

const blueAgents = computed(() => allAgents.value.filter(item => item.agent_type === 'blue' || item.agent_type === 'analyst'))
const redAgents = computed(() => allAgents.value.filter(item => item.agent_type === 'red'))
const judgeAgents = computed(() => allAgents.value.filter(item => item.agent_type === 'judge'))
const currentPlan = computed(() => plans.value.find(item => item.plan_id === form.selectedPlanId))
const selectedBlueAgents = computed(() => blueAgents.value.filter(agent => form.blueAgents.includes(agent.agent_id)))
const selectedRedAgents = computed(() => redAgents.value.filter(agent => form.redAgents.includes(agent.agent_id)))
const selectedJudgeAgent = computed(() => judgeAgents.value.find(agent => agent.agent_id === form.judgeAgent) || null)

const dedupePlans = (items: DrawerPlan[]) => {
  const seen = new Set<string>()
  return items.filter(item => {
    const key = item.plan_id || String(item.id || '')
    if (!key || seen.has(key)) return false
    seen.add(key)
    return true
  })
}

const readLocalPlan = (): DrawerPlan[] => {
  const savedPlan = localStorage.getItem('selectedPlan')
  if (!savedPlan) return []

  try {
    const parsed = JSON.parse(savedPlan)
    return [{
      plan_id: parsed.plan_id || 'current',
      title: parsed.title || '当前综合研判方案',
      content: parsed.sections?.length
        ? parsed.sections.map((section: any) => `## ${section.title}\n\n${section.content}`).join('\n\n')
        : parsed.content || '',
      created_at: parsed.timestamp,
      event_id: parsed.event?.event_id || parsed.event_id,
      event: parsed.event,
      event_name: parsed.event?.name || parsed.event?.title,
      event_description: parsed.event?.description || parsed.event?.fact_summary,
      status: 'draft'
    }]
  } catch (error) {
    console.error('解析本地方案失败:', error)
    return []
  }
}

const preloadSelectedAgents = () => {
  const raw = localStorage.getItem('selected_agents')
  if (!raw) return

  try {
    const selectedAgents = JSON.parse(raw) as Array<{ agent_id?: string; id?: string; agent_type?: string; type?: string }>
    const blueIds = selectedAgents
      .filter(agent => ['blue', 'analyst'].includes(String(agent.agent_type || agent.type || '')))
      .map(agent => String(agent.agent_id || agent.id || ''))
      .filter(Boolean)

    if (blueIds.length) {
      form.blueAgents = Array.from(new Set(blueIds))
    }
  } catch (error) {
    console.error('读取已选智能体失败:', error)
  }
}

const handleClose = () => {
  visible.value = false
}

const loadPlans = async () => {
  const localPlans = readLocalPlan()
  const routePlanId = props.initialPlanId || String(route.params.id || route.query.planId || '')
  const routeEventId = String(route.params.eventId || localPlans[0]?.event_id || '')

  try {
    const apiPlans = await planApi.listPlans()
    const filteredApiPlans = routeEventId
      ? apiPlans.filter(item => item.event_id === routeEventId)
      : apiPlans

    plans.value = dedupePlans([...localPlans, ...filteredApiPlans])
  } catch (error) {
    console.error('加载方案列表失败:', error)
    plans.value = dedupePlans(localPlans)
  }

  if (routePlanId && plans.value.some(item => item.plan_id === routePlanId)) {
    form.selectedPlanId = routePlanId
  } else if (!form.selectedPlanId && plans.value.length) {
    form.selectedPlanId = plans.value[0]?.plan_id || ''
  }
}

const loadAgents = async () => {
  try {
    const data = await agentApi.listAgents({ is_active: true })
    allAgents.value = data || []
  } catch (error) {
    console.error('加载智能体失败:', error)
    allAgents.value = []
  }

  if (!form.blueAgents.length && blueAgents.value.length) {
    form.blueAgents = blueAgents.value.slice(0, 2).map(agent => agent.agent_id)
  }
  if (!form.redAgents.length && redAgents.value.length) {
    form.redAgents = redAgents.value.slice(0, 2).map(agent => agent.agent_id)
  }
  if (!form.judgeAgent && judgeAgents.value.length) {
    form.judgeAgent = judgeAgents.value[0]?.agent_id || ''
  }
}

const emitStart = async () => {
  if (!form.selectedPlanId) return ElMessage.warning('请先选择方案')
  if (!form.blueAgents.length) return ElMessage.warning('请至少选择一个我方智能体')
  if (!form.redAgents.length) return ElMessage.warning('请至少选择一个对方智能体')
  if (!form.judgeAgent) return ElMessage.warning('请选择裁判智能体')

  const selectedPlan = currentPlan.value
  const eventId = String(selectedPlan?.event?.event_id || selectedPlan?.event_id || '')
  if (!eventId) return ElMessage.warning('未找到方案关联事件')

  const agentObjects: Record<string, Agent> = {}
  allAgents.value.forEach(agent => {
    agentObjects[agent.agent_id] = agent
  })

  starting.value = true
  try {
    const result = await simulationApi.startSimulation({
      event_id: eventId,
      plan_id: form.selectedPlanId,
      blue_agent_ids: form.blueAgents,
      red_agent_ids: form.redAgents,
      judge_agent_id: form.judgeAgent,
      max_rounds: form.maxRounds,
      target_win_rate: form.targetWinRate,
    })

    emit('start-game', {
      ...form,
      eventId,
      planTitle: selectedPlan?.title || '当前选定方案',
      simulationId: result.simulation_id,
      agentObjects,
      plan: selectedPlan,
    })
    visible.value = false
    ElMessage.success('推演环境初始化完成')
  } catch (error: any) {
    console.error(error)
    ElMessage.error(error?.message || '启动推演失败')
  } finally {
    starting.value = false
  }
}

onMounted(async () => {
  preloadSelectedAgents()
  loading.value = true
  await Promise.all([loadPlans(), loadAgents()])
  loading.value = false
})
</script>

<style scoped>
.drawer-layout { display: flex; flex-direction: column; gap: 16px; min-height: 100%; }
.header-desc {
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.75);
  color: #cbd5e1;
  line-height: 1.7;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
.overview-card,
.config-card {
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 14px;
  padding: 16px;
}
.overview-label { color: #94a3b8; font-size: 12px; margin-bottom: 8px; }
.overview-value { color: #fff; font-size: 20px; font-weight: 700; margin-bottom: 8px; }
.overview-hint { color: #94a3b8; font-size: 12px; line-height: 1.6; }
.config-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.span-2 { grid-column: span 2; }
.card-title { font-weight: 700; margin-bottom: 12px; color: #fff; }
.card-hint { margin-top: 10px; color: #94a3b8; font-size: 12px; line-height: 1.6; }
.param-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  color: #e2e8f0;
}
.selected-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  min-height: 24px;
}
.role-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid transparent;
}
.role-chip.blue {
  color: #bfdbfe;
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.35);
}
.role-chip.red {
  color: #fecaca;
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.3);
}
.role-chip.judge {
  color: #fde68a;
  background: rgba(234, 179, 8, 0.12);
  border-color: rgba(234, 179, 8, 0.28);
}
.plan-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 12px;
  color: #94a3b8;
  font-size: 12px;
}
.plan-preview {
  margin: 0;
  max-height: 260px;
  overflow: auto;
  white-space: pre-wrap;
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.8;
  background: rgba(2, 6, 23, 0.45);
  border-radius: 10px;
  padding: 14px;
}
.drawer-footer { display: flex; justify-content: flex-end; gap: 12px; margin-top: auto; }
@media (max-width: 900px) {
  .overview-grid,
  .config-grid { grid-template-columns: 1fr; }
  .span-2 { grid-column: span 1; }
}
</style>

<style>
.game-config-drawer .el-drawer {
  background: #0b1120 !important;
  color: #e2e8f0 !important;
}
.game-config-drawer .el-drawer__header {
  margin-bottom: 0 !important;
  padding: 18px 24px !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  background: rgba(15, 23, 42, 0.96) !important;
}
.game-config-drawer .el-drawer__title,
.game-config-drawer .el-drawer__close-btn {
  color: #f8fafc !important;
}
.game-config-drawer .el-drawer__body {
  background: linear-gradient(180deg, #0f172a 0%, #020617 100%) !important;
  padding: 20px !important;
}
</style>
