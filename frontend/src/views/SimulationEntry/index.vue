<template>
  <div class="simulation-entry">
    <div class="page-header">
      <h1>⚖️ 博弈推演中心</h1>
      <p class="subtitle">选择已生成的分析方案，进入红蓝对抗推演与结果验证。</p>
    </div>

    <div class="content-wrapper" v-loading="loading">
      <div class="process-guide">
        <h2 class="section-title">推演流程</h2>
        <div class="process-steps">
          <div class="process-step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h3>选择方案</h3>
              <p>从方案库中选择待验证的分析方案</p>
            </div>
          </div>
          <div class="process-arrow">→</div>
          <div class="process-step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h3>配置规则</h3>
              <p>设置参与智能体、推演轮次和约束条件</p>
            </div>
          </div>
          <div class="process-arrow">→</div>
          <div class="process-step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h3>开始推演</h3>
              <p>模拟多智能体博弈、质证与回应过程</p>
            </div>
          </div>
          <div class="process-arrow">→</div>
          <div class="process-step">
            <div class="step-number">4</div>
            <div class="step-content">
              <h3>查看结果</h3>
              <p>输出风险评估、结论摘要与优化建议</p>
            </div>
          </div>
        </div>
      </div>

      <div class="plans-section">
        <h2 class="section-title">可用方案</h2>

        <el-tabs v-model="activeTab" class="plans-tabs">
          <el-tab-pane label="待推演" name="pending">
            <div class="plans-grid">
              <div
                v-for="plan in filteredPlans('draft')"
                :key="plan.id"
                class="plan-card"
                @click="selectPlan(plan)"
              >
                <div class="plan-header">
                  <el-tag type="info" size="small">草稿</el-tag>
                  <span class="plan-date">{{ formatDate(plan.created_at) }}</span>
                </div>
                <h3>{{ plan.title }}</h3>
                <p class="plan-desc">{{ plan.description }}</p>
                <div class="plan-meta">
                  <span class="meta-item">
                    <el-icon><Document /></el-icon>
                    关联事件：{{ plan.event_title || '未命名事件' }}
                  </span>
                  <span class="meta-item">
                    <el-icon><User /></el-icon>
                    {{ plan.agents_count || 0 }} 个智能体
                  </span>
                </div>
                <div class="card-action">
                  <el-button type="primary" size="small">
                    开始推演<el-icon class="el-icon--right"><VideoPlay /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="已推演" name="simulated">
            <div class="plans-grid">
              <div
                v-for="plan in filteredPlans('verified')"
                :key="plan.id"
                class="plan-card verified"
                @click="viewSimulation(plan)"
              >
                <div class="plan-header">
                  <el-tag type="success" size="small">已验证</el-tag>
                  <span class="plan-date">{{ formatDate(plan.updated_at) }}</span>
                </div>
                <h3>{{ plan.title }}</h3>
                <p class="plan-desc">{{ plan.description }}</p>
                <div class="simulation-result">
                  <div class="result-item">
                    <span class="label">推演轮次：</span>
                    <span class="value">{{ plan.simulation_rounds || 5 }} 轮</span>
                  </div>
                  <div class="result-item">
                    <span class="label">风险评分：</span>
                    <span class="value" :class="getRiskClass(plan.risk_score)">
                      {{ plan.risk_score || 6.5 }}
                    </span>
                  </div>
                </div>
                <div class="card-action">
                  <el-button type="success" size="small" plain>
                    查看结果 <el-icon class="el-icon--right"><View /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <el-tab-pane label="全部" name="all">
            <div class="plans-grid">
              <div
                v-for="plan in allPlans"
                :key="plan.id"
                class="plan-card"
                @click="handlePlanClick(plan)"
              >
                <div class="plan-header">
                  <el-tag :type="getStatusType(plan.status)" size="small">
                    {{ getStatusLabel(plan.status) }}
                  </el-tag>
                  <span class="plan-date">{{ formatDate(plan.created_at) }}</span>
                </div>
                <h3>{{ plan.title }}</h3>
                <p class="plan-desc">{{ plan.description }}</p>
                <div class="card-action">
                  <el-button
                    :type="plan.status === 'draft' ? 'primary' : 'success'"
                    size="small"
                    :plain="plan.status !== 'draft'"
                  >
                    {{ plan.status === 'draft' ? '开始推演' : '查看结果' }}
                  </el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <el-empty v-if="allPlans.length === 0 && !loading" description="暂无可用方案">
          <el-button type="primary" @click="goToSituation">
            前往态势首页创建事件
          </el-button>
        </el-empty>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document, User, VideoPlay, View } from '@element-plus/icons-vue'
import { planApi } from '@/api/plan'

const router = useRouter()
const loading = ref(false)
const activeTab = ref('pending')
const allPlans = ref<any[]>([])

const loadPlans = async () => {
  loading.value = true
  try {
    const data = await planApi.getPlans()
    allPlans.value = data as any
  } catch (error) {
    ElMessage.error('加载方案失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const filteredPlans = (status: string) => {
  return allPlans.value.filter(p => p.status === status)
}

const selectPlan = (plan: any) => {
  router.push(`/game-simulation/${plan.id}`)
}

const viewSimulation = (plan: any) => {
  router.push(`/game-simulation/${plan.id}`)
}

const handlePlanClick = (plan: any) => {
  if (plan.status === 'draft') {
    selectPlan(plan)
  } else {
    viewSimulation(plan)
  }
}

const goToSituation = () => {
  router.push('/situation')
}

const getStatusLabel = (status: string) => {
  const labels: Record<string, string> = {
    draft: '草稿',
    verified: '已验证',
    deployed: '已部署'
  }
  return labels[status] || status
}

const getStatusType = (status: string) => {
  const types: Record<string, any> = {
    draft: 'info',
    verified: 'success',
    deployed: 'warning'
  }
  return types[status] || 'info'
}

const getRiskClass = (score: number) => {
  if (score >= 8) return 'high-risk'
  if (score >= 5) return 'medium-risk'
  return 'low-risk'
}

const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadPlans()
})
</script>

<style scoped>
.simulation-entry {
  min-height: 100vh;
  padding: 32px;
  background: #020617;
  color: #fff;
}
.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  margin: 0 0 8px;
  font-size: 30px;
}
.subtitle {
  color: #94a3b8;
}
.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.process-guide,
.plans-section {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 16px;
  padding: 24px;
}
.section-title {
  margin: 0 0 20px;
  font-size: 20px;
}
.process-steps {
  display: grid;
  grid-template-columns: repeat(7, auto);
  gap: 12px;
  align-items: center;
}
.process-step {
  background: rgba(30, 41, 59, 0.8);
  border-radius: 12px;
  padding: 16px;
  min-width: 180px;
}
.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin-bottom: 12px;
}
.process-arrow {
  color: #60a5fa;
  font-size: 24px;
  text-align: center;
}
.plans-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.plan-card {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 14px;
  padding: 18px;
  cursor: pointer;
}
.plan-card.verified {
  border-color: rgba(16, 185, 129, 0.35);
}
.plan-header,
.plan-meta,
.result-item,
.card-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.plan-desc {
  color: #cbd5e1;
  min-height: 44px;
}
.plan-meta {
  flex-direction: column;
  align-items: flex-start;
  color: #94a3b8;
  margin-bottom: 16px;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}
.simulation-result {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
  color: #cbd5e1;
}
.high-risk { color: #f87171; }
.medium-risk { color: #fbbf24; }
.low-risk { color: #4ade80; }
@media (max-width: 1100px) {
  .process-steps {
    grid-template-columns: 1fr;
  }
  .process-arrow {
    transform: rotate(90deg);
  }
}
</style>
