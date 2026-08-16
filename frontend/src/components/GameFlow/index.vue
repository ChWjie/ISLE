<template>
  <div class="game-flow-container" ref="containerRef"></div>
</template>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { Graph } from '@antv/x6'
import type { GameRound } from '@/types'

const props = defineProps<{
  rounds: GameRound[]
  status: string
}>()

const containerRef = ref<HTMLElement | null>(null)
let graph: Graph | null = null

const initGraph = () => {
  if (!containerRef.value) return

  graph = new Graph({
    container: containerRef.value,
    width: containerRef.value.offsetWidth,
    height: containerRef.value.offsetHeight || 600,
    background: {
      color: '#101428', // 深色背景
    },
    grid: {
      size: 10,
      visible: true,
      type: 'dot',
      args: { color: '#2b344d', thickness: 1 },
    },
    panning: true,
    mousewheel: true,
    connecting: {
      router: 'manhattan',
      connector: {
        name: 'rounded',
        args: { radius: 8 },
      },
      anchor: 'center',
      connectionPoint: 'anchor',
      allowBlank: false,
    },
  })

  // 初始节点
  graph.addNode({
    id: 'start-node',
    x: 350,
    y: 50,
    width: 100,
    height: 40,
    shape: 'rect',
    label: '博弈开始',
    attrs: {
      body: { fill: '#3b82f6', stroke: '#2563eb', rx: 4, ry: 4 },
      label: { fill: '#fff' }
    }
  })

  updateGraph()
}

const updateGraph = () => {
  if (!graph) return

  // 清除除Start外的节点 (简单粗暴重画，或者优化为增量添加)
  // 为了演示流畅性，我们这里做增量添加的逻辑是个好主意，但简单起见，我们先每次重画
  // 实际上X6重画开销还好，或者我们只判断新增的round

  const startNode = graph.getCellById('start-node')
  if (!startNode || !startNode.isNode()) return

  let lastNode = startNode
  let yOffset = 150

  props.rounds.forEach((round, index) => {
    if (!graph) return

    // 1. 我方行动节点
    const ourNodeId = `round-${index}-our`
    let ourNode = graph.getCellById(ourNodeId)
    if (!ourNode) {
      ourNode = graph.addNode({
        id: ourNodeId,
        x: 200,
        y: yOffset,
        width: 160,
        height: 60,
        shape: 'rect',
        label: `我方: ${round.our_action.substring(0, 10)}...`,
        attrs: {
          body: { fill: '#1e3a8a', stroke: '#3b82f6', strokeWidth: 2, rx: 8, ry: 8 },
          label: { fill: '#fff', fontSize: 12 }
        }
      })

      graph.addEdge({
        source: lastNode,
        target: ourNode,
        attrs: { line: { stroke: '#5c6c8f', strokeWidth: 2 } }
      })
    }

    // 2. 对方行动节点
    const theirNodeId = `round-${index}-their`
    let theirNode = graph.getCellById(theirNodeId)
    if (!theirNode) {
      theirNode = graph.addNode({
        id: theirNodeId,
        x: 500,
        y: yOffset,
        width: 160,
        height: 60,
        shape: 'rect',
        label: `对方: ${round.their_action.substring(0, 10)}...`,
        attrs: {
          body: { fill: '#7f1d1d', stroke: '#ef4444', strokeWidth: 2, rx: 8, ry: 8 },
          label: { fill: '#fff', fontSize: 12 }
        }
      })

      // 规则判定节点 (如果触发风险)
      if (round.risks.length > 0) {
         const riskNode = graph.addNode({
           x: 350,
           y: yOffset + 40, // 稍微错开
           width: 120,
           height: 30,
           shape: 'path',
           path: 'M 0 15 L 60 0 L 120 15 L 60 30 Z', // 菱形
           label: '风险触发',
           attrs: {
             body: { fill: '#f59e0b', stroke: '#b45309' },
             label: { fill: '#000', fontSize: 10 }
           }
         })

         graph.addEdge({ source: ourNode, target: riskNode, attrs: { line: { stroke: '#f59e0b', strokeDasharray: 5 } } })
         graph.addEdge({ source: theirNode, target: riskNode, attrs: { line: { stroke: '#f59e0b', strokeDasharray: 5 } } })
      }

      graph.addEdge({
        source: ourNode,
        target: theirNode,
        label: '反制',
        attrs: { line: { stroke: '#ef4444', targetMarker: 'classic' } }
      })
    }

    lastNode = theirNode as any // 设置为对方节点作为下一轮的前置
    yOffset += 120
  })

  // 自动布局/居中
  graph.centerContent()
}

watch(() => props.rounds, () => {
  updateGraph()
}, { deep: true })

onMounted(() => {
  initGraph()
})

onBeforeUnmount(() => {
  if (graph) {
    graph.dispose()
  }
})
</script>

<style scoped>
.game-flow-container {
  width: 100%;
  height: 100%;
  min-height: 500px;
}
</style>
