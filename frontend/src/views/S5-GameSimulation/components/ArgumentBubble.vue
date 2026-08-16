<template>
  <div class="simulation-card" :class="side">
    <div class="card-role-label">
      <span v-if="side === 'our'" class="badge blue">我方</span>
      <span v-else-if="side === 'opponent'" class="badge red">对方</span>
      <span v-else class="badge gold">裁判</span>
      <span class="role-name">{{ agentName }}</span>
      <span class="time-mark">{{ timestamp }}</span>
    </div>

    <div class="card-body">
      <div class="argument-text">
        <span class="prefix-label">
          {{ side === 'our' ? '我方主张：' : (side === 'judge' ? '裁判意见：' : '对方主张：') }}
        </span>
        {{ content }}
      </div>

      <div class="legal-basis-section" v-if="legalBasis && legalBasis.length">
        <div class="section-title">
          <el-icon><CollectionTag /></el-icon> 法律依据
        </div>
        <ul class="basis-list">
          <li v-for="(item, idx) in normalizedBasis" :key="idx">{{ item }}</li>
        </ul>
      </div>

      <div class="risk-section" v-if="risks && risks.length">
        <div class="section-title risk">
          <el-icon><Warning /></el-icon> 潜在风险
        </div>
        <ul class="risk-list">
          <li v-for="(item, idx) in risks" :key="idx">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CollectionTag, Warning } from '@element-plus/icons-vue'

const props = defineProps<{
  side: 'our' | 'opponent' | 'judge'
  agentName: string
  content: string
  legalBasis?: string | string[]
  risks?: string[]
  timestamp: string
}>()

const normalizedBasis = computed(() => {
  if (!props.legalBasis) return []
  return Array.isArray(props.legalBasis) ? props.legalBasis : [props.legalBasis]
})
</script>

<style scoped>
.simulation-card {
  margin-bottom: 20px;
  background: rgba(30, 41, 59, 0.4);
  border-radius: 8px;
  border-left: 4px solid transparent;
  overflow: hidden;
  animation: fadeIn 0.4s ease;
}
.simulation-card.our { border-color: #3B82F6; background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), transparent); }
.simulation-card.opponent { border-color: #EF4444; background: linear-gradient(90deg, rgba(239, 68, 68, 0.1), transparent); }
.simulation-card.judge { border-color: #F59E0B; background: linear-gradient(90deg, rgba(245, 158, 11, 0.1), transparent); }
.card-role-label {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.badge { font-size: 10px; padding: 2px 6px; border-radius: 2px; font-weight: bold; }
.badge.blue { background: #3B82F6; color: #fff; }
.badge.red { background: #EF4444; color: #fff; }
.badge.gold { background: #F59E0B; color: #000; }
.role-name { font-weight: 700; font-size: 13px; color: #fff; letter-spacing: 0.5px; }
.time-mark { margin-left: auto; font-size: 11px; color: #64748B; font-family: monospace; }
.card-body { padding: 16px; font-size: 13px; color: #E2E8F0; line-height: 1.6; white-space: pre-wrap; }
.prefix-label { font-weight: bold; margin-right: 4px; opacity: 0.8; }
.legal-basis-section { margin-top: 12px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 4px; }
.section-title { font-size: 11px; color: #60A5FA; display: flex; align-items: center; gap: 6px; margin-bottom: 6px; font-weight: 600; }
.basis-list { margin: 0; padding-left: 16px; list-style-type: disc; }
.basis-list li { color: #93C5FD; font-size: 12px; margin-bottom: 2px; }
.risk-section { margin-top: 8px; background: rgba(239, 68, 68, 0.1); padding: 10px; border-radius: 4px; }
.section-title.risk { color: #F87171; }
.risk-list { margin: 0; padding-left: 16px; list-style-type: square; color: #FCA5A5; font-size: 12px; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
