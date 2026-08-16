<template>
  <div class="s6-optimization-page">
    <div class="opt-header">
       <button class="back-btn" @click="$router.push('/simulation')">
          <el-icon><ArrowLeft /></el-icon> 返回推演
       </button>
       <h1 class="page-title">方案优化引擎</h1>
       <div class="header-actions">
           <el-button type="primary" @click="handleApply" :loading="applying" :disabled="!optimizedContent">
               <el-icon><Check /></el-icon> 采纳优化方案
           </el-button>
       </div>
    </div>

    <div class="opt-content" v-loading="loading" element-loading-text="正在基于推演数据重构方案..." element-loading-background="rgba(15, 23, 42, 0.9)">
        <div class="changes-summary" v-if="changesSummary">
            <div class="summary-header">
                <div class="summary-label">优化摘要</div>
                <div class="summary-tag">Optimization Notes</div>
            </div>
            <div class="summary-text markdown-body custom-scroll" v-html="renderMarkdown(formatSummary(changesSummary))"></div>
        </div>

        <div class="diff-container">
            <div class="diff-pane">
                <div class="pane-header">
                    <span class="ph-title">原始方案</span>
                    <span class="ph-tag">Before</span>
                </div>
                <div class="markdown-body custom-scroll" v-html="renderMarkdown(originalContent)"></div>
            </div>

            <div class="diff-pane optimized">
                <div class="pane-header">
                    <span class="ph-title">AI优化方案</span>
                    <span class="ph-tag new">After Simulation</span>
                </div>
                <div class="markdown-body custom-scroll" v-html="renderMarkdown(optimizedContent)"></div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import simulationApi from '@/api/simulation'
import { marked } from 'marked'
import plansApi from '@/api/plans'

const route = useRoute()
const router = useRouter()
const simulationId = route.params.id as string

const loading = ref(true)
const applying = ref(false)
const originalContent = ref('')
const optimizedContent = ref('')
const changesSummary = ref('')
const eventId = ref('')

const normalizeText = (text: string) => {
    if (!text) return ''
    const trimmed = text.trim()
    try {
        const parsed = JSON.parse(trimmed)
        if (typeof parsed === 'string') return parsed
        if (parsed?.optimized_content) return String(parsed.optimized_content)
        if (parsed?.content) return String(parsed.content)
        if (parsed?.changes_summary) return String(parsed.changes_summary)
        return '```json\n' + JSON.stringify(parsed, null, 2) + '\n```'
    } catch {
        return trimmed
    }
}

const renderMarkdown = (text: string) => {
    if (!text) return ''
    return marked(text)
}

const formatSummary = (text: string) => {
    const normalized = normalizeText(text)
    if (!normalized) return ''
    if (normalized.includes('\n') || normalized.includes('- ') || normalized.includes('1.')) return normalized
    return normalized.replace(/。/g, '。\n').replace(/；/g, '；\n')
}

onMounted(async () => {
   if(!simulationId) {
        ElMessage.error('无效的推演ID')
        return
   }

   await generateOptimization()
})

const generateOptimization = async () => {
    try {
        loading.value = true
        const res = await simulationApi.optimizePlan(simulationId)
        originalContent.value = normalizeText(res.original_plan)
        optimizedContent.value = normalizeText(res.optimized_plan)
        changesSummary.value = normalizeText(res.changes_summary)
        if (res.event_id) {
            eventId.value = res.event_id
        }
    } catch (e: any) {
        console.error(e)
        ElMessage.error('优化生成失败: ' + e.message)
    } finally {
        loading.value = false
    }
}

const handleApply = async () => {
    applying.value = true
    try {
        if (!optimizedContent.value) return

        if (!eventId.value) {
             ElMessage.error('无法获取关联事件信息，无法保存')
             return
        }

        const res = await plansApi.savePlan({
            event_id: eventId.value || 'Event-20251222-ECS',
            title: `Optimized Plan ${new Date().toLocaleString()}`,
            content: optimizedContent.value
        })

        ElMessage.success('优化方案已采纳并保存')

        router.push({
            path: '/simulation',
            query: { planId: res.plan_id }
        })

    } catch (e: any) {
        console.error(e)
        ElMessage.error('方案保存失败: ' + e.message)
    } finally {
        applying.value = false
    }
}
</script>

<style scoped>
.s6-optimization-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #020617;
  color: #fff;
  font-family: 'Inter', sans-serif;
}
.opt-header {
  height: 60px;
  background: rgba(15, 23, 42, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}
.back-btn {
    background: none; border: none; color: #94A3B8; cursor: pointer;
    display: flex; align-items: center; gap: 8px; font-size: 14px;
}
.back-btn:hover { color: #fff; }
.page-title {
    font-size: 18px; font-weight: 700; background: linear-gradient(90deg, #3B82F6, #8B5CF6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.opt-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 24px;
    gap: 20px;
    overflow: hidden;
}
.changes-summary {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    min-height: 120px;
}
.summary-header {
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    background: rgba(15, 23, 42, 0.5);
}
.summary-label { font-size: 12px; font-weight: bold; color: #60A5FA; text-transform: uppercase; }
.summary-tag { font-size: 10px; background: #3B82F6; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
.summary-text { max-height: 180px; padding: 18px 20px; overflow-y: auto; }
.diff-container {
    flex: 1;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    overflow: hidden;
    min-height: 0;
}
.diff-pane {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.diff-pane.optimized {
    background: rgba(30, 41, 59, 0.8);
    border-color: rgba(139, 92, 246, 0.3);
    box-shadow: 0 0 20px rgba(139, 92, 246, 0.1);
}
.pane-header {
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    background: rgba(15, 23, 42, 0.5);
}
.ph-title { font-weight: 600; font-size: 14px; color: #CBD5E1; }
.ph-tag { font-size: 10px; background: #64748B; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
.ph-tag.new { background: #8B5CF6; }
.markdown-body {
    flex: 1;
    padding: 24px;
    overflow-y: auto;
    font-size: 14px;
    line-height: 1.7;
    color: #CBD5E1;
    white-space: normal;
    word-break: break-word;
}
.markdown-body :deep(h1), .markdown-body :deep(h2) { border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 8px; margin-bottom: 16px; color: #fff; }
.markdown-body :deep(p) { margin-bottom: 16px; }
.markdown-body :deep(ul), .markdown-body :deep(ol) { padding-left: 20px; margin-bottom: 16px; }
.markdown-body :deep(pre) {
    background: rgba(2, 6, 23, 0.6);
    padding: 14px;
    border-radius: 8px;
    overflow-x: auto;
}
.custom-scroll::-webkit-scrollbar { width: 6px; }
.custom-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 3px; }
</style>
