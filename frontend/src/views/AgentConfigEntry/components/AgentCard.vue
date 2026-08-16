<template>
  <div class="agent-card" :class="{ selected: isSelected }" @click="$emit('toggle')">
    <div class="card-header">
      <div class="avatar-wrapper">
        <div class="avatar-icon">
          <img v-if="agent.avatar" :src="agent.avatar" alt="avatar" />
          <span v-else>⚖️</span>
        </div>
      </div>
      <div class="header-info">
        <h3 class="agent-name">{{ agent.name }}</h3>
        <span class="agent-title">{{ getAgentTypeLabel(agent.agent_type) }}</span>
      </div>
      <el-checkbox :model-value="isSelected" class="select-checkbox" @click.stop="$emit('toggle')" />
    </div>

    <div class="card-body">
      <p class="description">{{ agent.description }}</p>
      <div class="meta-info">
        <span class="meta-item">创建时间：{{ agent.created_at || '2026-01-01' }}</span>
      </div>
    </div>

    <div class="card-footer">
      <el-button class="action-btn" :type="isSelected ? 'primary' : 'default'" size="small" @click.stop="$emit('toggle')">
        {{ isSelected ? '已选中' : '加入分析' }}
      </el-button>
      <el-button class="action-btn outline" size="small" @click.stop="$emit('edit')">
        配置参数
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  agent: any
  isSelected: boolean
}>()

defineEmits(['toggle', 'edit'])

const getAgentTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    blue: '分析智能体',
    red: '博弈智能体',
    judge: '裁判智能体',
    analyst: '分析师',
  }
  return labels[type] || '分析智能体'
}
</script>

<style scoped>
.agent-card {
  background: rgba(20, 27, 45, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  padding: 12px;
  transition: all 0.2s ease;
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.agent-card:hover {
  background: rgba(20, 27, 45, 0.8);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.agent-card.selected {
  background: rgba(30, 58, 138, 0.2);
  border-color: var(--color-primary);
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.1);
}
.card-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.avatar-wrapper {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.avatar-icon { font-size: 20px; }
.avatar-icon img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}
.header-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.agent-name {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}
.agent-title {
  font-size: 11px;
  color: var(--color-primary-light);
  background: rgba(59, 130, 246, 0.1);
  padding: 1px 5px;
  border-radius: 2px;
  width: fit-content;
}
.select-checkbox {
  margin-right: -4px;
  transform: scale(0.9);
}
.description {
  font-size: 11px;
  color: var(--color-text-secondary);
  line-height: 1.5;
  margin: 0 0 10px 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.meta-info {
  font-size: 10px;
  color: var(--color-text-tertiary);
}
.card-footer {
  display: flex;
  gap: 8px;
}
.action-btn {
  flex: 1;
  padding: 4px 0;
  font-size: 11px;
  height: 28px;
}
.action-btn.outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: var(--color-text-secondary);
}
.action-btn.outline:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}
</style>
