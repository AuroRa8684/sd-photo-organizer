<template>
  <div class="summary-page">
    <div class="page-header">
      <h1>📊 拍摄总结</h1>
      <p>查看统计数据和AI生成的拍摄复盘</p>
    </div>

    <el-row :gutter="20">
      <!-- 左侧：生成和历史 -->
      <el-col :span="6">
        <!-- 生成新总结 -->
        <div class="content-card">
          <h3>📅 生成新总结</h3>
          <div class="date-selector">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始"
              end-placeholder="结束"
              style="width: 100%; margin-bottom: 12px"
              size="small"
            />
            <el-button type="primary" @click="handleGenerate" :loading="loading" style="width: 100%">
              <el-icon><DataAnalysis /></el-icon>
              生成总结
            </el-button>
            <el-button @click="handleGenerateAll" :loading="loading" style="width: 100%; margin-top: 8px">
              全部数据
            </el-button>
          </div>
        </div>

        <!-- 历史记录 -->
        <div class="content-card history-card">
          <h3>📜 历史记录</h3>
          <div v-if="historyLoading" class="loading-small">
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
          <div v-else-if="historyList.length === 0" class="empty-small">
            暂无历史记录
          </div>
          <div v-else class="history-list">
            <div
              v-for="item in historyList"
              :key="item.id"
              class="history-item"
              :class="{ active: selectedHistoryId === item.id }"
              @click="loadHistoryDetail(item.id)"
            >
              <div class="title">{{ item.title }}</div>
              <div class="meta">
                {{ formatHistoryDate(item.created_at) }} · {{ item.total_photos }}张
              </div>
              <el-icon class="delete-btn" @click.stop="deleteHistory(item.id)">
                <Delete />
              </el-icon>
            </div>
          </div>
        </div>
      </el-col>

      <!-- 右侧：总结内容 -->
      <el-col :span="18">
        <!-- 概览统计 -->
        <el-row :gutter="20" class="stats-row" v-if="summary">
          <el-col :span="6">
            <div class="content-card stat-card">
              <div class="stat-value">{{ summary.stats?.total || 0 }}</div>
              <div class="stat-label">总照片数</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="content-card stat-card">
              <div class="stat-value">{{ summary.stats?.with_raw || 0 }}</div>
              <div class="stat-label">含RAW照片</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="content-card stat-card">
              <div class="stat-value">{{ summary.stats?.selected || 0 }}</div>
              <div class="stat-label">精选照片</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="content-card stat-card">
              <div class="stat-value">{{ Object.keys(summary.stats?.categories || {}).length }}</div>
              <div class="stat-label">类别数量</div>
            </div>
          </el-col>
        </el-row>

        <!-- 图表区域 -->
        <el-row :gutter="20" v-if="summary?.charts">
          <el-col :span="12">
            <div class="content-card chart-card">
              <h3>📷 类别分布</h3>
              <div ref="categoryChartRef" class="chart-container"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="content-card chart-card">
              <h3>🔭 焦段分布</h3>
              <div ref="focalChartRef" class="chart-container"></div>
            </div>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="summary?.charts">
          <el-col :span="12">
            <div class="content-card chart-card">
              <h3>🎚️ ISO分布</h3>
              <div ref="isoChartRef" class="chart-container"></div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="content-card chart-card">
              <h3>📸 相机使用</h3>
              <div ref="cameraChartRef" class="chart-container"></div>
            </div>
          </el-col>
        </el-row>

        <!-- AI总结 -->
        <div class="content-card" v-if="summary?.ai_summary">
          <h3>🤖 AI拍摄复盘</h3>
          <div class="ai-summary-content">
            <div v-html="formatSummary(summary.ai_summary)"></div>
          </div>
        </div>

        <!-- 空状态 -->
        <div class="content-card" v-if="!summary && !loading">
          <div class="empty-state">
            <el-icon><DataAnalysis /></el-icon>
            <p>点击左侧"生成总结"按钮创建新的拍摄总结</p>
            <p class="sub">或从历史记录中选择查看</p>
            <div class="quick-tips">
              <h4>📌 快速指南</h4>
              <ul>
                <li>选择日期范围后点击"生成总结"</li>
                <li>点击"全部数据"可分析所有已导入照片</li>
                <li>生成的总结会自动保存到历史记录</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- 加载状态 -->
        <div class="content-card" v-if="loading">
          <div class="loading-overlay">
            <el-icon class="is-loading" :size="48"><Loading /></el-icon>
            <p>正在生成总结，请稍候...</p>
            <p class="loading-tip">AI分析可能需要10-30秒</p>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DataAnalysis, Loading, Delete } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { generateSummary, getSummaryHistory, getSummaryHistoryDetail, deleteSummaryHistory } from '@/api'

// 数据
const dateRange = ref(null)
const summary = ref(null)
const loading = ref(false)

// 历史记录
const historyList = ref([])
const historyLoading = ref(false)
const selectedHistoryId = ref(null)

// 图表引用
const categoryChartRef = ref(null)
const focalChartRef = ref(null)
const isoChartRef = ref(null)
const cameraChartRef = ref(null)

// 图表实例
let categoryChart = null
let focalChart = null
let isoChart = null
let cameraChart = null

// 加载历史记录列表
const loadHistoryList = async () => {
  historyLoading.value = true
  try {
    const res = await getSummaryHistory(20)
    historyList.value = res.data || []
  } catch (e) {
    console.error('加载历史记录失败:', e)
  } finally {
    historyLoading.value = false
  }
}

// 加载历史详情
const loadHistoryDetail = async (historyId) => {
  loading.value = true
  selectedHistoryId.value = historyId
  summary.value = null
  
  try {
    const res = await getSummaryHistoryDetail(historyId)
    summary.value = res.data
    
    await nextTick()
    renderCharts()
  } catch (e) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

// 删除历史记录
const deleteHistory = async (historyId) => {
  try {
    await ElMessageBox.confirm('确定要删除这条历史记录吗？', '确认删除', { type: 'warning' })
    await deleteSummaryHistory(historyId)
    ElMessage.success('删除成功')
    
    if (selectedHistoryId.value === historyId) {
      summary.value = null
      selectedHistoryId.value = null
    }
    
    loadHistoryList()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 格式化历史日期
const formatHistoryDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// 生成总结
const handleGenerate = async () => {
  loading.value = true
  summary.value = null
  selectedHistoryId.value = null
  
  try {
    const params = { save_history: true }
    if (dateRange.value && dateRange.value.length === 2) {
      params.date_from = dateRange.value[0].toISOString()
      params.date_to = dateRange.value[1].toISOString()
    }
    
    const res = await generateSummary(params)
    
    if (!res.data.success) {
      ElMessage.warning(res.data.message || '无数据可用于生成总结')
      return
    }
    
    summary.value = res.data
    
    // 刷新历史列表
    loadHistoryList()
    
    // 等待DOM更新后渲染图表
    await nextTick()
    renderCharts()
    
    ElMessage.success('总结生成成功')
    
  } catch (error) {
    ElMessage.error('生成总结失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 生成全部数据的总结
const handleGenerateAll = async () => {
  dateRange.value = null
  await handleGenerate()
}

// 渲染图表
const renderCharts = () => {
  if (!summary.value?.charts) return
  
  const charts = summary.value.charts
  
  // 类别分布饼图
  if (categoryChartRef.value && charts.category_pie?.data?.length) {
    categoryChart = echarts.init(categoryChartRef.value)
    categoryChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: charts.category_pie.data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
  
  // 焦段分布柱状图
  if (focalChartRef.value && charts.focal_bar?.categories?.length) {
    focalChart = echarts.init(focalChartRef.value)
    focalChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: charts.focal_bar.categories,
        axisLabel: { rotate: 30, fontSize: 10 }
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: charts.focal_bar.values,
        itemStyle: { color: '#409EFF' }
      }]
    })
  }
  
  // ISO分布柱状图
  if (isoChartRef.value && charts.iso_bar?.categories?.length) {
    isoChart = echarts.init(isoChartRef.value)
    isoChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: {
        type: 'category',
        data: charts.iso_bar.categories,
        axisLabel: { rotate: 30, fontSize: 10 }
      },
      yAxis: { type: 'value' },
      series: [{
        type: 'bar',
        data: charts.iso_bar.values,
        itemStyle: { color: '#67C23A' }
      }]
    })
  }
  
  // 相机使用饼图
  if (cameraChartRef.value && charts.camera_pie?.data?.length) {
    cameraChart = echarts.init(cameraChartRef.value)
    cameraChart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: ['40%', '70%'],
        data: charts.camera_pie.data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  }
}

// 格式化AI总结（将换行转为HTML）
const formatSummary = (text) => {
  if (!text) return ''
  return text
    .replace(/\n/g, '<br>')
    .replace(/- /g, '• ')
    .replace(/(\d+\.)/, '<strong>$1</strong>')
}

// 窗口resize处理
const handleResize = () => {
  categoryChart?.resize()
  focalChart?.resize()
  isoChart?.resize()
  cameraChart?.resize()
}

onMounted(async () => {
  window.addEventListener('resize', handleResize)
  await loadHistoryList()
  // 自动加载最新的总结记录
  if (historyList.value.length > 0) {
    loadHistoryDetail(historyList.value[0].id)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  categoryChart?.dispose()
  focalChart?.dispose()
  isoChart?.dispose()
  cameraChart?.dispose()
})
</script>

<style lang="scss" scoped>
.summary-page {
  max-width: 1400px;
  margin: 0 auto;
}

.date-selector {
  margin-top: 12px;
}

.stats-row {
  margin-bottom: 20px;
}

.chart-card {
  margin-bottom: 20px;
  
  h3 {
    margin-bottom: 16px;
    color: #303133;
    font-size: 16px;
  }
}

.chart-container {
  height: 300px;
}

.ai-summary-content {
  background: #f9fafc;
  border-radius: 8px;
  padding: 20px;
  line-height: 1.8;
  font-size: 15px;
  color: #303133;
  
  :deep(br) {
    margin-bottom: 8px;
  }
}

.loading-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 8px;
}

.empty-state {
  .sub {
    font-size: 12px;
    color: #c0c4cc;
    margin-top: 8px;
  }
  
  .quick-tips {
    margin-top: 24px;
    padding: 16px 24px;
    background: #f5f7fa;
    border-radius: 8px;
    text-align: left;
    
    h4 {
      font-size: 14px;
      color: #606266;
      margin-bottom: 12px;
    }
    
    ul {
      padding-left: 20px;
      margin: 0;
      
      li {
        font-size: 13px;
        color: #909399;
        line-height: 2;
      }
    }
  }
}

// 历史记录
.history-card {
  max-height: 400px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  
  h3 {
    flex-shrink: 0;
  }
}

.history-list {
  flex: 1;
  overflow-y: auto;
  margin-top: 12px;
}

.history-item {
  position: relative;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  
  &:hover {
    background: #f5f7fa;
    
    .delete-btn {
      opacity: 1;
    }
  }
  
  &.active {
    background: #ecf5ff;
    
    .title {
      color: #409EFF;
    }
  }
  
  .title {
    font-size: 13px;
    color: #303133;
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 24px;
  }
  
  .meta {
    font-size: 11px;
    color: #909399;
  }
  
  .delete-btn {
    position: absolute;
    top: 10px;
    right: 8px;
    color: #f56c6c;
    opacity: 0;
    transition: opacity 0.2s;
    cursor: pointer;
    
    &:hover {
      color: #f56c6c;
    }
  }
}

.loading-small {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.empty-small {
  text-align: center;
  padding: 20px;
  color: #c0c4cc;
  font-size: 13px;
}

h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
}
</style>
