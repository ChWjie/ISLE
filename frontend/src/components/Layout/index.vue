<template>
  <div class="app-layout">
    <header class="navbar">
      <div class="logo">
        <h1 class="text-gradient">ICLGS</h1>
      </div>

      <div class="modules-nav">
        <div
          v-for="module in modules"
          :key="module.path"
          class="module-item"
          :class="{ active: isModuleActive(module.path) }"
          @click="navigate(module.path)"
        >
          <span class="module-label">{{ module.label }}</span>
        </div>
      </div>

      <div class="user-profile">
        <el-avatar :size="32" icon="UserFilled" />
        <span class="role-badge">法务顾问</span>
      </div>
    </header>

    <main class="page-container">
      <router-view v-slot="{ Component, route }">
        <component :is="Component" :key="route.path" v-if="Component" />
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">

import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const modules = [
  { id: 'M1', label: '态势首页', path: '/situation' },
  { id: 'M2', label: '多智能体任务分析', path: '/agent-config' },
  { id: 'M3', label: '法庭博弈模拟', path: '/simulation' },
  { id: 'M4', label: '法律库', path: '/law-library' },
  { id: 'M5', label: '方案库', path: '/plan-library' }
]

const isModuleActive = (path: string) => {
  return route.path.startsWith(path)
}

const navigate = (path: string) => {
  router.push(path)
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-primary);
}

.navbar {
  height: 64px;
  background: rgba(11, 16, 38, 0.95);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-lg);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
}

.modules-nav {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  margin: 0 var(--spacing-xl);
}

.module-item {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 140px;
  gap: 6px;
  padding: 8px 20px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid transparent;
}

.module-item:hover {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.9);
}

.module-item.active {
  background: rgba(64, 158, 255, 0.15);
  color: #409EFF;
  border-color: rgba(64, 158, 255, 0.3);
  box-shadow: 0 0 12px rgba(64, 158, 255, 0.2);
}

.module-icon {
  font-size: 16px;
  line-height: 1;
}

.module-label {
  white-space: nowrap;
}

.user-profile {
  display: flex;
  align-items: center;
  gap: 8px;
}

.role-badge {
  font-size: 12px;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.page-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
