<template>
  <div class="globe-container" ref="containerRef">
    <div ref="chartRef" class="china-map"></div>
    <!-- 事件弹窗 -->
    <div v-if="popupEvent" class="event-popup" :style="popupStyle">
      <div class="popup-content">
        <h3>{{ popupEvent.title }}</h3>
        <p>{{ popupEvent.description }}</p>
        <el-button type="primary" size="small" @click="goToDetail(String(popupEvent.event_id || popupEvent.id))">查看详情</el-button>
        <el-button link size="small" @click="popupEvent = null">关闭</el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { DisputeEvent } from '@/types'

const props = defineProps<{
  events: DisputeEvent[]
  selectedEvent?: DisputeEvent | null
}>()

const emit = defineEmits(['view-detail'])

const chartRef = ref<HTMLElement | null>(null)
const containerRef = ref<HTMLElement | null>(null)
let chart: echarts.ECharts | null = null

const popupEvent = ref<DisputeEvent | null>(null)
const popupStyle = ref({ top: '50px', left: '50px' })

// 风险类型对应颜色
const getRiskColor = (riskLevel?: string) => {
  if (riskLevel === 'high') return '#F56C6C'
  if (riskLevel === 'medium') return '#E6A23C'
  return '#67C23A'
}

// 将事件转为 ECharts scatter 数据
const getScatterData = () => {
  return props.events
    .filter(e => e.location && typeof e.location.lng === 'number' && typeof e.location.lat === 'number')
    .map(e => ({
      name: e.title || e.name || '未命名事件',
      value: [e.location.lng, e.location.lat, 1],
      itemStyle: { color: getRiskColor(e.riskLevel) },
      eventId: e.event_id || e.id,
    }))
}

const initChart = async () => {
  if (!chartRef.value || !containerRef.value) return

  // Register map. Prefer local static data, fallback to CDN and simplified outline.
  try {
    const res = await fetch('/maps/china.json')
    if (!res.ok) throw new Error(`map json failed: ${res.status}`)
    const geoJson = await res.json()
    echarts.registerMap('china', geoJson)
  } catch (localError) {
    try {
      console.warn('[Globe3D] local map failed, trying CDN', localError)
      const res = await fetch('https://geo.datav.aliyun.com/areas_v3/bound/100000_full.json')
      if (!res.ok) throw new Error(`remote map json failed: ${res.status}`)
      const geoJson = await res.json()
      echarts.registerMap('china', geoJson)
    } catch {
      console.warn('[Globe3D] remote map failed, using simplified local map')
      echarts.registerMap('china', {
        type: 'FeatureCollection',
        features: [
          {
            type: 'Feature',
            properties: { name: 'China' },
            geometry: {
              type: 'Polygon',
              coordinates: [[
                [73, 39], [80, 45], [88, 49], [98, 48], [108, 50],
                [121, 53], [134, 48], [130, 42], [124, 39], [122, 31],
                [119, 25], [113, 22], [109, 18], [103, 22], [98, 25],
                [92, 28], [85, 29], [80, 34], [73, 39]
              ]]
            }
          },
          {
            type: 'Feature',
            properties: { name: 'Hainan' },
            geometry: {
              type: 'Polygon',
              coordinates: [[[108.5, 20.2], [111.2, 20.1], [111.4, 18.2], [109, 18.1], [108.5, 20.2]]]
            }
          }
        ]
      } as any)
    }
  }

  chart = echarts.init(chartRef.value, 'dark')

  const option: echarts.EChartsOption = {
    backgroundColor: '#0b1026',
    geo: {
      map: 'china',
      roam: true,
      zoom: 1.2,
      center: [105, 35],
      label: {
        show: false,
      },
      itemStyle: {
        areaColor: '#0d1e4d',
        borderColor: '#1a3a7a',
        borderWidth: 1,
      },
      emphasis: {
        itemStyle: {
          areaColor: '#1a3a8a',
        },
        label: {
          show: true,
          color: '#ffffff',
          fontSize: 12,
        },
      },
    },
    series: [
      {
        name: '合规风险案件',
        type: 'scatter',
        coordinateSystem: 'geo',
        data: getScatterData(),
        symbolSize: 14,
        symbol: 'circle',
        label: {
          show: true,
          formatter: (params: any) => {
            const name: string = params.name || ''
            return name.length > 8 ? name.slice(0, 8) + '…' : name
          },
          position: 'right',
          fontSize: 11,
          color: '#e0e8ff',
          distance: 6,
        },
        emphasis: {
          scale: 1.5,
        },
        zlevel: 2,
      },
      {
        name: '波纹',
        type: 'effectScatter',
        coordinateSystem: 'geo',
        data: getScatterData(),
        symbolSize: 10,
        showEffectOn: 'render',
        rippleEffect: {
          brushType: 'stroke',
          scale: 3,
          period: 4,
        },
        itemStyle: {
          color: (params: any) => params.data?.itemStyle?.color || '#F56C6C',
          opacity: 0.6,
        },
        zlevel: 1,
      },
    ],
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(11,16,38,0.9)',
      borderColor: '#1a3a7a',
      textStyle: { color: '#e0e8ff', fontSize: 12 },
      formatter: (params: any) => {
        if (!params.name) return ''
        return `<b>${params.name}</b><br/>点击查看详情`
      },
    },
  }

  chart.setOption(option)

  // 点击事件
  chart.on('click', (params: any) => {
    if (params.componentType === 'series' && params.data?.eventId) {
      const event = props.events.find(e => String(e.event_id || e.id) === String(params.data.eventId))
      if (event) {
        popupEvent.value = event
        const px = params.event?.offsetX ?? 100
        const py = params.event?.offsetY ?? 100
        popupStyle.value = {
          left: `${px + 20}px`,
          top: `${py - 50}px`,
        }
      }
    } else {
      popupEvent.value = null
    }
  })
}

const updateChart = () => {
  if (!chart) return
  chart.setOption({
    series: [
      { name: '合规风险案件', data: getScatterData() },
      { name: '波纹', data: getScatterData() },
    ],
  })
}

const goToDetail = (id: string) => {
  popupEvent.value = null
  emit('view-detail', id)
}

watch(() => props.events, () => {
  updateChart()
}, { deep: true })

watch(() => props.selectedEvent, (newEvent) => {
  if (newEvent && chart && newEvent.location) {
    // 飞向选中事件（缩放到指定区域）
    chart.setOption({
      geo: {
        center: [newEvent.location.lng, newEvent.location.lat],
        zoom: 4,
      },
    })
  }
})

const handleResize = () => {
  chart?.resize()
}

onMounted(async () => {
  await nextTick()
  await initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  chart?.dispose()
  chart = null
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.globe-container {
  width: 100%;
  height: 100%;
  position: relative;
  overflow: hidden;
  background: #0b1026;
}

.china-map {
  width: 100%;
  height: 100%;
}

.event-popup {
  position: absolute;
  background: rgba(11, 16, 38, 0.95);
  border: 1px solid #1a3a7a;
  border-radius: 4px;
  padding: 16px;
  width: 280px;
  backdrop-filter: blur(12px);
  box-shadow: 0 0 20px rgba(0, 122, 255, 0.3);
  pointer-events: auto;
  z-index: 100;
  animation: fadeIn 0.3s ease;
}

.popup-content h3 {
  margin: 0 0 8px 0;
  color: #66b3ff;
  font-size: 15px;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-bottom: 8px;
}

.popup-content p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 13px;
  margin-bottom: 12px;
  line-height: 1.5;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
