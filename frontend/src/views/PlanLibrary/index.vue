<template>
  <div class="plan-library-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">方案库 // PLAN LIBRARY</h1>
        <p class="subtitle">历史方案与最佳实践案例</p>
      </div>
      <el-button type="primary" size="large" class="cyber-btn">
        <el-icon><Plus /></el-icon>
        新建方案
      </el-button>
    </div>

    <div class="library-content" v-loading="loading" element-loading-background="rgba(0, 0, 0, 0.7)">
      <div class="filter-bar">
        <el-select v-model="filterStatus" placeholder="状态筛选" class="cyber-select" style="width: 150px" popper-class="cyber-dropdown">
          <el-option label="全部" value="all" />
          <el-option label="草稿" value="draft" />
          <el-option label="已验证" value="verified" />
          <el-option label="已部署" value="deployed" />
        </el-select>

        <el-select v-model="filterCategory" placeholder="类别筛选" class="cyber-select" style="width: 150px" popper-class="cyber-dropdown">
          <el-option label="全部类别" value="all" />
          <el-option label="企业合规" value="compliance" />
          <el-option label="合同争议" value="contract" />
          <el-option label="监管应对" value="regulatory" />
        </el-select>

        <el-input
          v-model="searchQuery"
          placeholder="搜索方案..."
          class="cyber-input"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="plans-grid">
        <div
          v-for="plan in filteredPlans"
          :key="plan.id"
          class="plan-card"
        >
          <div class="plan-header">
            <h3>{{ plan.title }}</h3>
            <span class="status-tag" :class="plan.status">{{ plan.statusText }}</span>
          </div>

          <div class="plan-meta">
            <div class="meta-item">
              <span class="label">事件:</span>
              <span class="value">{{ plan.event }}</span>
            </div>
            <div class="meta-item">
              <span class="label">创建时间:</span>
              <span class="value">{{ plan.createdAt }}</span>
            </div>
            <div class="meta-item">
              <span class="label">风险评分:</span>
              <div class="risk-bar-container">
                 <div class="risk-bar" :style="{ width: plan.riskScore + '%', background: getRiskColor(plan.riskScore) }"></div>
              </div>
              <span class="score-val" :style="{ color: getRiskColor(plan.riskScore) }">{{ plan.riskScore }}/100</span>
            </div>
          </div>

          <div class="plan-actions">
            <el-button type="primary" link class="action-btn" @click.stop="viewPlan(plan)">查看详情</el-button>
            <el-button type="info" link class="action-btn" @click.stop="exportPlan(plan)">导出</el-button>
            <el-button type="danger" link class="action-btn delete" @click.stop="deletePlan(plan)">删除</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- Plan Detail Dialog -->
    <el-dialog
      v-model="detailVisible"
      title="方案详情"
      width="60%"
      class="cyber-dialog"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <div class="plan-detail-content" v-loading="detailLoading" element-loading-background="rgba(0, 0, 0, 0.7)">
        <div v-if="currentPlan" class="markdown-preview">
           <div class="md-header">
               <h2>{{ currentPlan.title }}</h2>
               <div class="md-meta">
                   <span>ID: {{ currentPlan.plan_id }}</span>
                   <span class="status-badge" :class="currentPlan.status">{{ currentPlan.status }}</span>
               </div>
           </div>

           <div class="md-body" v-html="renderMarkdown(currentPlan.content)"></div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button class="cyber-btn" @click="detailVisible = false">关闭</el-button>
          <el-button type="primary" class="cyber-btn" @click="exportPlan(currentPlanDetail)">导出方案</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { caseApi } from '@/api/case'
import { ElMessage, ElMessageBox } from 'element-plus'
import { marked } from 'marked'

const searchQuery = ref('')
const filterStatus = ref('all')
const filterCategory = ref('all')
const loading = ref(false)

// Detail Dialog logic
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentPlanDetail = ref<any>(null)

// Computed property for detail view
const currentPlan = computed(() => currentPlanDetail.value)

const plans = ref<any[]>([])

// 加载方案数据
const loadPlans = async () => {
  loading.value = true
  try {
    const response: any = await caseApi.getPlans({ limit: 100 })
    // 转换数据格式
    plans.value = response.map((planData: any) => ({
      id: planData.plan_id, // Use string plan_id for key
      title: planData.title || '未命名方案',
      event: planData.event_name || planData.event_description || '未知事件',
      status: planData.status || 'draft',
      statusText: getStatusText(planData.status),
      createdAt: new Date(planData.created_at).toLocaleDateString('zh-CN'),
      riskScore: planData.risk_score || 0,
      caseId: planData.plan_id
    }))

    // Mock if empty
    if (plans.value.length === 0) {
        plans.value = [
            { id: '1', title: '员工数据泄露事件处置方案', event: '关于员工信息泄露后的合规整改与通知义务...', status: 'verified', statusText: '已验证', createdAt: '2026-01-23', riskScore: 35 },
            { id: '2', title: '供应商违约索赔方案', event: '关于供应商延迟交付与违约责任承担...', status: 'verified', statusText: '已验证', createdAt: '2026-01-15', riskScore: 45 },
            { id: '3', title: '劳动争议仲裁应对', event: '针对员工解除、赔偿与证据整理的应对方案...', status: 'draft', statusText: '草稿', createdAt: '2026-01-24', riskScore: 60 },
        ]
    }
  } catch (error) {
    console.error('Failed to load plans:', error)
    // ElMessage.error('加载方案数据失败')
  } finally {
    loading.value = false
  }
}

const filteredPlans = computed(() => {
  return plans.value.filter(plan => {
    const matchesStatus = filterStatus.value === 'all' || plan.status === filterStatus.value
    const matchesSearch = plan.title.includes(searchQuery.value) || plan.event.includes(searchQuery.value)
    return matchesStatus && matchesSearch
  })
})

const getStatusText = (status: string) => {
    const map: Record<string, string> = {
        'draft': '草稿',
        'verified': '已验证',
        'deployed': '已部署',
        'archived': '已归档'
    }
    return map[status] || status
}

const getRiskColor = (score: number) => {
  if (score < 40) return '#10B981' // Green
  if (score < 70) return '#F59E0B' // Orange
  return '#EF4444' // Red
}

const viewPlan = async (plan: any) => {
    detailVisible.value = true
    detailLoading.value = true
    currentPlanDetail.value = null

    try {
        const res: any = await caseApi.getPlanDetail(plan.id)
        currentPlanDetail.value = res
    } catch (e: any) {
        ElMessage.error(e.message || '获取方案详情失败')
        detailVisible.value = false
    } finally {
        detailLoading.value = false
    }
}

const renderMarkdown = (content: string) => {
    if (!content) return '<p>暂无内容</p>'
    return marked(content)
}

const exportPlan = (plan: any) => {
    if (!plan || (!plan.content && !plan.content_md)) {
        ElMessage.warning('方案内容为空，无法导出')
        return
    }

    // Fallback to title/content if detail not fully loaded context
    const content = plan.content || plan.content_md || ''
    const title = plan.title || '方案'

    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${title}.md`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
}

const deletePlan = (plan: any) => {
    ElMessageBox.confirm(
        '确定要删除该方案吗？此操作无法撤销。',
        '警告',
        {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
          customClass: 'cyber-message-box'
        }
    ).then(async () => {
        try {
            await caseApi.deletePlan(plan.id)
            ElMessage.success('删除成功')
            // Remove from list locally or refresh
            plans.value = plans.value.filter(p => p.id !== plan.id)
        } catch (e: any) {
            ElMessage.error('删除失败: ' + e.message)
        }
    }).catch(() => {
        // Cancelled
    })
}

onMounted(() => {
  loadPlans()
})
</script>

<style>
/* Global overrides for this page's dialog (fixed theme) */
.cyber-dialog {
    background: rgba(15, 23, 42, 0.95) !important;
    backdrop-filter: blur(20px);
    border: 1px solid rgba(59, 130, 246, 0.3);
    box-shadow: 0 0 50px rgba(0, 0, 0, 0.8);
}
.cyber-dialog .el-dialog__header {
    margin-right: 0;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px 24px;
}
.cyber-dialog .el-dialog__title {
    color: #fff;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 1px;
}
.cyber-dialog .el-dialog__body {
    padding: 0;
    color: #E2E8F0;
}
.cyber-dialog .el-dialog__footer {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    padding: 20px 24px;
}
.cyber-dialog .el-button--default {
    background: transparent;
    border: 1px solid rgba(255, 255, 255, 0.2);
    color: #cbd5e1;
}
.cyber-dialog .el-button--default:hover {
    background: rgba(255, 255, 255, 0.1);
    color: #fff;
    border-color: rgba(255, 255, 255, 0.4);
}
</style>

<style scoped>
.plan-library-page {
  padding: 40px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  background: #020617;
  color: #fff;
  font-family: 'Inter', sans-serif;
}
/* ... existing styles ... */
/* Keep only scoped styles not moving to global */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40px;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  font-family: 'Orbitron', sans-serif;
  letter-spacing: 2px;
  background: linear-gradient(90deg, #fff, #94A3B8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  margin: 0;
  color: #94A3B8;
  font-size: 14px;
}

.filter-bar {
  display: flex;
  gap: 20px;
  margin-bottom: 40px;
}

/* Cyber Custom Inputs */
:deep(.cyber-input .el-input__wrapper), :deep(.cyber-select .el-input__wrapper) {
    background: rgba(30, 41, 59, 0.5) !important;
    box-shadow: none !important;
    border: 1px solid rgba(255,255,255,0.1);
    color: #fff;
}
:deep(.cyber-input .el-input__inner), :deep(.cyber-select .el-input__inner) { color: #fff; }

.cyber-btn {
    background: #3B82F6;
    border: none;
    font-weight: 600;
    font-family: 'Orbitron', sans-serif;
    letter-spacing: 1px;
}
.cyber-btn:hover { background: #2563EB; box-shadow: 0 0 15px rgba(59, 130, 246, 0.4); }

.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 30px;
}

.plan-card {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  padding: 24px;
  transition: all 0.3s;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

.plan-card:hover {
  transform: translateY(-4px);
  border-color: rgba(59, 130, 246, 0.4);
  background: rgba(30, 41, 59, 0.6);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.plan-card::before {
    content: ''; position: absolute; top: 0; left: 0; width: 2px; height: 100%; background: #3B82F6; opacity: 0; transition: opacity 0.3s;
}
.plan-card:hover::before { opacity: 1; }

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}

.plan-header h3 {
  margin: 0;
  font-size: 18px;
  flex: 1;
  color: #fff;
  font-weight: 600;
  line-height: 1.4;
}

.status-tag {
    font-size: 11px; padding: 2px 8px; border-radius: 4px; border: 1px solid;
}
.status-tag.verified { background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3); color: #34D399; }
.status-tag.draft { background: rgba(148, 163, 184, 0.1); border-color: rgba(148, 163, 184, 0.3); color: #CBD5E1; }
.status-tag.deployed { background: rgba(59, 130, 246, 0.1); border-color: rgba(59, 130, 246, 0.3); color: #60A5FA; }

.plan-meta {
  margin-bottom: 20px;
  display: flex; flex-direction: column; gap: 10px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
}

.meta-item .label {
  color: #94A3B8;
  min-width: 70px;
}
.meta-item .value { color: #E2E8F0; }

.risk-bar-container {
    width: 100px; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden;
}
.risk-bar { height: 100%; border-radius: 3px; }
.score-val { font-size: 12px; font-weight: 700; margin-left: 8px; }

.plan-actions {
  display: flex;
  gap: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255,255,255,0.1);
}
.action-btn { font-size: 13px; font-weight: 500; }
.action-btn:hover { text-decoration: underline; }
.action-btn.delete { color: #EF4444; }
.action-btn.delete:hover { color: #F87171; }

.plan-detail-content {
    min-height: 300px;
    padding: 20px 40px;
    color: #E2E8F0;
    max-height: 70vh;
    overflow-y: auto;
}
.md-header {
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}
.md-meta {
    display: flex; gap: 20px; margin-top: 16px; color: #94A3B8; font-size: 14px;
}
.status-badge {
    padding: 2px 10px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    font-size: 12px;
}

/* Markdown Styles */
:deep(.md-body h1) { font-size: 26px; margin: 30px 0 20px; color: #fff; font-weight: 700; }
:deep(.md-body h2) {
    font-size: 22px;
    margin: 30px 0 16px;
    color: #60A5FA;
    border-left: 4px solid #3B82F6;
    padding-left: 16px;
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), transparent);
    padding-top: 8px;
    padding-bottom: 8px;
    border-radius: 0 4px 4px 0;
}
:deep(.md-body h3) { font-size: 18px; margin: 24px 0 12px; color: #E2E8F0; font-weight: 600; }
:deep(.md-body p) { font-size: 16px; line-height: 1.8; margin-bottom: 16px; color: #CBD5E1; text-align: justify; }
:deep(.md-body ul), :deep(.md-body ol) { padding-left: 24px; margin-bottom: 16px; color: #CBD5E1; }
:deep(.md-body li) { margin-bottom: 8px; line-height: 1.6; }
:deep(.md-body strong) { color: #fff; font-weight: 700; color: #60A5FA; }
:deep(.md-body blockquote) {
    border-left: 4px solid #64748B;
    margin: 20px 0;
    padding: 10px 20px;
    background: rgba(100, 116, 139, 0.1);
    color: #94A3B8;
}
:deep(.md-body code) {
    background: rgba(0, 0, 0, 0.3);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'JetBrains Mono', monospace;
    color: #E2E8F0;
    font-size: 0.9em;
}

/* Scrollbar */
.plan-detail-content::-webkit-scrollbar { width: 8px; }
.plan-detail-content::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
.plan-detail-content::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.2); border-radius: 4px; }
.plan-detail-content::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.3); }
</style>
