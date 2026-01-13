<template>
  <div class="summary-page">
    <div class="page-header">
      <h1>📊 拍摄总结</h1>
      <p>查看统计数据和AI生成的拍摄复盘</p>
    </div>

    <!-- 日期范围选择 -->
    <div class="content-card">
      <h3>📅 选择日期范围</h3>
      <div class="date-selector">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 300px"
        />
        <el-button type="primary" @click="handleGenerate" :loading="loading">
          <el-icon><DataAnalysis /></el-icon>
          生成总结
        </el-button>
        <el-button @click="handleGenerateAll" :loading="loading">
          全部数据
        </el-button>
      </div>
    </div>

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
        <p>点击"生成总结"按钮查看统计数据和AI复盘</p>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="content-card" v-if="loading">
      <div class="loading-overlay">
        <el-icon class="is-loading" :size="48"><Loading /></el-icon>
        <p>正在生成总结，请稍候...</p>
        <p class="loading-tip" v-if="loading">AI分析可能需要10-30秒</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { DataAnalysis, Loading } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { generateSummary } from '@/api'

// 数据
const dateRange = ref(null)
const summary = ref(null)
const loading = ref(false)

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

// 生成总结
const handleGenerate = async () => {
  loading.value = true
  summary.value = null
  
  try {
    const params = {}
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

onMounted(() => {
  window.addEventListener('resize', handleResize)
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
  display: flex;
  gap: 16px;
  align-items: center;
  margin-top: 16px;
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

h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
}
</style>
