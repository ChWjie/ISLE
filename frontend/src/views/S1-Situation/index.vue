<template>
  <div class="situation-dashboard">
    <aside class="dashboard-panel left-panel">
      <div class="panel-header-tabs">
        <div class="tab-item" :class="{ active: activeTab === 'events' }" @click="activeTab = 'events'">风险事件</div>
        <div class="tab-item" :class="{ active: activeTab === 'articles' }" @click="activeTab = 'articles'">合规资讯</div>
      </div>

      <div class="filter-row" v-if="activeTab === 'events'">
        <div class="filter-group">
          <span class="filter-tag active">全部</span>
          <span class="filter-tag">劳动合规</span>
          <span class="filter-tag">合同争议</span>
          <span class="filter-tag">数据安全</span>
          <span class="filter-tag">知识产权</span>
        </div>
      </div>

      <div class="events-list-container" v-if="activeTab === 'events'">
        <div
          v-for="event in events"
          :key="event.event_id || event.id"
          class="event-card-new"
          :class="(event as any).riskLevel || 'medium'"
          @click="goToEventDetail(event.event_id || event.id)"
        >
          <div class="card-header">
            <span class="event-title">{{ event.title || event.name }}</span>
            <span class="risk-badge" :class="(event as any).riskLevel || 'medium'">{{ getRiskLabel((event as any).riskLevel || 'medium') }}</span>
          </div>
          <div class="card-tags">
            <span class="tag" v-for="tag in (event.tags || [event.dispute_type || '企业合规'])" :key="tag">{{ tag }}</span>
          </div>
          <div class="card-meta">
            <span class="time">{{ formatTime(event.created_at) }}</span>
            <span class="location">地点：{{ event.location_name || '未指定' }}</span>
          </div>
          <div class="card-footer">
            <span class="law-count">关联法规：{{ (event.legal_systems || []).length || 3 }} 条</span>
            <p class="law-refs">{{ event.description || '点击查看事件详情、证据材料和下一步分析建议。' }}</p>
          </div>
        </div>
      </div>

      <div class="articles-list-container" v-else>
        <div v-for="article in articles" :key="article.id" class="article-card">
          <div class="article-header"><span class="article-title">{{ article.title }}</span></div>
          <div class="article-tags"><span class="tag-outline" v-for="tag in article.tags" :key="tag">{{ tag }}</span></div>
          <div class="article-meta"><span class="source">{{ article.source }}</span><span class="time">{{ article.time }}</span></div>
        </div>
      </div>
    </aside>

    <div class="dashboard-panel center-panel">
      <div class="globe-wrapper">
        <Globe3D :events="events" :selected-event="selectedEvent" @view-detail="goToEventDetail" />
        <div class="timeline-player">
          <div class="timeline-controls">
            <div class="time-label">时间轴</div>
            <div class="play-btns"><el-icon><ArrowLeft /></el-icon><el-icon><VideoPlay /></el-icon><el-icon><ArrowRight /></el-icon></div>
          </div>
          <div class="timeline-slider">
            <span class="time-mark start">起点</span>
            <el-slider v-model="timeProgress" :show-tooltip="false" />
            <span class="time-mark end">当前</span>
          </div>
        </div>
      </div>
    </div>

    <aside class="dashboard-panel right-panel">
      <EventDetailPanel v-if="selectedEvent" :event="selectedEvent" @close="closeEventDetail" />

      <template v-else>
        <div class="stats-overview">
          <div class="stat-box"><div class="stat-title">当前活跃事件</div><div class="stat-num">{{ totalEvents }}</div></div>
          <div class="stat-box"><div class="stat-title">高风险事件</div><div class="stat-num">{{ highRiskEvents }}</div></div>
        </div>

        <div class="chart-box">
          <div class="chart-title">案件类型分布</div>
          <div class="chart-content">
            <div class="legend-list">
              <div class="legend-item"><span class="dot c1"></span>劳动用工争议 <span class="percent">{{ sourceStats.enforcement }}%</span></div>
              <div class="legend-item"><span class="dot c2"></span>合同履约争议 <span class="percent">{{ sourceStats.military }}%</span></div>
              <div class="legend-item"><span class="dot c3"></span>知识产权争议 <span class="percent">{{ sourceStats.civilian }}%</span></div>
              <div class="legend-item"><span class="dot c4"></span>数据合规风险 <span class="percent">{{ sourceStats.other }}%</span></div>
            </div>
            <DonutChart :data="sourceDataComputed" width="80px" height="80px" />
          </div>
        </div>

        <div class="chart-box">
          <div class="chart-title">热点区域</div>
          <div class="hotspot-list">
            <div class="hotspot-item" v-for="area in hotspotStats" :key="area.name">
              <span class="area-name">{{ area.name }}</span>
              <span class="area-count">{{ area.count }} 起</span>
              <span class="risk-badge-sm" :class="area.riskClass">{{ area.riskLabel }}</span>
            </div>
          </div>
        </div>

        <div class="chart-box">
          <div class="chart-title">风险等级分布</div>
          <div class="chart-content">
            <div class="legend-list">
              <div class="legend-item"><span class="dot c1"></span>高风险 <span class="percent">{{ sentimentStats.negative }}%</span></div>
              <div class="legend-item"><span class="dot c2"></span>中风险 <span class="percent">{{ sentimentStats.neutral }}%</span></div>
              <div class="legend-item"><span class="dot c3"></span>低风险 <span class="percent">{{ sentimentStats.positive }}%</span></div>
            </div>
            <DonutChart :data="sentimentDataComputed" width="80px" height="80px" />
          </div>
        </div>
      </template>
    </aside>

    <div class="quick-action">
      <el-button type="primary" circle size="large" @click="showCreateDialog = true"><el-icon><Plus /></el-icon></el-button>
    </div>

    <el-dialog v-model="showCreateDialog" title="新建合规风险事件" width="600px" destroy-on-close custom-class="dark-dialog">
      <div style="padding: 20px; text-align: center; color: #fff;">此处保留新建事件流程入口。</div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Plus, ArrowLeft, ArrowRight, VideoPlay } from '@element-plus/icons-vue'
import Globe3D from '@/components/Globe3D/index.vue'
import EventDetailPanel from './components/EventDetailPanel.vue'
import DonutChart from '@/components/DonutChart.vue'
import eventsApi from '@/api/events'
import { apiUrl } from '@/api/config'
import type { DisputeEvent, EventType, EventStatus } from '@/types'

const events = ref<DisputeEvent[]>([])
const selectedEvent = ref<DisputeEvent | null>(null)
const showCreateDialog = ref(false)
const timeProgress = ref(0)
const activeTab = ref<'events' | 'articles'>('events')

const articles = ref([
  { id: 1, title: '劳动用工合规新规解读', tags: ['劳动合规', '用工风险'], source: '法规观察', time: '今日' },
  { id: 2, title: '数据处理活动中的个人信息保护义务', tags: ['数据合规', '个保法'], source: '合规研究院', time: '昨日' },
])

const totalEvents = computed(() => events.value.length)
const highRiskEvents = computed(() => events.value.filter((item: any) => item.riskLevel === 'high').length)

const sourceStats = computed(() => ({ enforcement: 35, military: 28, civilian: 20, other: 17 }))
const sourceDataComputed = computed(() => [
  { name: '劳动用工争议', value: 35, color: '#60a5fa' },
  { name: '合同履约争议', value: 28, color: '#f59e0b' },
  { name: '知识产权争议', value: 20, color: '#a78bfa' },
  { name: '数据合规风险', value: 17, color: '#34d399' },
])
const hotspotStats = computed(() => [
  { name: '深圳', count: 4, riskClass: 'high', riskLabel: '高风险' },
  { name: '上海', count: 3, riskClass: 'medium', riskLabel: '中风险' },
  { name: '北京', count: 2, riskClass: 'low', riskLabel: '低风险' },
])
const sentimentStats = computed(() => ({ negative: 25, neutral: 50, positive: 25 }))
const sentimentDataComputed = computed(() => [
  { name: '高风险', value: 25, color: '#f87171' },
  { name: '中风险', value: 50, color: '#fbbf24' },
  { name: '低风险', value: 25, color: '#4ade80' },
])

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

const inferCity = (text: string) => {
  const source = text || ''
  return Object.keys(CITY_COORDS).find(city => source.includes(city)) || '深圳'
}

const inferRiskLevel = (text: string): 'high' | 'medium' | 'low' => {
  const source = text || ''
  if (/(立案|处罚|索赔|诉讼|调查|违规|工伤|侵权|行贿|歧视)/.test(source)) return 'high'
  if (/(争议|仲裁|合规|问询|整改)/.test(source)) return 'medium'
  return 'low'
}

const inferEventType = (disputeType?: string): EventType => {
  const source = disputeType || ''
  if (source.includes('数据')) return 'economic' as EventType
  if (source.includes('劳动')) return 'economic' as EventType
  if (source.includes('知识产权')) return 'economic' as EventType
  return 'economic' as EventType
}

const normalizeEvent = (item: any, index: number): DisputeEvent => {
  const title = item.title || item.name || `事件 ${index + 1}`
  const city = item.location_name || inferCity(`${title} ${item.description || ''} ${item.fact_summary || ''}`)
  const location = item.location || CITY_COORDS[city] || CITY_COORDS['深圳']
  const riskLevel = item.riskLevel || inferRiskLevel(`${title} ${item.description || ''} ${item.dispute_type || ''}`)
  return {
    id: String(item.id || item.event_id || `event-${index + 1}`),
    event_id: String(item.event_id || item.id || `event-${index + 1}`),
    title,
    name: item.name || title,
    type: inferEventType(item.dispute_type),
    description: item.description || item.fact_summary || '暂无描述',
    location,
    location_name: city,
    parties: [...(item.our_side || []), ...(item.opponent_side || [])],
    our_side: item.our_side || [],
    opponent_side: item.opponent_side || [],
    legal_systems: item.legal_systems || [],
    dispute_type: item.dispute_type || '企业合规',
    fact_summary: item.fact_summary || '',
    status: (item.status || 'pending') as EventStatus,
    severity: riskLevel === 'high' ? 5 : riskLevel === 'medium' ? 3 : 1,
    created_at: item.created_at,
    updated_at: item.updated_at || item.created_at,
    riskLevel,
    tags: item.tags || [item.dispute_type || city],
  }
}

const loadEvents = async () => {
  try {
    const eventsUrl = apiUrl('/api/v1/events')
    console.info('[S1] loading events from', eventsUrl)
    const response = await fetch(eventsUrl)
    if (!response.ok) {
      throw new Error(`events request failed: ${response.status}`)
    }
    const result = await response.json()
    const data = Array.isArray(result) ? result : (result?.data || [])
    console.info('[S1] events loaded', data.length)
    events.value = (data || []).map((item: any, index: number) => normalizeEvent(item, index))
    if (selectedEvent.value) {
      const currentId = String(selectedEvent.value.event_id || selectedEvent.value.id)
      selectedEvent.value = events.value.find(item => String(item.event_id || item.id) === currentId) || null
    }
  } catch (error) {
    console.error('[S1] direct events request failed, fallback to api client', error)
    try {
      const data = await eventsApi.listEvents()
      events.value = (data || []).map((item: any, index: number) => normalizeEvent(item, index))
    } catch (fallbackError) {
      console.error('[S1] fallback events request failed', fallbackError)
      events.value = []
    }
  }
}

const goToEventDetail = (id: string | number) => {
  const matched = events.value.find((item: any) => String(item.event_id || item.id) === String(id))
  selectedEvent.value = matched || null
}

const closeEventDetail = () => {
  selectedEvent.value = null
}

const formatTime = (value: any) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

const getRiskLabel = (risk: string) => {
  const labels: Record<string, string> = { high: '高风险', medium: '中风险', low: '低风险' }
  return labels[risk] || '中风险'
}

onMounted(() => {
  loadEvents()
})
</script>

<style scoped>
.situation-dashboard {
  height: calc(100vh - 64px);
  display: grid;
  grid-template-columns: 360px 1fr 360px;
  gap: 16px;
  padding: 16px;
  background: #020617;
  color: #fff;
}
.dashboard-panel {
  background: rgba(15, 23, 42, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.14);
  border-radius: 16px;
  overflow: hidden;
}
.left-panel, .right-panel { padding: 16px; overflow-y: auto; }
.panel-header-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.tab-item { padding: 8px 12px; border-radius: 999px; background: rgba(30, 41, 59, 0.8); cursor: pointer; }
.tab-item.active { background: #2563eb; }
.filter-row { margin-bottom: 16px; }
.filter-group { display: flex; gap: 8px; flex-wrap: wrap; }
.filter-tag, .tag, .tag-outline { padding: 4px 10px; border-radius: 999px; font-size: 12px; }
.filter-tag, .tag { background: rgba(37, 99, 235, 0.18); }
.tag-outline { border: 1px solid rgba(148, 163, 184, 0.3); }
.events-list-container, .articles-list-container { display: flex; flex-direction: column; gap: 12px; }
.event-card-new, .article-card, .chart-box, .stat-box {
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 14px;
  padding: 14px;
}
.card-header, .card-meta, .article-meta, .timeline-controls, .timeline-slider, .stats-overview, .chart-content, .hotspot-item {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}
.card-tags, .article-tags, .legend-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
.event-title, .article-title { font-weight: 700; }
.risk-badge { padding: 2px 8px; border-radius: 999px; font-size: 12px; }
.risk-badge.high, .risk-badge-sm.high { background: rgba(239, 68, 68, 0.18); color: #f87171; }
.risk-badge.medium, .risk-badge-sm.medium { background: rgba(245, 158, 11, 0.18); color: #fbbf24; }
.risk-badge.low, .risk-badge-sm.low { background: rgba(34, 197, 94, 0.18); color: #4ade80; }
.card-footer p { margin: 8px 0 0; color: #94a3b8; }
.center-panel { position: relative; }
.globe-wrapper { height: 100%; position: relative; }
.timeline-player {
  position: absolute; left: 16px; right: 16px; bottom: 16px;
  background: rgba(2, 6, 23, 0.8); border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 14px; padding: 14px;
}
.stats-overview { display: grid; grid-template-columns: repeat(2, 1fr); margin-bottom: 16px; }
.stat-title { color: #94a3b8; }
.stat-num { font-size: 28px; font-weight: 700; }
.legend-item, .hotspot-item { color: #cbd5e1; }
.dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
.c1 { background: #60a5fa; } .c2 { background: #f59e0b; } .c3 { background: #a78bfa; } .c4 { background: #34d399; }
.quick-action { position: fixed; right: 24px; bottom: 24px; }
@media (max-width: 1400px) { .situation-dashboard { grid-template-columns: 1fr; height: auto; min-height: 100vh; } }
</style>
