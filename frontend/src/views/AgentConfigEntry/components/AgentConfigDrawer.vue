<template>
  <div class="agent-config-drawer">
    <div class="drawer-header">
      <h3>博弈智能体配置详情</h3>
      <div class="header-actions">
        <el-button type="primary" size="small" @click="$emit('save')">保存配置</el-button>
        <el-button size="small" @click="$emit('close')">返回</el-button>
      </div>
    </div>

    <div class="drawer-content">
      <!-- Basic Info -->
      <div class="config-section">
        <div class="section-title">基本信息</div>

        <div class="form-item">
          <label>智能体名称</label>
          <el-input v-model="localConfig.name" placeholder="请输入智能体名称" />
          <span class="help-text">智能体的显示名称，用于标识和区分</span>
        </div>

        <div class="form-item">
          <label>专业领域</label>
          <el-select v-model="localConfig.domain" placeholder="请选择专业领域" style="width: 100%">
            <el-option label="公司治理" value="corporate_governance" />
            <el-option label="数据合规" value="data_compliance" />
            <el-option label="劳动用工" value="labor_compliance" />
          </el-select>
          <span class="help-text">智能体主要擅长的法律研究方向</span>
        </div>

        <div class="form-item">
          <label>模型副本</label>
          <el-select v-model="localConfig.model" placeholder="请选择模型" style="width: 100%">
            <el-option label="Deepseek/V3" value="deepseek-v3" />
            <el-option label="GPT-4" value="gpt-4" />
          </el-select>
          <span class="help-text">智能体的后端大模型引擎，可选多版本</span>
        </div>

        <div class="form-item">
          <label>智能体描述</label>
          <el-input
            v-model="localConfig.description"
            type="textarea"
            :rows="3"
            placeholder="结合公司法、劳动法、数据合规、知识产权等规则进行专业分析"
          />
        </div>
      </div>

      <!-- Capability Params -->
      <div class="config-section">
        <div class="section-title">法律能力参数</div>

        <div class="form-item">
          <label>专业深度</label>
          <el-select v-model="localConfig.depth" placeholder="专家级-前沿法律研究和深度分析" style="width: 100%">
             <el-option label="专家级-前沿法律研究和深度分析" value="expert" />
             <el-option label="资深级-常规法律实务分析" value="senior" />
          </el-select>
          <span class="help-text">智能体的专业深度等级，影响分析质量和服务费</span>
        </div>

        <div class="form-item">
          <label>分析倾向</label>
          <el-select v-model="localConfig.bias" placeholder="保守-严谨遵循法律条文，风格稳健" style="width: 100%">
             <el-option label="保守-严谨遵循法律条文，风格稳健" value="conservative" />
             <el-option label="激进-探索法律边缘，风格犀利" value="aggressive" />
          </el-select>
          <span class="help-text">智能体分析时的倾向性，影响结果</span>
        </div>

        <div class="form-item">
          <label>法律条文引用深度</label>
          <el-slider v-model="localConfig.citationDepth" :min="1" :max="10" :step="1" show-stops />
          <div class="slider-labels">
            <span>1-3 浅层引用</span>
            <span>4-7 中等深度</span>
            <span>8-10 深度分析</span>
          </div>
        </div>

        <div class="form-item">
          <label>推理精度</label>
          <el-slider v-model="localConfig.reasoningPrecision" :min="1" :max="10" :step="1" show-stops />
          <div class="slider-labels">
            <span>1-3 快速响应</span>
            <span>4-7 平衡</span>
            <span>8-10 高精度推理</span>
          </div>
        </div>
      </div>

       <!-- Output Settings -->
      <div class="config-section">
        <div class="section-title">输出设置</div>
         <div class="form-item">
          <label>输出格式</label>
          <el-select v-model="localConfig.format" placeholder="Markdown" style="width: 100%">
             <el-option label="Markdown-支持富文本格式" value="markdown" />
             <el-option label="Plain Text" value="text" />
          </el-select>
        </div>
        <div class="form-item">
          <label>语言设置</label>
           <el-select v-model="localConfig.language" placeholder="中文" style="width: 100%">
             <el-option label="中文" value="zh" />
             <el-option label="English" value="en" />
          </el-select>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  agent: any
}>()

const localConfig = ref({
  name: '',
  domain: '',
  model: '',
  description: '',
  depth: '',
  bias: '',
  citationDepth: 5,
  reasoningPrecision: 5,
  format: 'markdown',
  language: 'zh'
})

// Initialize form
watch(() => props.agent, (agent) => {
  if (agent) {
    localConfig.value = {
      name: agent.name || '',
      domain: agent.domain || 'corporate_governance',
      model: agent.model || 'deepseek-v3',
      description: agent.description || '',
      depth: 'expert',
      bias: 'conservative',
      citationDepth: 8,
      reasoningPrecision: 7,
      format: 'markdown',
      language: 'zh'
    }
  }
}, { immediate: true })

const emit = defineEmits(['close', 'save'])
</script>

<style scoped>
.agent-config-drawer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-secondary);
  border-left: 1px solid var(--color-border);
}

.drawer-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.2);
}

.drawer-header h3 {
  margin: 0;
  font-size: 16px;
  color: #fff;
}

.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.config-section {
  margin-bottom: 30px;
}

.section-title {
  font-size: 14px;
  color: var(--color-primary-light);
  font-weight: 600;
  margin-bottom: 20px;
  padding-bottom: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  font-size: 13px;
  color: #fff;
  margin-bottom: 8px;
}

.help-text {
  display: block;
  font-size: 12px;
  color: var(--color-text-tertiary);
  margin-top: 6px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: var(--color-text-tertiary);
  margin-top: 4px;
}

/* Custom Scrollbar */
.drawer-content::-webkit-scrollbar { width: 6px; }
.drawer-content::-webkit-scrollbar-thumb { background: var(--color-border-light); border-radius: 3px; }
</style>
