<template>
  <div class="event-detail-page">
    <div class="globe-section">
      <Globe3D :events="event ? [event] : []" />
      <div class="globe-overlay-top">
        <el-button @click="goBack" class="back-btn-glass">
          <el-icon><ArrowLeft /></el-icon>
          返回态势首页
        </el-button>
      </div>
    </div>

    <div class="info-panel" v-if="event">
      <div class="panel-header">
        <div class="header-top">
          <div class="title-row">
            <h1 class="event-title">{{ event.title || event.name }}</h1>
            <span class="risk-badge">重点关注</span>
          </div>
          <el-button type="primary" class="analysis-btn" @click="startAnalysis">进入智能体分析</el-button>
        </div>
        <div class="tags-row">
          <span class="tag-blue">{{ event.dispute_type || '企业合规' }}</span>
          <span class="tag-outline">{{ event.location_name || '未指定地区' }}</span>
        </div>
        <div class="time-row">{{ formatDate(event.created_at) }}</div>
      </div>

      <div class="section-box">
        <div class="section-title">事件概览</div>
        <div class="overview-grid">
          <div class="grid-item"><span class="label">涉事主体</span><span class="value">{{ getPartyText(event.our_side, '我方主体') }} / {{ getPartyText(event.opponent_side, '对方主体') }}</span></div>
          <div class="grid-item"><span class="label">地点</span><span class="value">{{ event.location_name || '未指定' }}</span></div>
          <div class="grid-item"><span class="label">首次录入</span><span class="value">{{ formatDate(event.created_at) }}</span></div>
          <div class="grid-item"><span class="label">最近更新</span><span class="value">{{ formatDate(event.updated_at) }}</span></div>
          <div class="grid-item"><span class="label">状态</span><span class="value status-warn">研判中</span></div>
          <div class="grid-item"><span class="label">关联法域</span><span class="value">{{ getLegalSystemsText(event.legal_systems) }}</span></div>
        </div>
      </div>

      <div class="section-box">
        <div class="section-title">事件详情</div>
        <p class="detail-text">{{ event.description || event.fact_summary || '暂无详细描述。' }}</p>
      </div>

      <div class="section-box">
        <div class="section-title">相关法规</div>
        <div class="law-list">
          <div class="law-item" v-for="(law, index) in legalRefs" :key="index">
            <span class="law-name">{{ law }}</span>
          </div>
        </div>
      </div>

      <div class="section-box">
        <div class="section-title">相关提示</div>
        <div class="law-list">
          <div class="law-item"><span class="law-name">建议补充证据链、关键时间线与涉案主体关系图。</span></div>
          <div class="law-item"><span class="law-name">进入下一步后可选择多个智能体进行并行分析。</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { eventApi } from '@/api/event'
import Globe3D from '@/components/Globe3D/index.vue'
import type { DisputeEvent, EventType, EventStatus } from '@/types'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const event = ref<DisputeEvent | null>(null)

const CITY_COORDS: Record<string, { lat: number; lng: number }> = {
  深圳: { lat: 22.5431, lng: 114.0579 },
  广州: { lat: 23.1291, lng: 113.2644 },
  北京: { lat: 39.9042, lng: 116.4074 },
  上海: { lat: 31.2304, lng: 121.4737 },
  杭州: { lat: 30.2741, lng: 120.1551 },
  成都: { lat: 30.5728, lng: 104.0668 },
  武汉: { lat: 30.5928, lng: 114.3055 },
  南京: { lat: 32.0603, lng: 118.7969 },
  重庆: { lat: 29.5630, lng: 106.5516 },
}

const normalizeEvent = (item: any): DisputeEvent => {
  const title = item.title || item.name || '未命名事件'
  const city = item.location_name || Object.keys(CITY_COORDS).find(cityName =>
    `${title} ${item.description || ''} ${item.fact_summary || ''}`.includes(cityName)
  ) || '深圳'
  return {
    id: String(item.id || item.event_id || ''),
    event_id: String(item.event_id || item.id || ''),
    title,
    name: item.name || title,
    type: 'economic' as EventType,
    description: item.description || item.fact_summary || '暂无详细描述',
    location: item.location || CITY_COORDS[city],
    location_name: city,
    parties: [...(item.our_side || []), ...(item.opponent_side || [])],
    status: (item.status || 'pending') as EventStatus,
    severity: 3,
    created_at: item.created_at,
    updated_at: item.updated_at || item.created_at,
    dispute_type: item.dispute_type || '企业合规',
    our_side: item.our_side || [],
    opponent_side: item.opponent_side || [],
    legal_systems: item.legal_systems || [],
    fact_summary: item.fact_summary || '',
  }
}

const legalRefs = computed(() => {
  const systems = (event.value as any)?.legal_systems
  if (Array.isArray(systems) && systems.length) return systems
  return ['公司法', '劳动合同法', '个人信息保护法']
})

const loadEvent = async () => {
  loading.value = true
  try {
    const id = route.params.id as string
    const data = await eventApi.getEventById(id)
    event.value = normalizeEvent(data)
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/situation')
}

const startAnalysis = () => {
  if (!event.value) return
  router.push(`/agent-config/${(event.value as any).event_id || (event.value as any).id}`)
}

const formatDate = (date: any) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

const getPartyText = (party: any, fallback: string) => {
  if (!party) return fallback
  if (typeof party === 'string') return party
  return party.name || party.title || fallback
}

const getLegalSystemsText = (systems: any) => {
  if (!systems) return '待补充'
  if (Array.isArray(systems)) return systems.join('、')
  return String(systems)
}

onMounted(() => {
  loadEvent()
})
</script>

<style scoped>
.event-detail-page {
  min-height: calc(100vh - 64px);
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  background: var(--color-bg-primary);
  overflow: hidden;
}
.globe-section { position: relative; background: #000; border-right: 1px solid var(--color-border); }
.globe-overlay-top { position: absolute; top: 20px; left: 20px; z-index: 10; }
.back-btn-glass {
  background: rgba(11, 16, 38, 0.6);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}
.info-panel {
  background: var(--color-bg-secondary);
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  padding: 20px;
}
.panel-header, .section-box {
  background: rgba(15, 23, 42, 0.82);
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 16px;
  padding: 18px;
}
.header-top, .title-row, .tags-row, .overview-grid { display: flex; gap: 12px; flex-wrap: wrap; }
.header-top { justify-content: space-between; align-items: center; }
.event-title { margin: 0; }
.risk-badge, .tag-blue, .tag-outline {
  padding: 4px 10px; border-radius: 999px; font-size: 12px;
}
.risk-badge { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.tag-blue { background: rgba(37, 99, 235, 0.18); color: #93c5fd; }
.tag-outline { border: 1px solid rgba(148, 163, 184, 0.3); color: #cbd5e1; }
.time-row, .detail-text, .value { color: #cbd5e1; }
.section-title { font-weight: 700; margin-bottom: 12px; }
.overview-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-item { display: flex; flex-direction: column; gap: 6px; }
.label { color: #94a3b8; font-size: 13px; }
.status-warn { color: #fbbf24; }
.law-list { display: flex; flex-direction: column; gap: 10px; }
.law-item { padding: 12px; border-radius: 12px; background: rgba(30, 41, 59, 0.65); color: #e2e8f0; }
@media (max-width: 1200px) { .event-detail-page { grid-template-columns: 1fr; } .globe-section { min-height: 360px; } }
</style>
