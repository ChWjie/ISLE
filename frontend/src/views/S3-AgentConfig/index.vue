<template>
  <div class="agent-config-page">
    <!-- Top Breadcrumb -->
    <div class="top-bread">
       <span>态势首页</span>
       <el-icon><ArrowRight /></el-icon>
       <span>事件详情</span>
       <el-icon><ArrowRight /></el-icon>
       <span class="active">多智能体任务分析</span>
    </div>

    <!-- Main Layout -->
    <div class="main-layout">
      <!-- Left Sidebar: Event Locking (The one I mistakenly put in Entry previously) -->
      <aside class="sidebar-left">
        <div class="input-panel">
           <!-- 1. Select Event -->
           <div class="panel-section">
              <div class="section-label-row">
                 <div class="radio-indicator"></div>
                 <span class="label">选择事件</span>
              </div>
              <el-select v-model="selectedEventId" placeholder="请选择争议事件" class="custom-select" size="large" disabled>
                 <el-option v-if="currentEvent" :label="currentEvent.name" :value="currentEvent.event_id" />
                 <el-option v-else label="加载中..." value="" />
              </el-select>
           </div>

           <!-- 2. Task Description -->
           <div class="panel-section flex-grow">
              <div class="section-label-row">
                 <div class="radio-indicator active"></div>
                 <span class="label">任务描述</span>
              </div>
              <div class="textarea-wrapper">
                 <el-input
                    v-model="taskDescription"
                    type="textarea"
                    :rows="12"
                    placeholder="请输入具体的任务描述，包括背景、目标、约束条件等..."
                    class="custom-textarea"
                    resize="none"
                    maxlength="1500"
                    show-word-limit
                 />
              </div>
           </div>

           <!-- 3. Upload -->
           <div class="panel-section">
              <div class="section-label-row">
                 <div class="radio-indicator"></div>
                 <span class="label">上传附件</span>
              </div>
              <div class="upload-zone">
                 <el-icon class="upload-icon"><UploadFilled /></el-icon>
                 <div class="upload-text">文件拖拽到此处，或 <span class="click-text">点击上传</span></div>
                 <div class="upload-limit">每文件大小不超过10MB</div>
              </div>
           </div>
        </div>
      </aside>

      <!-- Center: Agents Grid -->
      <main class="center-content">
        <!-- Stats/Filter Header -->
        <div class="center-header">
           <div class="stat-group">
             <div class="stat-item">
               <span class="label">智能体分类</span>
               <span class="value">分析律师</span>
             </div>
             <div class="stat-item">
               <span class="label">创建时间</span>
               <div class="time-filters">
                 <span class="filter-btn active">近七天</span>
                 <span class="filter-btn">近一个月</span>
                 <span class="filter-btn">近三个月</span>
                 <span class="filter-btn custom">自定义 2026-01-01 ~ 2026-01-10</span>
               </div>
             </div>
             <div class="stat-item">
               <span class="label">专业分类</span>
             </div>
           </div>

           <div class="search-wrap">
             <el-input
               v-model="searchQuery"
               placeholder="搜索智能体"
               class="search-input"
               suffix-icon="Search"
             />
           </div>
        </div>

        <!-- Grid -->
        <div class="grid-container custom-scrollbar" v-loading="loading">
            <!-- Action Cards Row (Moved inside grid) -->
            <div class="action-cards-row">
              <!-- Card 1: Event/Contract Analysis -->
              <div class="action-card">
                 <div class="card-icon-wrapper"><el-icon><Document /></el-icon></div>
                 <div class="card-content">
                    <h3>事件/合同分析</h3>
                    <p>从系统已创建的争议事件出发，进行具体事件并配置律师团分析参数，直接进入多智能体分析流程。</p>
                    <div class="card-meta">
                       <span class="meta-row">适用卡片：已存在争议事件的深度分析</span>
                       <span class="meta-row">可用事件：15个</span>
                    </div>
                    <el-button type="primary" class="action-btn" @click="startAnalysis">开始分析</el-button>
                 </div>
              </div>

              <!-- Card 2: Add Lawyer Agent -->
              <div class="action-card">
                 <div class="card-icon-wrapper"><el-icon><User /></el-icon></div>
                 <div class="card-content">
                    <h3>新增法庭律师智能体</h3>
                    <p>介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字</p>
                    <div class="card-meta">
                       <span class="meta-row">适用卡片：拓展法律分析维度</span>
                       <span class="meta-row">可用模板：15个</span>
                    </div>
                    <el-button plain class="action-btn" @click="createAgent('lawyer')">创建智能体</el-button>
                 </div>
              </div>

              <!-- Card 3: Add Game Agent -->
              <div class="action-card">
                 <div class="card-icon-wrapper"><el-icon><Setting /></el-icon></div>
                 <div class="card-content">
                    <h3>新增博弈智能体</h3>
                    <p>介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字介绍文字</p>
                    <div class="card-meta">
                       <span class="meta-row">适用卡片：红蓝对抗与策略推演</span>
                       <span class="meta-row">可用模板：15个</span>
                    </div>
                    <el-button plain class="action-btn" @click="createAgent('game')">创建智能体</el-button>
                 </div>
              </div>
            </div>

            <AgentCard
              v-for="agent in filteredAgents"
              :key="agent.id"
              :agent="agent"
              :is-selected="selectedAgentIds.has(agent.id)"
              @toggle="toggleAgent(agent.id)"
              @edit="selectAgentForConfig(agent)"
            />
        </div>

        <!-- Bottom Action -->
        <div class="bottom-bar">
           <el-button type="primary" class="start-btn" size="large" @click="startAnalysis">开始分析</el-button>
        </div>
      </main>

      <!-- Agent Config Drawer -->
      <AgentConfigDrawer
         v-model:visible="drawerVisible"
         :agent="currentConfigAgent"
         @save="saveConfig"
         append-to-body
      />

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, UploadFilled, Document, User, Setting } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import AgentConfigDrawer from './components/AgentConfigDrawer.vue'
import AgentCard from './components/AgentCard.vue'
import eventsApi from '@/api/events'  // 真实Events API
import agentsApi from '@/api/agents'  // 真实Agents API
import type { Agent, DisputeEvent } from '@/types'

const route = useRoute()
const router = useRouter()
const loading = ref(false)

const currentEvent = ref<DisputeEvent | null>(null)
const selectedEventId = ref('evt1')
const taskDescription = ref(`文本描述文本描述文本描述文本描述文本描述文本描述文本描述文本描述文本描述
文本描述文本描述文本描述文本描述文本描述文本描述文本描述文本描述文本描述
文本描述文本描述文本描述文本描述文本描述文本描述文本描述文本描述文本描述`)

const agents = ref<Agent[]>([])
const selectedAgentIds = ref<Set<string>>(new Set())
// const selectAllRec = ref(false) // Removed
const searchQuery = ref('')
const currentConfigAgent = ref<Agent | null>(null)
const drawerVisible = ref(false)

const filteredAgents = computed(() => {
  return agents.value.filter(agent => agent.name.includes(searchQuery.value))
})

const fallbackAgents: Agent[] = [
  { id: 'agent-labor', agent_id: 'agent-labor', name: 'Labor Compliance Advisor', type: 'blue', description: 'Labor contracts, dismissal process, salary and injury disputes.', created_at: '2026-01-01', law_domains: ['Labor'] } as Agent,
  { id: 'agent-data', agent_id: 'agent-data', name: 'Data Compliance Advisor', type: 'blue', description: 'Personal information protection, data security and export compliance.', created_at: '2026-01-01', law_domains: ['Data'] } as Agent,
  { id: 'agent-contract', agent_id: 'agent-contract', name: 'Contract Dispute Lawyer', type: 'blue', description: 'Contract performance, liability and dispute resolution strategy.', created_at: '2026-01-01', law_domains: ['Contract'] } as Agent,
  { id: 'agent-ip', agent_id: 'agent-ip', name: 'IP Lawyer', type: 'blue', description: 'Trade secrets, trademarks, copyright and infringement disputes.', created_at: '2026-01-01', law_domains: ['IP'] } as Agent,
]

const createAgent = (type: string) => {
  // 创建新智能体模板
  currentConfigAgent.value = {
    id: '',
    name: type === 'lawyer' ? '新法庭律师' : '新博弈智能体',
    type: type === 'lawyer' ? 'analysis_lawyer' : 'game_lawyer',
    avatar: '',
    law_domains: [],
    description: '',
    level: 'L1',
    created_at: new Date().toISOString()
  } as Agent
  drawerVisible.value = true
}

const loadData = async () => {
   loading.value = true
   try {
     const res = await agentsApi.listAgents()
     // 简单的类型断言修复
     agents.value = (res as any[]).map((agent: any) => ({
       ...agent,
       id: String(agent.agent_id || agent.id),
       law_domains: agent.knowledge_scope || agent.law_domains || [],
     })) as unknown as Agent[]
     console.log(`✓ Loaded ${res.length} agents from backend`)
   } catch (e) {
      console.error('Failed to load agents:', e)
      agents.value = fallbackAgents
      ElMessage.warning('智能体接口暂不可用，已加载本地兜底智能体')
   } finally {
     loading.value = false
   }
}

const toggleAgent = (id: string) => {
  const normalizedId = String(id)
  if (selectedAgentIds.value.has(normalizedId)) {
    selectedAgentIds.value.delete(normalizedId)
  } else {
    selectedAgentIds.value.add(normalizedId)
  }
}

const selectAgentForConfig = (agent: Agent) => {
  currentConfigAgent.value = agent
  drawerVisible.value = true
}

const saveConfig = async (config: any) => {
    loading.value = true
    try {
        console.log('Saving agent config:', config)

        // Prepare payload (adapt frontend form to backend schema)
        // Note: Backend expects snake_case, frontend form uses mixed.
        // We need to map form fields to API request body.

        const payload = {
            name: config.name,
            agent_type: 'blue', // Default for now, or derive from type
            system_prompt: config.mission + '\n' + config.responsibilities, // Combine or use prompt directly if available
            stance: config.mission, // Use mission as stance summary
            goals: [], // Default empty or map from somewhere
            strategy_orientation: config.reasoningStyle || 'balanced',
            legal_priority: 'mixed',
            knowledge_scope: config.knowledge_scope || [],
            // Store other detailed configs in model_config JSON if needed
            model_config: {
                model: config.model,
                temperature: config.temperature,
                responsibilities: config.responsibilities
            }
        }

        // If it's an existing agent (has ID and ID is not empty/temp)
        if (currentConfigAgent.value && currentConfigAgent.value.id && currentConfigAgent.value.agent_id) {
             await agentsApi.updateAgent(currentConfigAgent.value.agent_id, payload)
             ElMessage.success('智能体更新成功')
        } else {
             // Create new
             // We might need to generate a random ID if backend requires it, or let backend handle it.
             // The seed script generates IDs. Let's see if createAgent requires ID.
             // Schema says ID is autogenerated usually, but agent_id string might be needed.
             // Let's rely on backend or generate one.
             await agentsApi.createAgent({
                 ...payload,
                 agent_id: `AGENT-${Date.now()}` // Temporary detailed ID generation
             } as any)
             ElMessage.success('智能体创建成功')
        }

        drawerVisible.value = false
        loadData() // Refresh list
    } catch (e) {
        console.error('Save failed:', e)
        ElMessage.error('保存失败: ' + (e as any).message)
    } finally {
        loading.value = false
    }
}

const startAnalysis = () => {
   if (selectedAgentIds.value.size === 0) return ElMessage.warning('请选择智能体')

   // 保存选中的智能体到localStorage
   const selectedAgents = agents.value.filter(a => selectedAgentIds.value.has(a.id))
   localStorage.setItem('selected_agents', JSON.stringify(selectedAgents))

   router.push(`/plan-generation/${route.params.id || currentEvent.value?.event_id}`)
}

// 加载事件详情（从路由参数）
const loadEventDetail = async () => {
  const eventId = route.params.id as string
  if (!eventId) return

  try {
    const found = await eventsApi.getEvent(eventId)
    if (found) {
      // 类型适配
      currentEvent.value = {
          ...found,
          id: found.event_id || String(found.id),
          title: found.name,
          location_name: found.dispute_type || '未知区域',
          parties: [...(found.our_side || []), ...(found.opponent_side || [])],
          status: 'pending',
          type: 'territory', // 默认值
          location: { lat: 0, lng: 0 } // 默认值
      } as unknown as DisputeEvent

      selectedEventId.value = currentEvent.value.id
      taskDescription.value = currentEvent.value.description || ''
      console.log('✓ Loaded event for analysis:', currentEvent.value.title)
    }
  } catch (error) {
    console.error('Failed to load event:', error)
  }
}

onMounted(() => {
    loadEventDetail()  // 加载事件详情
    loadData()         // 加载智能体
})
</script>

<style scoped>
.agent-config-page {
  height: calc(100vh - 64px);
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
  color: #fff;
  font-family: 'Inter', sans-serif;
}

.top-bread {
  height: 48px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  gap: 8px;
  font-size: 14px;
  color: var(--color-text-tertiary);
}
.top-bread .active { color: #fff; font-weight: 500; }

.main-layout {
  flex: 1;
  display: flex;
  overflow: hidden;
}


.sidebar-left {
  width: 400px;
  background: rgba(20, 27, 45, 0.6);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.input-panel {
  padding: 24px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 24px;
  position: relative;
}
.panel-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  padding-left: 28px;
  padding-top: 24px; /* Space for absolute label */
}
.panel-section.flex-grow { flex: 1; min-height: 0; }

/* Connecting Line */
.input-panel::before {
   content: ''; position: absolute; top: 40px; bottom: 80px; left: 29px; width: 1px;
   background: rgba(255,255,255,0.1); z-index: 0;
}

.section-label-row { display: flex; align-items: center; gap: 0; position: absolute; left: 0; top: 0; }
.radio-indicator { width: 12px; height: 12px; border: 2px solid var(--color-text-tertiary); border-radius: 50%; background: #0B1026; z-index: 1; margin-right: 12px; }
.radio-indicator.active { border-color: var(--color-primary); background: var(--color-primary); box-shadow: 0 0 8px var(--color-primary); }
.label { font-size: 14px; color: #fff; font-weight: 500; }

.custom-select { width: 100%; }
.custom-textarea :deep(.el-textarea__inner) {
  background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255,255,255,0.05); color: #94A3B8; font-size: 13px; line-height: 1.6; height: 100%; padding: 12px;
  resize: none;
}
.textarea-wrapper { flex: 1; display: flex; flex-direction: column; }
.textarea-wrapper :deep(.el-textarea) { height: 100%; }

.upload-zone {
  border: 1px dashed var(--color-border);
  background: rgba(0,0,0,0.2);
  border-radius: 4px;
  height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}
.upload-zone:hover { border-color: var(--color-primary); background: rgba(59, 130, 246, 0.05); }
.upload-icon { font-size: 32px; color: var(--color-text-tertiary); margin-bottom: 8px; }
.upload-text { font-size: 12px; color: var(--color-text-secondary); }
.click-text { color: var(--color-primary); font-weight: bold; }
.upload-limit { font-size: 10px; color: var(--color-text-tertiary); margin-top: 4px; }


/* Center Content */
.center-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
  border-right: 1px solid var(--color-border);
  overflow: hidden;
  position: relative; /* Ensure stacking context */
  z-index: 1;
}

.center-header {
  padding: 16px;
  background: rgba(0,0,0,0.2);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  position: relative;
  z-index: 2;
}
/* ... (stat-group styles omitted for brevity) ... */

/* Action Cards */
.action-cards-row {
  grid-column: 1 / -1; /* Span all columns in grid */
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  position: relative;
  z-index: 20;
  margin-bottom: 16px; /* Add margin bottom since it's inside grid now */
}

.action-card {
  background: rgba(20, 27, 45, 0.6);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 16px;
  display: flex;
  gap: 16px;
  transition: all 0.2s;
  position: relative;
  z-index: 21;
}
.action-card:hover {
  border-color: var(--color-primary);
  background: rgba(30, 58, 138, 0.2);
}

/* ... (card-icon-wrapper, card-content styles omitted) ... */

.action-btn {
  width: 100%;
  margin-top: auto;
  position: relative;
  z-index: 22; /* Ensure button is top-most */
  cursor: pointer;
  pointer-events: auto; /* Force pointer events */
}
.stat-group { display: flex; flex-direction: column; gap: 8px; }
.stat-item { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.stat-item .label { color: var(--color-text-tertiary); width: 60px; }
.stat-item .value { color: #fff; font-weight: 500; }
.time-filters { display: flex; gap: 4px; }
.filter-btn { padding: 2px 8px; font-size: 11px; color: var(--color-text-secondary); cursor: pointer; }
.filter-btn.active { background: var(--color-primary); color: #fff; border-radius: 2px; }
.search-input { width: 200px; }

/* Action Cards */
.action-cards-row {
  margin: 0 16px 16px 16px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  position: relative;
  z-index: 10;
}

.action-card {
  background: rgba(20, 27, 45, 0.6);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 16px;
  display: flex;
  gap: 16px;
  transition: all 0.2s;
}
.action-card:hover {
  border-color: var(--color-primary);
  background: rgba(30, 58, 138, 0.2);
}

.card-icon-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(59, 130, 246, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: var(--color-primary);
  flex-shrink: 0;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-content h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #fff;
  font-weight: 600;
}

.card-content p {
  margin: 0 0 12px 0;
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 16px;
}

.meta-row {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

.action-btn {
  width: 100%;
  margin-top: auto;
}

.grid-container {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px 16px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  align-content: flex-start;
}

.bottom-bar {
  padding: 12px;
  background: rgba(0,0,0,0.4);
  border-top: 1px solid var(--color-border);
  display: flex;
}
.start-btn { width: 100%; font-size: 16px; letter-spacing: 2px; }

/* Right Sidebar */
.sidebar-right {
  width: 280px;
  background: rgba(20, 27, 45, 0.4);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}
.right-panel-content { padding: 16px; }
.agent-detail-panel h3 { margin-top: 0; }
.detail-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 20px; }
.right-panel-empty { height: 100%; display: flex; align-items: center; justify-content: center; color: var(--color-text-tertiary); text-align: center; }
.sub-text { font-size: 12px; opacity: 0.6; }

/* Scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.2); border-radius: 2px; }
</style>
