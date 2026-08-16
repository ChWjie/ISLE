<template>
  <div class="agent-grid-container">
    <div class="grid-header">
      <h2>多维度分析矩阵</h2>
      <p>基于事件特征，智能体将从三个核心维度进行法律分析</p>
    </div>

    <div class="analysis-grid">
      <!-- Card 1: 事件性质分析 -->
      <div class="analysis-card">
        <div class="card-header">
          <div class="card-icon blue">
            <el-icon><Document /></el-icon>
          </div>
          <div class="card-title-group">
            <h3>事件/合约性质分析</h3>
            <p>提供现行法可用解释的完整图景，避免法律盲区</p>
          </div>
        </div>
        <div class="card-footer">
          <el-button type="primary" @click="$emit('intelligent-reasoning', 'nature')">
            智能推理
          </el-button>
          <el-button>证据链验证</el-button>
        </div>
      </div>

      <!-- Card 2: 新旧法律依据 -->
      <div class="analysis-card">
        <div class="card-header">
          <div class="card-icon green">
            <el-icon><Reading /></el-icon>
          </div>
          <div class="card-title-group">
            <h3>新旧法律依据</h3>
            <p>提取关键法律条款组建自动化工具，呈现矛盾双方法律武器库</p>
          </div>
        </div>
        <div class="card-footer">
          <el-button type="primary" @click="$emit('intelligent-reasoning', 'legal')">
            智能推理
          </el-button>
          <el-button>证据链验证</el-button>
        </div>
      </div>

      <!-- Card 3: 新旧博弈路径 -->
      <div class="analysis-card">
        <div class="card-header">
          <div class="card-icon orange">
            <el-icon><Trophy /></el-icon>
          </div>
          <div class="card-title-group">
            <h3>新旧博弈路径</h3>
            <p>生成对抗结构树，推演双方策略空间与风险分布，给出优选方案</p>
          </div>
        </div>
        <div class="card-footer">
          <el-button type="primary" @click="$emit('intelligent-reasoning', 'strategy')">
            智能推理
          </el-button>
          <el-button>证据链验证</el-button>
        </div>
      </div>
    </div>

    <!-- Agents Section -->
    <div class="agents-section">
      <div class="section-title">执行智能体</div>
      <div class="agents-list">
        <div v-for="agent in agents" :key="agent.id" class="agent-item">
          <el-avatar :size="32" :src="agent.avatar">{{ agent.name[0] }}</el-avatar>
          <div class="agent-info">
            <div class="agent-name">{{ agent.name }}</div>
            <div class="agent-role">{{ agent.role }}</div>
          </div>
          <el-button size="small" link @click="$emit('config-agent', agent.id)">配置</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Document, Reading, Trophy } from '@element-plus/icons-vue'

interface Agent {
  id: string
  name: string
  role: string
  avatar?: string
}

defineProps<{
  agents?: Agent[]
}>()

defineEmits(['intelligent-reasoning', 'config-agent'])
</script>

<style scoped>
.agent-grid-container {
  padding: 24px;
  background: var(--color-bg-secondary);
  border-radius: 8px;
}

.grid-header {
  margin-bottom: 24px;
}

.grid-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-highlight);
  margin-bottom: 8px;
}

.grid-header p {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.analysis-card {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s;
}

.analysis-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.2);
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.card-icon.blue {
  background: rgba(59, 130, 246, 0.2);
  color: #3B82F6;
}

.card-icon.green {
  background: rgba(16, 185, 129, 0.2);
  color: #10B981;
}

.card-icon.orange {
  background: rgba(245, 158, 11, 0.2);
  color: #F59E0B;
}

.card-title-group h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-highlight);
  margin-bottom: 8px;
}

.card-title-group p {
  font-size: 12px;
  color: var(--color-text-secondary);
  line-height: 1.5;
}

.card-footer {
  display: flex;
  gap: 12px;
}

.card-footer .el-button {
  flex: 1;
}

/* Agents Section */
.agents-section {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 20px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-highlight);
  margin-bottom: 16px;
}

.agents-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
}

.agent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--color-border-light);
  border-radius: 6px;
  transition: all 0.2s;
}

.agent-item:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--color-primary-light);
}

.agent-info {
  flex: 1;
}

.agent-name {
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 2px;
}

.agent-role {
  font-size: 11px;
  color: var(--color-text-tertiary);
}

@media (max-width: 1400px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}
</style>
