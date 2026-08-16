<template>
  <div class="plan-document">
    <div class="doc-header">
      <div class="doc-title">{{ title }}</div>
      <div class="doc-meta">
        <span>生成时间: {{ new Date().toLocaleDateString() }}</span>
        <span class="security-level">CONFIDENTIAL / 机密</span>
      </div>
    </div>

    <div class="doc-body custom-scrollbar">
      <div v-for="(section, index) in sections" :key="index" class="doc-section">
        <h3 class="section-title">{{ section.title }}</h3>
        <div class="section-content">
          <p v-if="section.content" v-html="formatContent(section.content)" class="content-text"></p>
          <div v-else class="content-placeholder">
            <el-skeleton :rows="3" animated />
          </div>
        </div>
      </div>

      <div v-if="isStreaming" class="streaming-cursor"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  sections: Array<{ title: string; content: string }>
  isStreaming: boolean
}>()

const formatContent = (text: string) => text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')
</script>

<style scoped>
.plan-document { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(10px); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 8px; display: flex; flex-direction: column; height: 100%; overflow: hidden; box-shadow: 0 0 40px rgba(0, 0, 0, 0.5); position: relative; }
.plan-document::before { content: ''; position: absolute; top: 0; left: 0; width: 20px; height: 20px; border-top: 2px solid #3b82f6; border-left: 2px solid #3b82f6; border-top-left-radius: 4px; pointer-events: none; }
.plan-document::after { content: ''; position: absolute; bottom: 0; right: 0; width: 20px; height: 20px; border-bottom: 2px solid #3b82f6; border-right: 2px solid #3b82f6; border-bottom-right-radius: 4px; pointer-events: none; }
.doc-header { height: 70px; padding: 0 30px; background: linear-gradient(90deg, rgba(30, 58, 138, 0.4) 0%, rgba(15, 23, 42, 0.4) 100%); border-bottom: 1px solid rgba(59, 130, 246, 0.2); display: flex; justify-content: space-between; align-items: center; }
.doc-title { font-family: 'Orbitron', sans-serif; font-size: 18px; font-weight: 600; color: #e2e8f0; letter-spacing: 1px; }
.doc-meta { font-size: 11px; color: #64748b; display: flex; align-items: center; gap: 16px; text-transform: uppercase; letter-spacing: 0.5px; }
.security-level { color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.4); background: rgba(239, 68, 68, 0.1); padding: 2px 8px; border-radius: 2px; font-weight: bold; box-shadow: 0 0 10px rgba(239, 68, 68, 0.2); }
.doc-body { flex: 1; padding: 40px; overflow-y: auto; font-family: 'Inter', sans-serif; background: radial-gradient(circle at top right, rgba(30, 58, 138, 0.05), transparent 60%); }
.doc-section { margin-bottom: 40px; animation: fadeIn 0.5s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.section-title { font-size: 16px; font-weight: 600; color: #60a5fa; margin-bottom: 16px; display: flex; align-items: center; gap: 10px; border-left: 3px solid #3b82f6; padding-left: 12px; background: linear-gradient(90deg, rgba(59, 130, 246, 0.1) 0%, transparent 100%); height: 32px; line-height: 32px; }
.content-text { font-size: 14px; line-height: 1.8; color: #cbd5e1; text-align: justify; padding-left: 15px; }
:deep(strong) { color: #fff; font-weight: 700; text-shadow: 0 0 10px rgba(255, 255, 255, 0.1); }
.content-placeholder { padding-left: 15px; opacity: 0.2; }
.streaming-cursor { display: inline-block; width: 8px; height: 16px; background: #60a5fa; animation: blink 1s infinite; margin-left: 4px; box-shadow: 0 0 8px #60a5fa; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }
</style>
