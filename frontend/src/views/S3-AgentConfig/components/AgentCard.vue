<template>
  <div class="agent-card" :class="{ selected: isSelected }" @click="$emit('toggle')">
    <div class="card-top">
       <div class="avatar-wrap">
          <el-avatar :size="40" :src="agent.avatar">A</el-avatar>
          <div class="expert-badge" v-if="agent.is_expert">专家</div>
       </div>
       <div class="info-col">
          <div class="name-row">
             <span class="name">{{ agent.name }}</span>
          </div>
          <div class="tags-row">
             <span class="tag" v-for="(domain, i) in agent.law_domains" :key="i">{{ domain }}</span>
          </div>
       </div>
       <div class="checkbox">
          <div class="check-circle" :class="{ checked: isSelected }">
             <el-icon v-if="isSelected"><Check /></el-icon>
          </div>
       </div>
    </div>

    <div class="desc-box">
       {{ agent.description }}
    </div>

    <div class="card-footer">
       <span class="time">{{ agent.created_at }}</span>
       <div class="actions">
          <el-button link type="primary" size="small" @click.stop="$emit('edit')">配置</el-button>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Check } from '@element-plus/icons-vue'
import type { Agent } from '@/types'

defineProps<{
  agent: Agent,
  isSelected: boolean
}>()

defineEmits(['toggle', 'edit'])
</script>

<style scoped>
.agent-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  position: relative;
}
.agent-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
}
.agent-card.selected {
  background: rgba(59, 130, 246, 0.15);
  border-color: #3B82F6;
}

.card-top { display: flex; gap: 12px; margin-bottom: 12px; }

.avatar-wrap { position: relative; }
.expert-badge {
  position: absolute; bottom: -4px; right: -4px;
  background: #F59E0B; color: #000; font-size: 8px; padding: 1px 3px; border-radius: 2px; font-weight: bold;
}

.info-col { flex: 1; overflow: hidden; }
.name-row { margin-bottom: 4px; }
.name { font-weight: bold; font-size: 14px; color: #fff; }

.tags-row { display: flex; gap: 4px; flex-wrap: wrap; }
.tag { font-size: 10px; background: rgba(255,255,255,0.1); padding: 1px 4px; border-radius: 2px; color: #cbd5e1; }

.checkbox { display: flex; align-items: flex-start; }
.check-circle {
  width: 18px; height: 18px; border: 1px solid rgba(255,255,255,0.3); border-radius: 50%;
  display: flex; align-items: center; justify-content: center; color: #fff; font-size: 12px;
  background: rgba(0,0,0,0.3);
}
.check-circle.checked { background: #3B82F6; border-color: #3B82F6; }

.desc-box {
  font-size: 12px; color: #94A3B8; line-height: 1.4;
  margin-bottom: 12px;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  height: 34px;
}

.card-footer {
  display: flex; justify-content: space-between; align-items: center;
  border-top: 1px dashed rgba(255,255,255,0.1);
  padding-top: 8px;
  font-size: 11px; color: #64748B;
}
</style>
