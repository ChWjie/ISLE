<template>
  <el-drawer
    v-model="visible"
    title="智能体配置详情"
    size="500px"
    direction="rtl"
    class="config-drawer"
  >
    <el-tabs v-model="activeTab" class="config-tabs">
      <!-- Tab 1: 基本信息 -->
      <el-tab-pane label="基本信息" name="basic">
        <div class="tab-content">
          <div class="info-group">
            <div class="label">智能体ID</div>
            <div class="value">AGENT-COMPLIANCE-EXP-001</div>
          </div>
          <div class="info-group">
            <div class="label">智能体名称</div>
            <div class="value">企业合规专家</div>
          </div>
          <div class="info-group">
            <div class="label">生成时间</div>
            <div class="value">2025-12-22 14:30</div>
          </div>
          <div class="info-group">
            <div class="label">法律主体定位</div>
            <div class="value">中国海警、中国渔业局</div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 2: 角色定位 -->
      <el-tab-pane label="角色定位" name="role">
        <div class="tab-content">
          <div class="role-description">
            <h4>核心职责</h4>
            <p>基于企业合规、合同履约、数据治理等法律规则进行分析，评估我方行为的合法性基础，识别对方可能的反制论点。</p>
          </div>
          <div class="capabilities">
            <h4>能力配置</h4>
            <ul>
              <li>✓ 企业合规分析能力（合同/劳动/数据/知识产权）</li>
              <li>✓ 证据链构建能力</li>
              <li>✓ 风险预测能力</li>
            </ul>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 3: 分析目标 -->
      <el-tab-pane label="分析目标" name="goals">
        <div class="tab-content">
          <div class="goals-list">
            <div class="goal-item">
              <el-checkbox checked disabled>维护海洋权益与主权权利</el-checkbox>
            </div>
            <div class="goal-item">
              <el-checkbox checked disabled>证明我方行为的合法性与正当性</el-checkbox>
            </div>
            <div class="goal-item">
              <el-checkbox disabled>降低争议升级风险</el-checkbox>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <!-- Tab 4: 核心依据法条 -->
      <el-tab-pane label="核心依据法条" name="legal">
        <div class="tab-content">
          <div class="legal-list">
            <div class="legal-item">
              <div class="legal-title">《个人信息保护法》相关条款</div>
              <div class="legal-desc">沿海国在专属经济区内的权利、管辖权和义务</div>
            </div>
            <div class="legal-item">
              <div class="legal-title">《劳动合同法》或《公司法》相关条款</div>
              <div class="legal-desc">所有国家在专属经济区内的权利和义务</div>
            </div>
            <div class="legal-item">
              <div class="legal-title">《中华人民共和国海警法》</div>
              <div class="legal-desc">海警机构执法权限与程序</div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <div class="drawer-footer">
        <el-button @click="visible = false">关闭</el-button>
        <el-button type="primary">保存配置</el-button>
      </div>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  modelValue: boolean
  agentId?: string
}>()

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const activeTab = ref('basic')
</script>

<style scoped>
.config-tabs {
  height: 100%;
}

.config-tabs :deep(.el-tabs__content) {
  padding: 20px;
}

.tab-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.label {
  font-size: 12px;
  color: var(--color-text-secondary);
  font-weight: 600;
}

.value {
  font-size: 14px;
  color: var(--color-text-highlight);
}

.role-description h4,
.capabilities h4 {
  font-size: 14px;
  color: var(--color-primary-light);
  margin-bottom: 12px;
}

.role-description p {
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.6;
}

.capabilities ul {
  list-style: none;
  padding: 0;
}

.capabilities li {
  font-size: 13px;
  color: var(--color-text-secondary);
  padding: 8px 0;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legal-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.legal-item {
  padding: 16px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 6px;
}

.legal-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary-light);
  margin-bottom: 8px;
}

.legal-desc {
  font-size: 12px;
  color: var(--color-text-secondary);
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid var(--color-border);
}
</style>
