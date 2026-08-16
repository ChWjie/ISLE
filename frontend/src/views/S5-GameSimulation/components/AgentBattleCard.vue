<template>
  <div
    class="agent-battle-card"
    :class="[side, { active: isActive }]"
  >
    <div class="avatar-container">
      <div class="avatar-ring">
        <img :src="agent.avatar || `https://api.dicebear.com/7.x/avataaars/svg?seed=${agent.id}`" alt="avatar" />
      </div>
      <div class="pulse-ring" v-if="isActive"></div>
    </div>

    <div class="agent-info">
      <div class="name">{{ agent.name }}</div>
      <div class="role">{{ agent.role }}</div>
    </div>

    <div class="status-indicators">
       <!-- Mock confidence/health bar -->
       <div class="confidence-bar">
         <div class="fill" :style="{ width: (agent.confidence || 100) + '%' }"></div>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">


const props = defineProps<{
  agent: {
    id: string
    name: string
    role: string
    avatar?: string
    confidence?: number
  }
  isActive: boolean
  side: 'our' | 'opponent'
}>()
</script>

<style scoped>
.agent-battle-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 120px;
  position: relative;
  transition: all 0.3s ease;
  opacity: 0.8;
  transform: scale(0.95);
}

.agent-battle-card.active {
  opacity: 1;
  transform: scale(1.05) translateY(-10px);
  z-index: 10;
}

/* Avatar */
.avatar-container {
  width: 80px;
  height: 80px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 12px;
}

.avatar-ring {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.2);
  padding: 3px;
  background: rgba(0, 0, 0, 0.3);
  z-index: 2;
  overflow: hidden;
}

.agent-battle-card.our .avatar-ring { border-color: #3B82F6; }
.agent-battle-card.opponent .avatar-ring { border-color: #EF4444; }

.avatar-ring img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

/* Pulse Animation */
.pulse-ring {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 4px solid;
  opacity: 0;
  animation: pulse 2s infinite;
  z-index: 1;
}

.agent-battle-card.our .pulse-ring { border-color: rgba(59, 130, 246, 0.6); }
.agent-battle-card.opponent .pulse-ring { border-color: rgba(239, 68, 68, 0.6); }

@keyframes pulse {
  0% { width: 100%; height: 100%; opacity: 0.8; }
  100% { width: 160%; height: 160%; opacity: 0; }
}

/* Info */
.agent-info {
  text-align: center;
  background: rgba(0, 0, 0, 0.6);
  padding: 4px 8px;
  border-radius: 4px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  width: 100%;
}

.name {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.role {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.7);
}

/* Indicators */
.status-indicators {
  width: 80%;
  margin-top: 6px;
}

.confidence-bar {
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
}

.confidence-bar .fill {
  height: 100%;
  background: #10B981;
  transition: width 0.3s;
}
</style>
