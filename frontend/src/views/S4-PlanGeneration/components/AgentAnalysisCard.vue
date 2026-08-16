<template>
  <div class="agent-analysis-card" :class="status">
    <div class="card-header">
      <div class="avatar-ring">
        <img :src="agent.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${agent.id}`" alt="avatar" />
        <div class="status-indicator"></div>
      </div>
      <div class="header-info">
        <div class="name-row">
          <span class="agent-name">{{ agent.name }}</span>
          <span class="agent-role">{{ agent.type || '法律专家' }}</span>
        </div>
        <div class="status-text">{{ statusText }}</div>
      </div>
    </div>

    <div v-if="sources.length" class="source-hit-box">
      <div class="source-hit-title">检索命中</div>
      <div class="source-summary">
        <span class="summary-chip">类案 {{ caseCount }}</span>
        <span class="summary-chip law">法规 {{ lawCount }}</span>
      </div>
      <div class="source-hit-list">
        <span v-for="(source, idx) in sources.slice(0, 4)" :key="idx" class="source-chip">{{ source }}</span>
      </div>
    </div>

    <div class="log-container custom-scrollbar" ref="logContainer">
      <div v-for="(log, idx) in logs" :key="idx" class="log-line">
        <span class="log-time">[{{ log.time }}]</span>
        <span class="log-content">{{ log.content }}</span>
      </div>
      <div v-if="status === 'retrieving' || status === 'generating'" class="typing-indicator">
        <span></span><span></span><span></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import type { Agent } from '@/types'

const props = defineProps<{
  agent: Agent
  status: 'pending' | 'retrieving' | 'generating' | 'completed' | 'error'
  logs: Array<{ time: string; content: string }>
  sources: string[]
}>()

const logContainer = ref<HTMLElement | null>(null)

const statusText = computed(() => {
  switch (props.status) {
    case 'pending': return '等待中...'
    case 'retrieving': return '检索中...'
    case 'generating': return '生成中...'
    case 'completed': return '分析完成'
    case 'error': return '执行失败'
    default: return ''
  }
})
const caseCount = computed(() => props.sources.filter(item => item.includes('[Case-')).length)
const lawCount = computed(() => props.sources.filter(item => item.includes('[Law-')).length)

watch(() => props.logs.length, () => {
  nextTick(() => {
    if (logContainer.value) logContainer.value.scrollTop = logContainer.value.scrollHeight
  })
})
</script>

<style scoped>
.agent-analysis-card { background: rgba(20, 27, 45, 0.4); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 4px; padding: 12px; display: flex; flex-direction: column; gap: 10px; transition: all 0.3s; }
.agent-analysis-card.retrieving, .agent-analysis-card.generating { border-color: #3b82f6; background: rgba(30, 58, 138, 0.2); box-shadow: 0 0 15px rgba(59, 130, 246, 0.2) inset; }
.agent-analysis-card.completed { border-color: #10b981; background: rgba(6, 78, 59, 0.2); }
.agent-analysis-card.error { border-color: #ef4444; background: rgba(127, 29, 29, 0.2); }
.card-header { display: flex; align-items: center; gap: 12px; }
.avatar-ring { width: 36px; height: 36px; position: relative; border-radius: 50%; padding: 2px; background: rgba(255, 255, 255, 0.1); }
.avatar-ring img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
.status-indicator { position: absolute; bottom: 0; right: 0; width: 8px; height: 8px; border-radius: 50%; background: #6b7280; border: 2px solid #0b1026; }
.retrieving .status-indicator, .generating .status-indicator { background: #3b82f6; box-shadow: 0 0 5px #3b82f6; }
.completed .status-indicator { background: #10b981; box-shadow: 0 0 5px #10b981; }
.error .status-indicator { background: #ef4444; box-shadow: 0 0 5px #ef4444; }
.header-info { flex: 1; }
.name-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 2px; }
.agent-name { font-size: 13px; font-weight: 600; color: #fff; }
.agent-role { font-size: 10px; color: rgba(255, 255, 255, 0.5); border: 1px solid rgba(255, 255, 255, 0.2); padding: 0 4px; border-radius: 2px; }
.status-text { font-size: 11px; color: #9ca3af; }
.retrieving .status-text, .generating .status-text { color: #60a5fa; }
.completed .status-text { color: #34d399; }
.error .status-text { color: #fca5a5; }
.source-hit-box { background: rgba(0, 0, 0, 0.18); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 4px; padding: 8px; }
.source-hit-title { font-size: 10px; color: #93c5fd; margin-bottom: 6px; }
.source-summary { display: flex; gap: 6px; margin-bottom: 6px; flex-wrap: wrap; }
.summary-chip { font-size: 10px; color: #bfdbfe; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59,130,246,0.2); padding: 2px 6px; border-radius: 999px; }
.summary-chip.law { color: #fde68a; background: rgba(234, 179, 8, 0.12); border-color: rgba(234,179,8,0.28); }
.source-hit-list { display: flex; flex-wrap: wrap; gap: 6px; }
.source-chip { font-size: 10px; color: #cbd5e1; background: rgba(59, 130, 246, 0.12); border: 1px solid rgba(59, 130, 246, 0.2); padding: 2px 6px; border-radius: 999px; }
.log-container { height: 80px; background: rgba(0, 0, 0, 0.3); border-radius: 2px; padding: 6px; overflow-y: auto; font-family: monospace; }
.log-line { font-size: 10px; color: #9ca3af; line-height: 1.4; margin-bottom: 2px; }
.log-time { color: #4b5563; margin-right: 4px; }
.retrieving .log-content, .generating .log-content { color: #e5e7eb; }
.typing-indicator span { display: inline-block; width: 3px; height: 3px; background-color: #60a5fa; border-radius: 50%; animation: typing 1s infinite; margin-right: 2px; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing { 0% { transform: translateY(0); } 50% { transform: translateY(-3px); } 100% { transform: translateY(0); } }
</style>
