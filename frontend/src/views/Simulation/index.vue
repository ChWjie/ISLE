<template>
  <div class="simulation-page">
    <div class="simulation-sidebar">
      <div class="sidebar-header">
        <h3>法庭博弈模拟</h3>
      </div>
      <div class="simulation-steps">
        <div
          v-for="step in simulationSteps"
          :key="step.path"
          class="step-item"
          :class="{ active: isStepActive(step.path) }"
          @click="navigateToStep(step.path)"
        >
          <div class="step-number">{{ step.number }}</div>
          <div class="step-info">
            <div class="step-title">{{ step.title }}</div>
            <div class="step-desc">{{ step.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="simulation-content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">

import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const simulationSteps = [
  {
    number: '01',
    title: '方案生成',
    desc: '基于律师团分析生成初步方案',
    path: '/simulation/plan-generation'
  },
  {
    number: '02',
    title: '博弈推演',
    desc: '红蓝对抗模拟验证',
    path: '/simulation/game'
  },
  {
    number: '03',
    title: '方案优化',
    desc: '根据推演结果优化方案',
    path: '/simulation/optimize'
  }
]

const isStepActive = (path: string) => {
  return route.path.includes(path.split('/').pop() || '')
}

const navigateToStep = (path: string) => {
  // 简单跳转，实际可能需要携带参数
  router.push(path)
}
</script>

<style scoped>
.simulation-page {
  display: flex;
  height: 100vh;
  background: var(--color-bg-primary);
}

.simulation-sidebar {
  width: 280px;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-border);
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.simulation-steps {
  flex: 1;
  padding: var(--spacing-md);
  overflow-y: auto;
}

.step-item {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.step-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.step-item.active {
  background: rgba(64, 158, 255, 0.1);
  border-color: rgba(64, 158, 255, 0.3);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.step-item.active .step-number {
  background: rgba(64, 158, 255, 0.2);
  color: var(--color-primary);
}

.step-info {
  flex: 1;
}

.step-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.step-desc {
  font-size: 12px;
  color: var(--color-text-tertiary);
  line-height: 1.4;
}

.simulation-content {
  flex: 1;
  overflow: auto;
}
</style>
