<template>
  <div class="law-library-page">
    <div class="page-header">
      <h1 class="page-title">法律资源库</h1>
      <p class="subtitle">企业合规、争议解决与监管执法相关法规资料，共 <span class="highlight">{{ allLaws.length }}</span> 条。</p>
    </div>

    <div class="library-content" v-loading="loading" element-loading-background="rgba(0, 0, 0, 0.7)">
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索法规名称、条文内容、案例关键词..."
          size="large"
          clearable
          class="cyber-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <div class="library-categories">
        <div
          v-for="category in categories"
          :key="category.id"
          class="category-card"
          :class="{ active: selectedCategory === category.key }"
          @click="selectCategory(category.key)"
        >
          <div class="category-icon">{{ category.icon }}</div>
          <h3>{{ category.title }}</h3>
          <p>{{ category.desc }}</p>
          <div class="category-count">{{ category.count }} 条</div>
        </div>
      </div>

      <div class="recent-laws">
        <div class="section-header">
          <h2>{{ selectedCategory ? `${selectedCategory}（${filteredLaws.length}）` : `全部法规（${filteredLaws.length}）` }}</h2>
        </div>
        <el-table :data="recentLaws" class="cyber-table" :header-cell-style="{ background: 'rgba(30, 41, 59, 0.8)', color: '#94A3B8' }" :row-style="{ background: 'transparent', color: '#E2E8F0' }">
          <el-table-column prop="code" label="编号" width="180">
            <template #default="{ row }">
              <span class="law-code">{{ row.code }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="title" label="标题" />
          <el-table-column prop="category" label="类别" width="140">
            <template #default="{ row }">
              <span class="law-tag">{{ row.category }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="date" label="更新日期" width="140" />
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="primary" link class="action-link" @click="viewLaw(row.code)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { lawApi } from '@/api/library'
import { ElMessage } from 'element-plus'

const searchQuery = ref('')
const loading = ref(false)
const allLaws = ref<any[]>([])
const selectedCategory = ref('')

const categories = computed(() => {
  const categoryCounts: Record<string, number> = {}
  allLaws.value.forEach(law => {
    categoryCounts[law.category] = (categoryCounts[law.category] || 0) + 1
  })

  return [
    { id: 1, icon: '🏢', title: '公司治理', key: '公司治理', desc: '公司法、股权治理、董监高责任', count: categoryCounts['公司治理'] || 0 },
    { id: 2, icon: '🛡️', title: '数据合规', key: '数据合规', desc: '数据安全法、个保法、网络安全', count: categoryCounts['数据合规'] || 0 },
    { id: 3, icon: '👥', title: '劳动用工', key: '劳动用工', desc: '劳动合同、员工关系、社保用工', count: categoryCounts['劳动用工'] || 0 },
    { id: 4, icon: '📝', title: '合同交易', key: '合同交易', desc: '合同审查、履约争议、违约责任', count: categoryCounts['合同交易'] || 0 },
    { id: 5, icon: '⚖️', title: '监管执法', key: '监管执法', desc: '行政处罚、行政复议、监管问询', count: categoryCounts['监管执法'] || 0 }
  ]
})

const filteredLaws = computed(() => {
  let laws = allLaws.value

  if (selectedCategory.value) {
    laws = laws.filter(law => law.category === selectedCategory.value)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    laws = laws.filter(law =>
      String(law.name_zh || '').toLowerCase().includes(query) ||
      String(law.content || '').toLowerCase().includes(query) ||
      String(law.code || '').toLowerCase().includes(query)
    )
  }

  return laws
})

const recentLaws = computed(() => {
  return filteredLaws.value.slice(0, 10).map(law => ({
    code: law.code,
    title: law.name_zh,
    category: law.category,
    date: law.updated_at ? new Date(law.updated_at).toLocaleDateString('zh-CN') : '-',
    summary: law.summary,
    content: law.content
  }))
})

const loadLaws = async () => {
  loading.value = true
  try {
    const response = await lawApi.getLaws({ limit: 100 })
    allLaws.value = response.data || response || []
  } catch (error) {
    console.error('Failed to load laws:', error)
    if (allLaws.value.length === 0) {
      allLaws.value = [
        { code: 'PIPL-13', name_zh: '个人信息保护法第13条 - 个人信息处理的合法性基础', category: '数据合规', updated_at: '2026-01-14', content: '处理个人信息应当具有明确的合法性基础。' },
        { code: 'DSL-21', name_zh: '数据安全法第21条 - 数据分类分级保护', category: '数据合规', updated_at: '2026-01-14', content: '国家建立数据分类分级保护制度。' },
        { code: 'LABOR-39', name_zh: '劳动合同法第39条 - 用人单位解除劳动合同', category: '劳动用工', updated_at: '2025-12-10', content: '劳动者存在严重违纪等情形时，用人单位可以解除劳动合同。' }
      ]
    }
  } finally {
    loading.value = false
  }
}

const viewLaw = (code: string) => {
  const law = allLaws.value.find(l => l.code === code)
  if (law) {
    ElMessage({
      message: `${law.name_zh}\n\n${law.content}`,
      type: 'info',
      duration: 5000,
      showClose: true,
      grouping: true,
    })
  }
}

const selectCategory = (categoryKey: string) => {
  selectedCategory.value = selectedCategory.value === categoryKey ? '' : categoryKey
}

onMounted(() => {
  loadLaws()
})
</script>

<style scoped>
.law-library-page {
  padding: 40px;
  max-width: 1600px;
  margin: 0 auto;
  min-height: 100vh;
  background: #020617;
  color: #fff;
  font-family: 'Inter', sans-serif;
}
.page-header {
  margin-bottom: 40px;
}
.page-title {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
}
.subtitle {
  margin: 0;
  color: #94A3B8;
  font-size: 14px;
}
.highlight { color: #3B82F6; font-weight: bold; }
.search-bar { margin-bottom: 32px; }
:deep(.cyber-input .el-input__wrapper) {
  background: rgba(30, 41, 59, 0.5) !important;
  box-shadow: none !important;
  border: 1px solid rgba(255,255,255,0.1);
  color: #fff;
  padding: 8px 15px;
}
.library-categories {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}
.category-card {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.15);
  border-radius: 14px;
  padding: 20px;
  cursor: pointer;
}
.category-card.active { border-color: #3B82F6; }
.category-icon { font-size: 28px; }
.category-count { color: #60A5FA; margin-top: 8px; }
.recent-laws {
  background: rgba(15, 23, 42, 0.8);
  border-radius: 16px;
  padding: 24px;
}
.section-header { margin-bottom: 16px; }
.law-code, .law-tag { color: #93C5FD; }
.action-link { color: #60A5FA; }
:deep(.cyber-table) {
  --el-table-border-color: rgba(148, 163, 184, 0.14);
  --el-table-row-hover-bg-color: rgba(30, 41, 59, 0.55);
  background: transparent !important;
  color: #e2e8f0 !important;
}
:deep(.cyber-table .el-table__inner-wrapper),
:deep(.cyber-table .el-table__body-wrapper),
:deep(.cyber-table .el-scrollbar__view),
:deep(.cyber-table tr),
:deep(.cyber-table td.el-table__cell),
:deep(.cyber-table th.el-table__cell) {
  background: transparent !important;
  color: #e2e8f0 !important;
}
:deep(.cyber-table::before),
:deep(.cyber-table .el-table__inner-wrapper::before) {
  background-color: rgba(148, 163, 184, 0.14) !important;
}
:deep(.cyber-table .el-table__header-wrapper th.el-table__cell) {
  background: rgba(30, 41, 59, 0.9) !important;
  color: #94a3b8 !important;
}
:deep(.cyber-table .el-table__body tr:hover > td.el-table__cell) {
  background: rgba(30, 41, 59, 0.55) !important;
}
</style>
