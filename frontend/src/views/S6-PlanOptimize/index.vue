<template>
  <div class="s6-optimize-page">
    <!-- Header -->
    <header class="optimize-header">
      <div class="left-section">
        <el-button @click="goBack" link class="back-btn">
           <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <h2>方案研判与优化 // STRATEGY OPTIMIZATION</h2>
      </div>
      <div class="right-section">
         <div class="risk-badge" :class="{ high: riskScore > 7 }">
            <el-icon><Warning /></el-icon>
            推演风险评分: {{ riskScore }}
         </div>
         <el-button type="success" @click="approveAndDeploy" class="deploy-btn" :disabled="!isOptimized">
            <el-icon><Stamp /></el-icon> 签发并部署 (DEPLOY)
         </el-button>
      </div>
    </header>

    <!-- Main Content -->
    <main class="editor-container">
      <!-- Left: Original Plan (Read-only) -->
      <div class="editor-pane original">
         <div class="pane-header">
           <span class="label">原始方案 (V1.0)</span>
           <span class="status">PRE-SIMULATION</span>
         </div>
         <div class="pane-content read-only">
            <div class="content-text">{{ originalPlan }}</div>
         </div>
      </div>

      <!-- Arrow Separator -->
      <div class="pane-separator">
         <el-icon><Right /></el-icon>
      </div>

      <!-- Center: Optimized Plan (Editable) -->
      <div class="editor-pane optimized">
         <div class="pane-header">
           <span class="label">优化方案 (V1.1)</span>
           <span class="status active">EDITABLE</span>
         </div>
         <textarea
            class="pane-content editable"
            v-model="optimizedPlan"
            placeholder="等待应用优化建议..."
         ></textarea>
      </div>

      <!-- Right: AI Suggestions Sidebar -->
      <aside class="suggestions-sidebar">
         <div class="sidebar-header">
            <el-icon><MagicStick /></el-icon>
            AI 优化建议
         </div>
         <div class="sidebar-desc">基于 S5 推演结果的风险分析</div>

         <div class="suggestion-list">
            <div
              v-for="(sug, idx) in suggestions"
              :key="idx"
              class="suggestion-card"
              :class="{ applied: sug.applied }"
            >
              <div class="sug-header">
                 <span class="risk-tag">{{ sug.riskType }}</span>
              </div>
              <p class="sug-text">{{ sug.text }}</p>
              <el-button
                size="small"
                type="primary"
                plain
                class="apply-btn"
                @click="applySuggestion(idx)"
                :disabled="sug.applied"
              >
                {{ sug.applied ? '已采纳' : '采纳建议' }}
              </el-button>
            </div>
         </div>
      </aside>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ArrowLeft, Warning, Right, MagicStick, Stamp } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()

// Mock Data
const originalPlan = ref(`# 法律应对综合方案

1. **核心主张**: 依据相关法律法规、合同约定与证据材料，重申我方在当前争议中的合法权益。
2. **反制措施**: 派遣海警船只进行常态化巡航，驱离非法作业船只。
3. **外交途径**: 向有关国家发出外交照会，要求其立即停止侵权行为。`)

const optimizedPlan = ref(originalPlan.value) // Start with copy
const riskScore = ref(8.2)

const suggestions = ref([
  {
    riskType: '外交风险',
    text: '推演显示"立即驱离"可能引发武力对峙。建议增加"喊话警告"作为前置程序。',
    patch: '2. **反制措施**: 派遣海警船只进行常态化巡航，优先采取喊话警告、水炮驱离等非接触手段，避免直接撞击。',
    targetIndex: 1, // Crude mapping for demo
    applied: false
  },
  {
    riskType: '法律漏洞',
    text: '单纯引用公约即通过不足，需补充"历史性权利"的法理依据。',
    patch: '1. **核心主张**: 依据相关法律法规、合同约定与证据材料，进一步强化我方在当前争议中的合法权益。',
    targetIndex: 0,
    applied: false
  }
])

const isOptimized = computed(() => suggestions.value.some(s => s.applied) || optimizedPlan.value !== originalPlan.value)

const applySuggestion = (idx: number) => {
  const sug = suggestions.value[idx]
  if (!sug || sug.applied) return

  // Very simple text replacement logic for demo
  // In real app, this would use diff-match-patch or specific block ID
  const lines = optimizedPlan.value.split('\n')
  // Find the line starting with the number
  const targetLineIdx = lines.findIndex(l => l.startsWith(`${sug.targetIndex + 1}.`))

  if (targetLineIdx !== -1) {
     lines[targetLineIdx] = sug.patch
     optimizedPlan.value = lines.join('\n')
     sug.applied = true
     ElMessage.success('已应用优化建议')
  }
}

const approveAndDeploy = () => {
  ElMessage.success('方案已签发，进入部署阶段')
  setTimeout(() => {
     // Navigate to S7 (Placeholder route)
     router.push(`/deployment/${route.params.planId || 'mock'}`)
  }, 1000)
}

const goBack = () => router.back()
</script>

<style scoped>
.s6-optimize-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #020617;
  color: #fff;
  font-family: 'Inter', sans-serif;
}

/* Header */
.optimize-header {
  height: 60px;
  background: rgba(15, 23, 42, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}
.left-section { display: flex; align-items: center; gap: 20px; }
.left-section h2 { margin: 0; font-size: 16px; font-weight: 600; letter-spacing: 1px; color: #E2E8F0; }
.back-btn { color: #94A3B8; }

.right-section { display: flex; align-items: center; gap: 20px; }
.risk-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 4px;
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
  border: 1px solid rgba(16, 185, 129, 0.2);
}
.risk-badge.high {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
  border-color: rgba(239, 68, 68, 0.2);
}
.deploy-btn {
  font-weight: bold;
  letter-spacing: 1px;
}

/* Editor */
.editor-container {
  flex: 1;
  display: flex;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
}

.editor-pane {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(30, 41, 59, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
}

.pane-header {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: rgba(0, 0, 0, 0.2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}
.pane-header .label { font-size: 13px; font-weight: 600; color: #fff; }
.pane-header .status { font-size: 10px; color: #64748B; font-weight: bold; }
.pane-header .status.active { color: #3B82F6; }

.pane-content {
  flex: 1;
  padding: 20px;
  font-family: 'Menlo', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #CBD5E1;
  overflow-y: auto;
  border: none;
  background: transparent;
  resize: none;
  outline: none;
}

.pane-content.read-only {
  background: rgba(0, 0, 0, 0.1);
  color: #94A3B8;
}
.content-text { white-space: pre-wrap; }

.pane-separator {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
}

/* Sidebar */
.suggestions-sidebar {
  width: 320px;
  background: rgba(15, 23, 42, 0.6);
  border-left: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.sidebar-header {
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #3B82F6;
  margin-bottom: 4px;
}
.sidebar-desc { font-size: 11px; color: #64748B; margin-bottom: 20px; }

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
}

.suggestion-card {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s;
}
.suggestion-card:hover { border-color: rgba(59, 130, 246, 0.3); }
.suggestion-card.applied { opacity: 0.5; border-color: transparent; }

.sug-header { margin-bottom: 8px; }
.risk-tag {
  font-size: 10px;
  background: rgba(239, 68, 68, 0.15);
  color: #F87171;
  padding: 2px 6px;
  border-radius: 4px;
}

.sug-text {
  font-size: 12px;
  color: #CBD5E1;
  margin: 0 0 12px 0;
  line-height: 1.4;
}

.apply-btn { width: 100%; }
</style>
