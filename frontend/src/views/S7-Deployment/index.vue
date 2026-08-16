<template>
  <div class="deployment-page">
    <el-page-header @back="goToDashboard" title="返回首页" class="page-header">
      <template #content>
        <span class="page-title">S7 方案落地与动态更新</span>
      </template>
    </el-page-header>

    <div class="main-content">
      <el-card class="status-card" v-if="deployStatus !== 'failed'">
        <div class="status-content">
          <el-icon class="status-icon" :class="deployStatus"><component :is="statusIcon" /></el-icon>
          <div class="status-text">
            <h2>{{ statusTitle }}</h2>
            <p>{{ statusDesc }}</p>
          </div>
          <div class="status-meta">
            <div class="meta-item">
              <span class="label">方案版本</span>
              <span class="value">V1.1</span>
            </div>
            <div class="meta-item">
              <span class="label">部署时间</span>
              <span class="value">{{ deployTime }}</span>
            </div>
            <div class="meta-item">
              <span class="label">运行状态</span>
              <span class="value active">监控中</span>
            </div>
          </div>
        </div>
      </el-card>

      <div class="dashboard-grid">
        <div class="log-panel">
          <h3><el-icon><Monitor /></el-icon> 实时动态监测</h3>
          <el-timeline>
            <el-timeline-item
              v-for="(log, index) in logs"
              :key="index"
              :type="log.type"
              :color="log.color"
              :timestamp="log.time"
              placement="top"
            >
              <h4>{{ log.title }}</h4>
              <p>{{ log.content }}</p>
            </el-timeline-item>
          </el-timeline>
        </div>

        <div class="feedback-panel">
          <h3><el-icon><DataLine /></el-icon> 实战效果评估</h3>
          <div class="metric-grid">
            <div class="metric-card">
              <div class="value">92%</div>
              <div class="label">方案执行率</div>
            </div>
            <div class="metric-card">
              <div class="value down">-15%</div>
              <div class="label">舆情敏感度</div>
            </div>
            <div class="metric-card">
              <div class="value up">+30%</div>
              <div class="label">法律主动权</div>
            </div>
          </div>

          <div class="alert-box" v-if="newTrigger">
            <el-alert
              title="监测到新的争议升级"
              type="error"
              show-icon
              description="对方新增陈述、证据或监管材料，建议立即启动新一轮分析。"
              :closable="false"
            >
              <div class="alert-action">
                <el-button type="danger" size="small" @click="startNewCycle">启动 S1 态势研判</el-button>
              </div>
            </el-alert>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Loading, CircleCheck, CircleClose, Monitor, DataLine } from '@element-plus/icons-vue'

const router = useRouter()
const deployStatus = ref<'deploying' | 'active' | 'failed'>('deploying')
const logs = ref<any[]>([])
const newTrigger = ref(false)
const deployTime = ref('')

const statusIcon = computed(() => {
  if (deployStatus.value === 'deploying') return Loading
  if (deployStatus.value === 'active') return CircleCheck
  return CircleClose
})

const statusTitle = computed(() => {
  if (deployStatus.value === 'deploying') return '方案部署中...'
  if (deployStatus.value === 'active') return '方案已落地运行'
  return '部署失败'
})

const statusDesc = computed(() => {
  if (deployStatus.value === 'deploying') return '正在同步执行指令并启动全链路监测。'
  if (deployStatus.value === 'active') return '核心流程已上线，系统正在持续接收执行反馈。'
  return '部署流程异常，请检查服务状态和配置项。'
})

const goToDashboard = () => {
  router.push('/situation')
}

const startNewCycle = () => {
  router.push('/situation')
}

onMounted(() => {
  deployTime.value = new Date().toLocaleString('zh-CN')

  logs.value.push({
    type: 'primary',
    time: new Date().toLocaleTimeString('zh-CN'),
    title: '部署指令已下发',
    content: '系统开始执行方案自动部署流程。'
  })

  setTimeout(() => {
    deployStatus.value = 'active'
    addLog('success', '#10b981', '系统部署完成', '方案 V1.1 已同步到相关执行节点。')
    simulateDynamicUpdates()
  }, 2000)
})

const addLog = (type: string, color: string, title: string, content: string) => {
  logs.value.unshift({
    type,
    color,
    title,
    content,
    time: new Date().toLocaleTimeString('zh-CN')
  })
}

const simulateDynamicUpdates = () => {
  setTimeout(() => {
    addLog('info', '#3b82f6', '收到执行反馈', '一线处理团队已确认接收并开始执行方案。')
  }, 4000)

  setTimeout(() => {
    addLog('warning', '#e6a23c', '舆情波动提醒', '相关话题热度出现上升，建议同步关注外部传播情况。')
  }, 7000)

  setTimeout(() => {
    newTrigger.value = true
    addLog('danger', '#f56c6c', '突发事件预警', '监测到对方新增动作，建议重新进入态势分析。')
  }, 10000)
}
</script>

<style scoped>
.deployment-page {
  min-height: 100vh;
  background: var(--color-bg-primary);
  display: flex;
  flex-direction: column;
}
.page-header {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  padding: var(--spacing-md) var(--spacing-lg);
}
.page-title {
  font-size: 18px;
  font-weight: 600;
}
.main-content {
  flex: 1;
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}
.status-card,
.log-panel,
.feedback-panel {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
}
.status-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}
.status-icon { font-size: 64px; }
.status-icon.deploying { animation: rotate 2s linear infinite; color: var(--color-primary); }
.status-icon.active { color: #22c55e; }
.status-icon.failed { color: #ef4444; }
.dashboard-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: var(--spacing-lg);
}
.log-panel,
.feedback-panel { padding: 20px; }
.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin: 16px 0;
}
.metric-card {
  background: rgba(15, 23, 42, 0.7);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}
.value { font-size: 28px; font-weight: 700; }
.value.down { color: #f87171; }
.value.up { color: #4ade80; }
.label { color: #94a3b8; }
.active { color: #4ade80; }
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
</style>
