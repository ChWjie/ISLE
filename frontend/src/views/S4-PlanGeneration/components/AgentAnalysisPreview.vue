<template>
  <div class="agent-preview-card">
    <div class="card-header">
      <div class="agent-info">
        <div class="avatar">{{ agent.icon || '⚖️' }}</div>
        <div class="title-col">
          <h3>{{ agent.name }}</h3>
          <span class="role-tag">{{ agent.role || '法律专家' }}</span>
        </div>
      </div>
      <div class="status-badge" :class="status">{{ statusText }}</div>
    </div>

    <div class="card-body custom-scrollbar">
      <div v-if="status === 'pending'" class="pending-state">
        <el-icon class="is-loading"><Loading /></el-icon>
        等待启动...
      </div>
      <div v-else-if="status === 'retrieving' || status === 'generating'" class="analyzing-state">
        <div class="typing-indicator"><span></span><span></span><span></span></div>
        <div class="stage-chip" :class="status === 'retrieving' ? 'retrieving' : 'generating'">
          {{ status === 'retrieving' ? '得理类案/法规检索中' : '法律分析生成中' }}
        </div>
        <div v-if="sources.length" class="retrieval-summary">
          <span class="summary-chip">类案 {{ caseCount }}</span>
          <span class="summary-chip law">法规 {{ lawCount }}</span>
        </div>
        <p class="current-log">{{ currentLog }}</p>
        <div v-if="sources.length" class="retrieval-panel">
          <div class="retrieval-title">命中来源</div>
          <div class="retrieval-items">
            <div v-for="(source, idx) in sources.slice(0, 5)" :key="idx" class="retrieval-item">{{ source }}</div>
          </div>
        </div>
      </div>
      <div v-else class="result-content">
        <div v-if="sources.length" class="retrieval-panel result-sources">
          <div class="retrieval-title">检索命中</div>
          <div class="retrieval-items">
            <div v-for="(source, idx) in sources.slice(0, 5)" :key="idx" class="retrieval-item">{{ source }}</div>
          </div>
        </div>
        <div v-if="result?.analysis" class="analysis-text">{{ result.analysis }}</div>
        <div v-else class="empty-state">暂无分析结果</div>
      </div>
    </div>

    <div class="card-footer">
      <el-button link type="primary" size="small" @click="showReport = true">查看完整报告</el-button>
    </div>

    <el-dialog v-model="showReport" :title="`${agent.name} - 深度法律分析报告`" width="800px" class="report-dialog" append-to-body>
      <div class="report-content custom-scrollbar" v-html="renderedContent"></div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showReport = false">关闭</el-button>
          <el-button type="primary" @click="copyReport">复制内容</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'

const props = defineProps<{
  agent: any
  status: 'pending' | 'retrieving' | 'generating' | 'completed' | 'error'
  logs: Array<{ time: string; content: string }>
  result?: { analysis?: string } | null
  sources: string[]
}>()

const showReport = ref(false)
const statusText = computed(() => ({ pending: '等待中', retrieving: '检索中', generating: '生成中', completed: '已完成', error: '失败' }[props.status] || '未知'))
const currentLog = computed(() => props.logs.length ? (props.logs[props.logs.length - 1]?.content || '正在初始化...') : '正在初始化...')
const caseCount = computed(() => props.sources.filter(item => item.includes('[Case-')).length)
const lawCount = computed(() => props.sources.filter(item => item.includes('[Law-')).length)
const renderedContent = computed(() => {
  if (!props.result?.analysis) return '<div class="empty">暂无内容</div>'
  try { return marked.parse(props.result.analysis) } catch { return props.result.analysis }
})

const copyReport = async () => {
  if (!props.result?.analysis) return
  try {
    await navigator.clipboard.writeText(props.result.analysis)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}
</script>

<style scoped>
.agent-preview-card { background: rgba(11, 16, 38, 0.6); border: 1px solid rgba(59, 130, 246, 0.3); border-radius: 4px; display: flex; flex-direction: column; height: 320px; overflow: hidden; }
.card-header { padding: 12px 16px; background: rgba(30, 58, 138, 0.2); border-bottom: 1px solid rgba(59, 130, 246, 0.2); display: flex; justify-content: space-between; align-items: center; }
.agent-info { display: flex; gap: 10px; align-items: center; }
.avatar { font-size: 24px; }
.title-col h3 { margin: 0; font-size: 14px; color: #fff; }
.role-tag { font-size: 10px; background: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 1px 4px; border-radius: 2px; }
.status-badge { font-size: 11px; padding: 2px 6px; border-radius: 2px; }
.status-badge.pending { color: #94a3b8; background: rgba(148, 163, 184, 0.1); }
.status-badge.retrieving, .status-badge.generating { color: #fbbf24; background: rgba(251, 191, 36, 0.1); }
.status-badge.completed { color: #34d399; background: rgba(52, 211, 153, 0.1); }
.status-badge.error { color: #fca5a5; background: rgba(239, 68, 68, 0.12); }
.card-body { flex: 1; padding: 16px; overflow-y: auto; font-size: 12px; color: #cbd5e1; line-height: 1.6; }
.pending-state, .analyzing-state { height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px; color: #64748b; }
.stage-chip { font-size: 11px; padding: 4px 10px; border-radius: 999px; border: 1px solid rgba(59, 130, 246, 0.25); }
.stage-chip.retrieving { color: #fde68a; background: rgba(234, 179, 8, 0.12); border-color: rgba(234, 179, 8, 0.32); }
.stage-chip.generating { color: #93c5fd; background: rgba(59, 130, 246, 0.12); }
.retrieval-summary { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.summary-chip { font-size: 11px; color: #bfdbfe; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59,130,246,0.25); border-radius: 999px; padding: 3px 8px; }
.summary-chip.law { color: #fde68a; background: rgba(234, 179, 8, 0.12); border-color: rgba(234,179,8,0.28); }
.current-log { text-align: center; margin: 0; color: #cbd5e1; }
.retrieval-panel { width: 100%; margin-top: 8px; background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 4px; padding: 8px; }
.retrieval-title { font-size: 11px; color: #93c5fd; margin-bottom: 6px; }
.retrieval-items { display: flex; flex-direction: column; gap: 4px; }
.retrieval-item { font-size: 11px; color: #e2e8f0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.analysis-text { white-space: pre-wrap; line-height: 1.8; color: #e2e8f0; display: -webkit-box; -webkit-line-clamp: 8; -webkit-box-orient: vertical; overflow: hidden; text-overflow: ellipsis; }
.result-sources { margin-bottom: 12px; }
.empty-state { text-align: center; color: #64748b; padding: 40px 20px; }
.card-footer { padding: 8px 16px; border-top: 1px solid rgba(59, 130, 246, 0.2); text-align: right; background: rgba(0, 0, 0, 0.1); }
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.2); border-radius: 2px; }
.typing-indicator span { display: inline-block; width: 4px; height: 4px; background: #60a5fa; border-radius: 50%; margin: 0 2px; animation: bounce 1.4s infinite ease-in-out both; }
.typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
.typing-indicator span:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }
</style>

<style>
.report-dialog.el-dialog { background: #0f172a !important; border: 1px solid rgba(59, 130, 246, 0.3) !important; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important; }
.report-dialog .el-dialog__header { border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-right: 0 !important; padding-bottom: 20px; }
.report-dialog .el-dialog__title { color: #fff !important; font-size: 18px; font-weight: 600; }
.report-dialog .el-dialog__close { color: #94a3b8 !important; }
.report-dialog .el-dialog__close:hover { color: #fff !important; }
.report-dialog .el-dialog__body { padding: 20px 30px !important; color: #cbd5e1 !important; background: #0f172a !important; }
.report-content { max-height: 60vh; overflow-y: auto; font-size: 15px; line-height: 1.8; color: #cbd5e1 !important; padding-right: 10px; }
.report-content h1, .report-content h2, .report-content h3 { color: #60a5fa !important; margin-top: 1.5em; margin-bottom: 0.8em; font-weight: 700; }
.report-content h1 { font-size: 20px; border-bottom: 1px solid rgba(59, 130, 246, 0.3); padding-bottom: 8px; }
.report-content h2 { font-size: 18px; }
.report-content h3 { font-size: 16px; color: #93c5fd !important; }
.report-content p { margin-bottom: 1em; color: #cbd5e1 !important; }
.report-content strong { color: #fff !important; font-weight: 700; background: rgba(255, 255, 255, 0.05); padding: 0 4px; border-radius: 2px; }
.report-content ul, .report-content ol { padding-left: 20px; margin-bottom: 1em; color: #cbd5e1 !important; }
.report-content li { margin-bottom: 0.5em; }
.report-content blockquote { border-left: 4px solid #3b82f6; background: rgba(59, 130, 246, 0.1); padding: 8px 16px; margin: 1em 0; color: #e2e8f0; font-style: italic; border-radius: 0 4px 4px 0; }
</style>
