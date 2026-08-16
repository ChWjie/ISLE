<template>
  <el-drawer
    v-model="visible"
    :title="agent ? '智能体配置详情' : '创建智能体'"
    size="600px"
    :before-close="handleClose"
    class="agent-config-drawer"
    direction="rtl"
    destroy-on-close
  >
    <div class="drawer-layout">
        <div class="header-desc">
            配置智能体的基本身份、模型参数、接口设置、能力参数等完整配置信息
        </div>

        <el-tabs v-model="activeTab" class="custom-tabs">
            <el-tab-pane label="基本信息" name="basic">
                <div class="tab-content custom-scrollbar">
                    <div class="section-title">基本身份</div>
                    <el-form label-position="top" size="small">
                        <el-form-item label="智能体唯一标识">
                            <el-input :model-value="agent?.id" disabled placeholder="系统自动生成">
                                <template #append>系统自动生成</template>
                            </el-input>
                        </el-form-item>
                        <div class="cols-2">
                             <el-form-item label="智能体名称">
                                <el-input v-model="form.name" />
                             </el-form-item>
                             <el-form-item label="智能体类型">
                                <el-select v-model="form.type" style="width:100%">
                                    <el-option label="博弈律师" value="game_lawyer" />
                                    <el-option label="分析律师" value="analysis_lawyer" />
                                </el-select>
                             </el-form-item>
                        </div>
                         <el-form-item label="智能体描述">
                            <el-input v-model="form.description" type="textarea" :rows="4" />
                        </el-form-item>
                    </el-form>

                    <div class="section-title mt-4">角色与职责</div>
                     <el-form label-position="top" size="small">
                         <el-form-item label="角色使命说明">
                            <el-input v-model="form.mission" type="textarea" :rows="3" placeholder="为国际涉海事件提供中立、结构化、可审计的法律分析..." />
                        </el-form-item>
                         <el-form-item label="核心职责范围">
                            <el-input v-model="form.responsibilities" type="textarea" :rows="3" placeholder="争点拆解; 事实模式分析; 法律适用判断..." />
                        </el-form-item>
                     </el-form>
                </div>
            </el-tab-pane>

            <el-tab-pane label="模型与接口" name="models">
                <div class="tab-content custom-scrollbar">
                    <div class="section-title">模型配置</div>
                    <el-form label-position="top" size="small">
                        <div class="cols-2">
                           <el-form-item label="主要LLM模型">
                                <el-select v-model="form.model" style="width:100%">
                                    <el-option label="GPT-4 Turbo" value="gpt-4-turbo" />
                                    <el-option label="Claude 3 Opus" value="claude-3-opus" />
                                </el-select>
                           </el-form-item>
                           <el-form-item label="模型版本">
                               <el-input v-model="form.modelVersion" disabled />
                           </el-form-item>
                        </div>
                        <el-form-item label="模型温度 (Temperature)">
                            <div class="slider-row">
                                <el-slider v-model="form.temperature" :min="0" :max="2" :step="0.1" input-size="small" show-input />
                            </div>
                        </el-form-item>
                    </el-form>

                    <div class="section-title mt-4">接口配置</div>
                    <el-form label-position="top" size="small">
                         <el-form-item label="API端点 URL">
                            <el-input v-model="form.apiUrl" />
                        </el-form-item>
                        <el-form-item label="API密钥配置">
                            <el-input v-model="form.apiKey" type="password" show-password placeholder="密钥安全存储，仅显示前3位和后3位" />
                        </el-form-item>
                    </el-form>
                </div>
            </el-tab-pane>

            <el-tab-pane label="分析策略" name="policy">
                <div class="tab-content custom-scrollbar">
                    <div class="section-title">分析范围</div>
                     <el-form label-position="top" size="small">
                         <el-form-item label="分析维度">
                             <el-checkbox-group v-model="form.analysisDimensions">
                                <el-checkbox label="事实一致性" />
                                <el-checkbox label="法律关联性" />
                                <el-checkbox label="升级风险" />
                                <el-checkbox label="不确定性分析" />
                                <el-checkbox label="证据缺口" />
                                <el-checkbox label="成本效益分析" />
                             </el-checkbox-group>
                         </el-form-item>
                         <el-form-item label="排除的分析维度">
                             <el-input v-model="form.excludedDimensions" type="textarea" :rows="2" placeholder="政治价值判断; 道德评价; 情感分析" />
                         </el-form-item>
                         <el-form-item label="专业领域">
                             <el-checkbox-group v-model="form.knowledge_scope">
                                <el-checkbox
                                    v-for="cat in lawCategories"
                                    :key="cat"
                                    :label="cat"
                                />
                             </el-checkbox-group>
                         </el-form-item>
                     </el-form>

                     <div class="section-title mt-4">推理策略</div>
                     <el-form label-position="top" size="small">
                          <div class="cols-2">
                              <el-form-item label="推理风格">
                                  <el-select v-model="form.reasoningStyle" style="width:100%">
                                      <el-option label="结构化分析型" value="structured" />
                                  </el-select>
                              </el-form-item>
                              <el-form-item label="推理深度">
                                  <el-select v-model="form.reasoningDepth" style="width:100%">
                                      <el-option label="深度" value="deep" />
                                  </el-select>
                              </el-form-item>
                          </div>

                          <el-form-item label="法律条文引用深度">
                              <div class="slider-row">
                                  <el-slider v-model="form.citationDepth" :min="1" :max="10" :step="1" show-input />
                                  <span class="slider-hint">1-3 浅层 | 4-7 中等 | 8-10 深度</span>
                              </div>
                          </el-form-item>

                          <el-form-item label="推理精度">
                              <div class="slider-row">
                                  <el-slider v-model="form.accuracy" :min="1" :max="10" :step="1" show-input />
                                  <span class="slider-hint">1-3 快速 | 4-7 平衡 | 8-10 高精度</span>
                              </div>
                          </el-form-item>

                          <el-form-item label="推理链最大长度">
                              <el-input v-model="form.maxSteps" placeholder="限制推理步骤的最大数量，防止无限递归" />
                          </el-form-item>
                     </el-form>
                </div>
            </el-tab-pane>

             <el-tab-pane label="数据与输出" name="data">
                <div class="tab-content custom-scrollbar">
                     <div class="section-title">数据源配置</div>
                     <el-form label-position="top" size="small">
                         <el-form-item label="知识库连接">
                            <el-checkbox-group v-model="form.datasources">
                                <el-checkbox label="法条库" />
                                <el-checkbox label="判例库" />
                                <el-checkbox label="条约库" />
                                <el-checkbox label="学术文献库" />
                            </el-checkbox-group>
                         </el-form-item>
                         <div class="cols-2">
                             <el-form-item label="数据连接字符串">
                                 <el-input v-model="form.dbConnection" type="password" show-password />
                             </el-form-item>
                             <el-form-item label="向量数据库">
                                 <el-select v-model="form.vectorDb" style="width:100%">
                                    <el-option label="Pinecone" value="pinecone" />
                                    <el-option label="Milvus" value="milvus" />
                                 </el-select>
                             </el-form-item>
                         </div>
                         <el-form-item label="外部API数据源">
                             <el-input v-model="form.externalApis" type="textarea" :rows="3" />
                         </el-form-item>
                     </el-form>

                     <div class="section-title mt-4">输出结构</div>
                     <el-form label-position="top" size="small">
                         <div class="cols-2">
                             <el-form-item label="输出格式">
                                 <el-select v-model="form.outputFormat" style="width:100%">
                                    <el-option label="Markdown" value="markdown" />
                                    <el-option label="JSON" value="json" />
                                 </el-select>
                             </el-form-item>
                             <el-form-item label="输出语言">
                                 <el-select v-model="form.outputLang" style="width:100%">
                                    <el-option label="中文" value="zh" />
                                    <el-option label="English" value="en" />
                                 </el-select>
                             </el-form-item>
                         </div>
                         <el-form-item label="输出包含模块">
                             <el-checkbox-group v-model="form.outputModules">
                                <el-checkbox label="争点分析" />
                                <el-checkbox label="证据对齐" />
                                <el-checkbox label="风险提示" />
                                <el-checkbox label="证据缺口" />
                                <el-checkbox label="建议方案" />
                                <el-checkbox label="不确定性说明" />
                             </el-checkbox-group>
                         </el-form-item>
                         <el-form-item label="输出模板">
                             <el-input v-model="form.outputTemplate" type="textarea" :rows="4" />
                         </el-form-item>
                     </el-form>
                 </div>
             </el-tab-pane>

             <el-tab-pane label="系统配置" name="system">
                <div class="tab-content custom-scrollbar">
                    <div class="section-title">性能参数</div>
                    <el-form label-position="top" size="small">
                        <div class="cols-2">
                           <el-form-item label="最大并发数">
                               <el-input v-model="form.concurrency" />
                           </el-form-item>
                           <el-form-item label="响应超时">
                               <el-input v-model="form.timeout" />
                           </el-form-item>
                           <el-form-item label="缓存启用">
                               <el-select v-model="form.cacheEnabled" style="width:100%">
                                   <el-option label="是" value="yes" />
                                   <el-option label="否" value="no" />
                               </el-select>
                           </el-form-item>
                        </div>
                        <div class="cols-2">
                            <el-form-item label="缓存TTL">
                               <el-input v-model="form.cacheTTL" />
                           </el-form-item>
                           <el-form-item label="资源限制">
                               <el-select v-model="form.resourceLimit" style="width:100%">
                                   <el-option label="无限制" value="none" />
                               </el-select>
                           </el-form-item>
                        </div>
                    </el-form>

                    <div class="section-title mt-4">记忆与学习</div>
                    <el-form label-position="top" size="small">
                        <div class="cols-2">
                           <el-form-item label="记忆作用范围">
                               <el-select v-model="form.memoryScope" style="width:100%">
                                   <el-option label="全局记忆" value="global" />
                               </el-select>
                           </el-form-item>
                           <el-form-item label="记忆容量">
                               <el-input v-model="form.memoryCapacity" placeholder="最大记忆条目数" />
                           </el-form-item>
                        </div>
                        <el-form-item label="学习模式">
                            <el-checkbox-group v-model="form.learningModes">
                               <el-checkbox label="在线学习" />
                               <el-checkbox label="强化学习" />
                               <el-checkbox label="迁移学习" />
                            </el-checkbox-group>
                        </el-form-item>
                    </el-form>
                </div>
             </el-tab-pane>

             <el-tab-pane label="风控与合规" name="risk">
                <div class="tab-content custom-scrollbar">
                    <div class="section-title">风控与合规</div>
                     <el-form label-position="top" size="small">
                        <div class="cols-2" style="grid-template-columns: 1fr 1.5fr; align-items: center;">
                            <el-form-item label="升级风险预警机制" style="margin-bottom:0">
                                 <el-select v-model="form.riskMechanism" style="width:100%">
                                    <el-option label="启用" value="enabled" />
                                 </el-select>
                            </el-form-item>
                            <el-form-item label="风险阈值" style="margin-bottom:0">
                                <div class="slider-row">
                                    <el-slider v-model="form.riskThreshold" :format-tooltip="(val: number) => val + '%'" />
                                    <span class="slider-value">{{ form.riskThreshold }}%</span>
                                </div>
                            </el-form-item>
                        </div>
                         <el-form-item label="禁止输出内容" class="mt-4">
                             <el-input v-model="form.forbiddenContent" type="textarea" :rows="3" />
                        </el-form-item>
                        <el-form-item label="内容审核规则">
                             <el-checkbox-group v-model="form.auditRules">
                                <el-checkbox label="自动审核" />
                                <el-checkbox label="关键词过滤" />
                                <el-checkbox label="人工审核" />
                             </el-checkbox-group>
                        </el-form-item>
                     </el-form>
                </div>
             </el-tab-pane>
        </el-tabs>

        <div class="drawer-footer">
            <el-button type="primary" @click="save">保存配置</el-button>
            <el-button @click="handleClose">返回</el-button>
        </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import type { Agent } from '@/types'
import { lawApi } from '@/api/library'

const props = defineProps<{
    visible: boolean,
    agent: Agent | null
}>()

const emit = defineEmits(['update:visible', 'save'])

const activeTab = ref('basic')
const lawCategories = ref<string[]>([])

const form = ref({
    name: '',
    type: 'analysis_lawyer',
    description: '',
    mission: '',
    responsibilities: '',
    model: 'gpt-4-turbo',
    modelVersion: 'gpt-4-preview',
    temperature: 0.7,
    apiUrl: 'https://api.openai.com/v1/chat/completions',
    apiKey: '',
    analysisDimensions: ['事实一致性', '法律关联性', '升级风险', '不确定性分析', '证据缺口', '成本效益分析'],
    excludedDimensions: '政治价值判断; 道德评价; 情感分析',
    domains: [] as string[],
    knowledge_scope: [] as string[],
    reasoningStyle: 'structured',
    reasoningDepth: 'deep',
    citationDepth: 8,
    accuracy: 9,
    maxSteps: '10',
    datasources: ['法条库', '案例库', '条约库', '学术文献库'],
    dbConnection: '***********',
    vectorDb: 'pinecone',
    externalApis: `https://api.legal-research.com/v1/provisions\nhttps://api.case-law.org/v2/search`,
    outputFormat: 'markdown',
    outputLang: 'zh',
    outputModules: ['争点分析', '证据对齐', '风险提示', '证据缺口'],
    outputTemplate: `## 分析结果\n### 争点分析\n{{ISSUE_ANALYSIS}}\n### 证据对齐\n{{EVIDENCE_ALIGNMENT}}\n### 风险评估\n{{RISK_ASSESSMENT}}`,
    concurrency: '5',
    timeout: '120',
    cacheEnabled: 'yes',
    cacheTTL: '3600',
    resourceLimit: 'none',
    memoryScope: 'global',
    memoryCapacity: '10000',
    learningModes: ['在线学习'],
    riskMechanism: 'enabled',
    riskThreshold: 70,
    forbiddenContent: '非法指令; 明确升级建议; 不可核验指控; 政治立场表达; 军事行动建议',
    auditRules: ['自动审核', '关键词过滤']
})

const visible = computed({
    get: () => props.visible,
    set: (val) => emit('update:visible', val)
})

watch(() => props.agent, (newVal) => {
    if (newVal) {
        form.value.name = newVal.name
        form.value.description = newVal.description || ''
        if (newVal.type) {
            // Map simple types to drawer types if needed, or just assign
            form.value.type = newVal.type
        }
        if (newVal.knowledge_scope) {
            form.value.knowledge_scope = newVal.knowledge_scope
        }
        form.value.mission = newVal.mission || ''
        form.value.responsibilities = newVal.responsibilities || ''
    }
}, { immediate: true })

onMounted(async () => {
    try {
        const res = await lawApi.getCategories()
        lawCategories.value = res.data || res || ['公司法', '劳动法', '数据合规', '知识产权', '竞争法']
    } catch (e) {
        console.error('Failed to load law categories', e)
        lawCategories.value = ['公司法', '劳动法', '数据合规', '知识产权', '竞争法']
    }
})

const handleClose = () => {
    emit('update:visible', false)
}

const save = () => {
    emit('save', form.value)
    handleClose()
}
</script>

<style>
/* Global overwrite for this drawer since Element appends to body */
.agent-config-drawer.el-drawer {
    background-color: #0B1026 !important;
    border-left: 1px solid #1E3A8A !important;
    box-shadow: -10px 0 30px rgba(0, 0, 0, 0.5) !important;
}
.agent-config-drawer .el-drawer__header {
    color: #fff;
    margin-bottom: 0;
    padding: 16px 20px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    background-color: #0F172A !important;
}
.agent-config-drawer .el-drawer__body {
    padding: 0;
    overflow: hidden;
    background-color: #0B1026 !important;
}
.agent-config-drawer .el-drawer__close-btn {
    color: #fff !important;
}
.agent-config-drawer .el-drawer__close-btn:hover {
    color: #3B82F6 !important;
}
</style>

<style scoped>
.drawer-layout {
    display: flex;
    flex-direction: column;
    height: 100%;
    color: #fff;
    background: #0B1026; /* Ensure background is dark */
    font-family: 'Inter', sans-serif;
}
.header-desc {
    padding: 12px 20px;
    font-size: 13px;
    color: #94A3B8; /* var(--color-text-secondary) */
    background: rgba(30, 41, 59, 0.3);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.custom-tabs {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.custom-tabs :deep(.el-tabs__header) {
    margin: 0;
    background: rgba(15, 23, 42, 0.8);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.custom-tabs :deep(.el-tabs__nav-wrap::after) {
    height: 1px;
    background-color: transparent;
}
.custom-tabs :deep(.el-tabs__item) {
    color: #64748B;
    font-size: 14px;
    height: 48px;
    line-height: 48px;
    transition: all 0.3s;
}
.custom-tabs :deep(.el-tabs__item:hover) {
    color: #CBD5E1;
}
.custom-tabs :deep(.el-tabs__item.is-active) {
    color: #3B82F6; /* var(--color-primary) */
    font-weight: 600;
}
.custom-tabs :deep(.el-tabs__active-bar) {
    background-color: #3B82F6;
    height: 3px;
    border-radius: 3px;
}
.custom-tabs :deep(.el-tabs__content) {
    flex: 1;
    overflow: hidden;
    background: transparent;
}
.custom-tabs :deep(.el-tab-pane) {
    height: 100%;
}

.tab-content {
    height: 100%;
    overflow-y: auto;
    padding: 24px;
}

.section-title {
    font-size: 14px;
    font-weight: 700;
    color: #60A5FA;
    margin-bottom: 16px;
    padding-left: 10px;
    border-left: 3px solid #3B82F6;
    letter-spacing: 0.5px;
}
.mt-4 { margin-top: 32px; }

.cols-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
}

.drawer-footer {
    padding: 16px 24px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    justify-content: flex-end;
    gap: 16px;
    background: #0F172A;
}

/* Form Styles Override for Dark Mode */
:deep(.el-form-item__label) {
    color: #CBD5E1;
    font-size: 13px;
    padding-bottom: 8px;
    font-weight: 500;
}
:deep(.el-input__wrapper), :deep(.el-textarea__inner), :deep(.el-select__wrapper) {
    background-color: rgba(255, 255, 255, 0.03) !important;
    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.1) inset !important;
    color: #fff !important;
    border-radius: 4px;
    transition: all 0.2s;
}
:deep(.el-input__wrapper:hover), :deep(.el-textarea__inner:hover), :deep(.el-select__wrapper:hover) {
    box-shadow: 0 0 0 1px #3B82F6 inset !important;
    background-color: rgba(59, 130, 246, 0.05) !important;
}
:deep(.el-input__wrapper.is-focus), :deep(.el-textarea__inner:focus), :deep(.el-select__wrapper.is-focused) {
    box-shadow: 0 0 0 1px #3B82F6 inset !important;
    background-color: rgba(59, 130, 246, 0.1) !important;
}
/* Select Options Popover */
:deep(.el-popper.is-light) {
    background: #1E293B !important;
    border: 1px solid #334155 !important;
}
:deep(.el-select-dropdown__item) {
    color: #CBD5E1;
}
:deep(.el-select-dropdown__item.hover), :deep(.el-select-dropdown__item:hover) {
    background-color: rgba(59, 130, 246, 0.1);
    color: #fff;
}
:deep(.el-select-dropdown__item.selected) {
    color: #3B82F6;
    font-weight: bold;
}

/* Checkboxes */
:deep(.el-checkbox) {
    color: #CBD5E1;
}
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: #3B82F6;
    border-color: #3B82F6;
}
:deep(.el-checkbox__inner) {
    background-color: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.2);
}

/* Slider Row */
.slider-row {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 0 4px;
}
.slider-row :deep(.el-slider) {
    flex: 1;
}
.slider-row :deep(.el-slider__runway) {
    background-color: rgba(255,255,255,0.1);
}
.slider-row :deep(.el-slider__bar) {
    background-color: #3B82F6;
}
.slider-row :deep(.el-slider__button) {
    border-color: #3B82F6;
    background-color: #0B1026;
}
.slider-hint {
    font-size: 12px;
    color: #64748B;
    white-space: nowrap;
}
.slider-value {
    font-size: 13px;
    color: #60A5FA;
    font-family: monospace;
    font-weight: bold;
    width: 40px;
    text-align: right;
}

/* Scrollbar */
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(71, 85, 105, 0.5); border-radius: 3px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
</style>
