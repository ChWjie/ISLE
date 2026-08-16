<template>
  <div class="agent-entry-page">
    <div class="top-nav-bar">
      <div class="nav-content">
        <span class="nav-item">态势首页</span>
        <span class="nav-sep">/</span>
        <span class="nav-item active">多智能体任务分析</span>
      </div>
    </div>

    <div class="page-header-banner">
      <h1 class="page-title">多智能体分析入口</h1>
      <p class="page-desc">在企业合规、争议解决和监管应对场景下，选择合适的智能体组合进入分析流程。</p>
    </div>

    <div class="main-container">
      <aside class="left-sidebar">
        <div class="sidebar-section description-box">
          <div class="section-title">能力说明</div>
          <p class="desc-text">
            系统支持劳动合规、数据合规、合同争议、知识产权、竞争合规、证券监管等多个专业智能体协同分析，适用于企业风控、案情研判和方案制定。
          </p>
        </div>

        <div class="sidebar-section">
          <div class="section-title">系统状态</div>
          <div class="status-list">
            <div class="status-item"><span class="label">可用智能体</span><span class="value highlight-green">{{ stats.total }} 个</span></div>
            <div class="status-item"><span class="label">分析智能体</span><span class="value highlight-blue">{{ stats.blue }} 个</span></div>
            <div class="status-item"><span class="label">博弈智能体</span><span class="value highlight-cyan">{{ stats.red }} 个</span></div>
            <div class="status-item"><span class="label">裁判智能体</span><span class="value highlight-purple">{{ stats.judge }} 个</span></div>
          </div>
        </div>
      </aside>

      <main class="right-content">
        <div class="search-row">
          <el-input
            v-model="searchQuery"
            placeholder="搜索智能体名称或专业方向"
            class="custom-search-input"
            :suffix-icon="Search"
          />
        </div>

        <div class="action-cards-row">
          <div class="action-card primary-card">
            <div class="card-icon"><el-icon><Document /></el-icon></div>
            <div class="card-content">
              <h3>从事件进入分析</h3>
              <p>如果你已经创建了争议事件或合规案件，可直接进入事件绑定分析流程。</p>
              <div class="card-meta">
                <span>适用于：已有事件的深度分析</span>
                <span>推荐流程：S1 → S2 → S3/S4</span>
              </div>
              <el-button type="primary" class="action-btn" @click="startAnalysis">进入态势首页</el-button>
            </div>
          </div>

          <div class="action-card secondary-card">
            <div class="card-icon"><el-icon><User /></el-icon></div>
            <div class="card-content">
              <h3>新增分析智能体</h3>
              <p>创建新的专业分析角色，补充合规研判、法律论证或证据分析能力。</p>
              <div class="card-meta">
                <span>适用于：扩展分析维度</span>
                <span>支持：劳动、数据、合同等方向</span>
              </div>
              <el-button class="action-btn outline-btn">创建智能体</el-button>
            </div>
          </div>

          <div class="action-card secondary-card">
            <div class="card-icon"><el-icon><Cpu /></el-icon></div>
            <div class="card-content">
              <h3>新增博弈智能体</h3>
              <p>创建对抗、质证、裁判或外部角色，用于后续博弈推演和方案验证。</p>
              <div class="card-meta">
                <span>适用于：红蓝对抗推演</span>
                <span>支持：对方代理、监管方、裁判方</span>
              </div>
              <el-button class="action-btn outline-btn">创建智能体</el-button>
            </div>
          </div>
        </div>

        <div class="filter-bar">
          <div class="filter-group">
            <span class="filter-label">智能体分类</span>
            <span class="filter-tag active">分析智能体</span>
            <span class="filter-tag">博弈智能体</span>
            <span class="filter-tag">裁判智能体</span>
          </div>
        </div>

        <div class="agents-grid-section custom-scrollbar">
          <AgentCard
            v-for="agent in filteredAgents"
            :key="String((agent as any).agent_id || agent.id)"
            :agent="agent"
            :is-selected="false"
            @toggle="noop"
            @edit="noop"
          />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, User, Cpu, Search } from '@element-plus/icons-vue'
import agentsApi from '@/api/agents'
import AgentCard from './components/AgentCard.vue'
import type { Agent } from '@/types'

const router = useRouter()
const searchQuery = ref('')
const agents = ref<Agent[]>([])

const stats = computed(() => {
  const total = agents.value.length
  const blue = agents.value.filter((agent: any) => agent.agent_type === 'blue').length
  const red = agents.value.filter((agent: any) => agent.agent_type === 'red').length
  const judge = agents.value.filter((agent: any) => agent.agent_type === 'judge').length
  return { total, blue, red, judge }
})

const filteredAgents = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) return agents.value
  return agents.value.filter((agent: any) => {
    const name = String(agent.name || '').toLowerCase()
    const desc = String(agent.description || '').toLowerCase()
    return name.includes(query) || desc.includes(query)
  })
})

const fallbackAgents: Agent[] = [
  { id: '0', name: '劳动合规顾问-张律师', description: '聚焦劳动用工、解除流程与工伤争议处理。', created_at: '2026-01-01', law_domains: ['劳动用工'] } as Agent,
  { id: '1', name: '数据合规专家-李顾问', description: '聚焦个人信息保护、数据安全与出境合规。', created_at: '2026-01-01', law_domains: ['数据合规'] } as Agent,
  { id: '2', name: '合同纠纷律师-王律师', description: '聚焦合同履行、违约责任与争议解决策略。', created_at: '2026-01-01', law_domains: ['合同交易'] } as Agent,
  { id: '3', name: '知识产权律师-陈律师', description: '聚焦商业秘密、商标和著作权侵权争议。', created_at: '2026-01-01', law_domains: ['知识产权'] } as Agent,
]

const loadAgents = async () => {
  try {
    const data = await agentsApi.listAgents()
    if (data && data.length > 0) {
      agents.value = (data as any[]).map((agent: any) => ({
        ...agent,
        id: String(agent.agent_id || agent.id),
        law_domains: agent.knowledge_scope || agent.law_domains || [],
      })) as Agent[]
    } else {
      agents.value = fallbackAgents
    }
  } catch {
    agents.value = fallbackAgents
  }
}

const startAnalysis = () => {
  router.push('/situation')
}

const noop = () => {}

onMounted(() => {
  loadAgents()
})
</script>

<style scoped>
.agent-entry-page {
  min-height: 100vh;
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
  color: #fff;
}
.top-nav-bar {
  background: var(--color-bg-secondary);
  padding: 10px 24px;
  border-bottom: 1px solid var(--color-border);
}
.nav-content { display: flex; gap: 8px; align-items: center; }
.nav-item { color: var(--color-text-secondary); }
.nav-item.active { color: #fff; font-weight: 600; }
.page-header-banner {
  padding: 24px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.15);
}
.page-title { margin: 0 0 8px; }
.page-desc { margin: 0; color: #94a3b8; }
.main-container {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 20px;
  padding: 20px 24px 24px;
}
.left-sidebar, .action-card, .agents-grid-section, .filter-bar {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 16px;
}
.left-sidebar { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.section-title { font-weight: 700; margin-bottom: 10px; }
.desc-text, .status-item, .card-meta { color: #cbd5e1; }
.status-list { display: flex; flex-direction: column; gap: 10px; }
.status-item { display: flex; justify-content: space-between; }
.highlight-green { color: #4ade80; }
.highlight-blue { color: #60a5fa; }
.highlight-cyan { color: #22d3ee; }
.highlight-purple { color: #c084fc; }
.right-content { display: flex; flex-direction: column; gap: 16px; }
.action-cards-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
.action-card { padding: 18px; display: flex; gap: 14px; }
.card-icon {
  width: 48px; height: 48px; border-radius: 12px;
  background: rgba(37, 99, 235, 0.15);
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; color: #60a5fa;
}
.card-content h3 { margin: 0 0 8px; }
.card-content p { margin: 0 0 12px; color: #cbd5e1; }
.card-meta { display: flex; flex-direction: column; gap: 6px; font-size: 13px; margin-bottom: 14px; }
.search-row, .filter-bar { padding: 16px; }
.filter-group { display: flex; gap: 12px; align-items: center; }
.filter-tag { color: #94a3b8; }
.filter-tag.active { color: #fff; }
.agents-grid-section {
  padding: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}
@media (max-width: 1200px) {
  .main-container, .action-cards-row { grid-template-columns: 1fr; }
}
</style>
