<template>
  <div class="event-detail-panel" v-if="event">
    <div class="panel-header">
      <div class="header-top">
        <div class="title-row">
          <h1 class="event-title">{{ event.title || event.name }}</h1>
          <span class="risk-badge">重点关注</span>
        </div>
        <div class="header-actions">
          <el-button type="primary" class="analysis-btn" size="small" @click="startAnalysis">进入分析</el-button>
          <div class="close-btn" @click="$emit('close')"><el-icon><Close /></el-icon></div>
        </div>
      </div>
      <div class="tags-row">
        <span class="tag-blue">{{ event.dispute_type || '企业合规' }}</span>
        <span class="tag-outline">{{ event.location_name || '未指定地区' }}</span>
      </div>
      <div class="time-row">{{ formatDate(event.created_at) }}</div>
    </div>

    <div class="section-box">
      <div class="section-title">概览</div>
      <div class="overview-grid">
        <div class="grid-item">
          <span class="label">涉事主体</span>
          <div class="value-tags">
            <span class="v-tag" v-for="party in normalizedParties" :key="party">{{ party }}</span>
          </div>
        </div>
        <div class="grid-item">
          <span class="label">地点</span>
          <span class="value">{{ event.location_name || '未指定' }}<template v-if="event.location">（{{ event.location.lat.toFixed(1) }}, {{ event.location.lng.toFixed(1) }}）</template></span>
        </div>
        <div class="grid-item">
          <span class="label">状态</span>
          <span class="value status-warn">研判中</span>
        </div>
        <div class="grid-item">
          <span class="label">触发信号</span>
          <span class="value">证据补充、监管问询、履约争议升级</span>
        </div>
      </div>
    </div>

    <div class="section-box">
      <div class="section-title">事件详情</div>
      <p class="detail-text">{{ event.description || '暂无详情' }}</p>
      <div class="media-grid" :class="{ 'single-image': !event.imageUrl2 }">
        <img v-if="event.imageUrl" :src="event.imageUrl" class="media-img" alt="Event Image 1" />
        <img v-if="event.imageUrl2" :src="event.imageUrl2" class="media-img" alt="Event Image 2" />
      </div>
    </div>

    <div class="section-box">
      <div class="section-title">相关法规</div>
      <div class="law-list">
        <div class="law-item"><span class="law-name">公司法、劳动合同法、个人信息保护法、数据安全法</span></div>
        <div class="law-item"><span class="law-name">根据案件类型自动推荐更多法规和类案</span></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Close } from '@element-plus/icons-vue'
import type { DisputeEvent } from '@/types'

const props = defineProps<{
  event: DisputeEvent | null
}>()

defineEmits(['close'])
const router = useRouter()

const normalizedParties = computed(() => {
  if (!props.event) return []
  const parties = (props.event as any).parties
  if (Array.isArray(parties) && parties.length) return parties
  return ['我方主体', '对方主体']
})

const startAnalysis = () => {
  if (!props.event) return
  router.push(`/agent-config/${props.event.event_id || props.event.id}`)
}

const formatDate = (date: any) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.event-detail-panel { display: flex; flex-direction: column; gap: 16px; color: #fff; }
.panel-header, .section-box {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 14px;
  padding: 16px;
}
.header-top { display: flex; justify-content: space-between; gap: 12px; }
.title-row, .tags-row, .overview-grid, .header-actions { display: flex; gap: 10px; flex-wrap: wrap; }
.event-title { margin: 0; font-size: 20px; }
.risk-badge, .tag-blue, .tag-outline { padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.risk-badge { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.tag-blue { background: rgba(37, 99, 235, 0.2); color: #93c5fd; }
.tag-outline { border: 1px solid rgba(148, 163, 184, 0.24); color: #cbd5e1; }
.close-btn { cursor: pointer; color: #94a3b8; }
.section-title { font-weight: 700; margin-bottom: 12px; }
.overview-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-item { display: flex; flex-direction: column; gap: 6px; }
.label { color: #94a3b8; font-size: 13px; }
.value, .detail-text { color: #e2e8f0; }
.value-tags { display: flex; gap: 8px; flex-wrap: wrap; }
.v-tag { padding: 4px 10px; border-radius: 999px; background: rgba(30, 41, 59, 0.85); }
.status-warn { color: #fbbf24; }
.media-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-top: 12px; }
.media-grid.single-image { grid-template-columns: 1fr; }
.media-img { width: 100%; height: 180px; object-fit: cover; border-radius: 12px; }
.law-list { display: flex; flex-direction: column; gap: 10px; }
.law-item { padding: 12px; border-radius: 12px; background: rgba(30, 41, 59, 0.65); }
</style>
