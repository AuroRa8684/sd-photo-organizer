<template>
  <div class="import-page">
    <div class="page-header">
      <h1>📸 导入照片</h1>
      <p>从SD卡或其他目录导入照片到本地图库</p>
      <!-- 新手引导提示 -->
      <el-alert
        v-if="stats.total_photos === 0"
        title="👋 欢迎使用！开始你的第一次照片导入"
        type="info"
        :closable="true"
        show-icon
        style="margin-top: 16px"
      >
        <template #default>
          <ol style="margin: 8px 0 0; padding-left: 20px; line-height: 2">
            <li>输入或选择SD卡/照片目录路径</li>
            <li>点击"扫描照片"读取并生成缩略图</li>
            <li>设置本地图库目录，点击"整理到图库"完成导入</li>
          </ol>
        </template>
      </el-alert>
    </div>

    <!-- 快速统计 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="content-card stat-card">
          <div class="stat-value">{{ stats.total_photos || 0 }}</div>
          <div class="stat-label">总照片数</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="content-card stat-card">
          <div class="stat-value">{{ stats.with_raw || 0 }}</div>
          <div class="stat-label">含RAW照片</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="content-card stat-card">
          <div class="stat-value">{{ stats.selected || 0 }}</div>
          <div class="stat-label">精选照片</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="content-card stat-card">
          <div class="stat-value">{{ stats.categories_count || 0 }}</div>
          <div class="stat-label">类别数量</div>
        </div>
      </el-col>
    </el-row>

    <!-- 导入设置 -->
    <div class="content-card">
      <h3>📁 选择目录</h3>
      
      <el-form :model="form" label-width="120px" class="import-form">
        <el-form-item label="SD卡目录">
          <el-input
            v-model="form.sdPath"
            placeholder="输入SD卡或照片目录路径，例如: D:\DCIM\100MSDCF"
            clearable
          >
            <template #append>
              <el-button @click="showSdPathPicker = true">
                <el-icon><FolderOpened /></el-icon>
              </el-button>
              <el-button @click="previewPath" :loading="previewing">
                预览
              </el-button>
            </template>
          </el-input>
          <div class="form-tip" v-if="preview">
            发现 {{ preview.jpg_count }} 张JPG照片，约 {{ preview.estimated_raw_count }} 张有配对的RAW
          </div>
        </el-form-item>

        <el-form-item label="本地图库目录">
          <el-input
            v-model="form.libraryRoot"
            placeholder="输入本地图库根目录，例如: D:\PhotoLibrary"
            clearable
          >
            <template #append>
              <el-button @click="showLibraryPicker = true">
                <el-icon><FolderOpened /></el-icon>
              </el-button>
            </template>
          </el-input>
          <div class="form-tip">
            照片将按 <code>图库目录/YYYY-MM-DD/类别/</code> 规则整理
          </div>
        </el-form-item>
      </el-form>
    </div>

    <!-- 文件夹选择器 -->
    <FolderPicker
      v-model="showSdPathPicker"
      title="选择SD卡目录"
      :initial-path="form.sdPath"
      @select="(path) => form.sdPath = path"
    />
    <FolderPicker
      v-model="showLibraryPicker"
      title="选择本地图库目录"
      :initial-path="form.libraryRoot"
      @select="(path) => form.libraryRoot = path"
    />

    <!-- 操作按钮 -->
    <div class="content-card">
      <h3>🚀 开始导入</h3>
      
      <div class="action-buttons">
        <el-button
          type="primary"
          size="large"
          @click="handleScan"
          :loading="scanning"
          :disabled="!form.sdPath"
        >
          <el-icon><Search /></el-icon>
          {{ scanning ? '扫描中...' : '扫描照片' }}
        </el-button>
        
        <el-button
          type="success"
          size="large"
          @click="handleImport"
          :loading="importing"
          :disabled="!form.libraryRoot || !scanResult"
        >
          <el-icon><FolderOpened /></el-icon>
          {{ importing ? '整理中...' : '整理到图库' }}
        </el-button>
      </div>
      
      <!-- 扫描进度提示 -->
      <div v-if="scanning" class="progress-hint">
        <el-progress :percentage="scanProgress" :stroke-width="8" :show-text="false" />
        <p>正在扫描照片并生成缩略图，请耐心等待...</p>
        <p class="hint-small">大量照片可能需要几分钟</p>
      </div>
      
      <!-- 整理进度提示 -->
      <div v-if="importing" class="progress-hint">
        <el-progress :percentage="importProgress" :stroke-width="8" status="success" :show-text="false" />
        <p>正在整理照片到本地图库...</p>
      </div>
    </div>

    <!-- 扫描结果 -->
    <div class="content-card" v-if="scanResult">
      <h3>📊 扫描结果</h3>
      
      <el-descriptions :column="4" border>
        <el-descriptions-item label="发现照片">
          {{ scanResult.total_found }}
        </el-descriptions-item>
        <el-descriptions-item label="新导入">
          <el-tag type="success">{{ scanResult.new_imported }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="重复跳过">
          <el-tag type="info">{{ scanResult.duplicates }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="含RAW">
          <el-tag type="warning">{{ scanResult.with_raw }}</el-tag>
        </el-descriptions-item>
      </el-descriptions>

      <div class="scan-message" v-if="scanResult.message">
        <el-alert :title="scanResult.message" type="success" show-icon />
      </div>

      <!-- 错误列表 -->
      <div class="error-list" v-if="scanResult.errors?.length">
        <el-collapse>
          <el-collapse-item :title="`处理错误 (${scanResult.errors.length})`">
            <div v-for="(err, index) in scanResult.errors" :key="index" class="error-item">
              <strong>{{ err.file }}</strong>: {{ err.error }}
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>

    <!-- 整理结果 -->
    <div class="content-card" v-if="importResult">
      <h3>✅ 整理结果</h3>
      
      <el-descriptions :column="4" border>
        <el-descriptions-item label="待整理">
          {{ importResult.total }}
        </el-descriptions-item>
        <el-descriptions-item label="成功">
          <el-tag type="success">{{ importResult.success }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="失败">
          <el-tag type="danger" v-if="importResult.failed">{{ importResult.failed }}</el-tag>
          <span v-else>0</span>
        </el-descriptions-item>
        <el-descriptions-item label="复制RAW">
          {{ importResult.raw_copied }}
        </el-descriptions-item>
      </el-descriptions>

      <div class="scan-message" v-if="importResult.message">
        <el-alert :title="importResult.message" type="success" show-icon />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, FolderOpened } from '@element-plus/icons-vue'
import { scanDirectory, previewDirectory, importToLibrary, getQuickStats } from '@/api'
import FolderPicker from '@/components/FolderPicker.vue'

// 表单数据
const form = reactive({
  sdPath: '',
  libraryRoot: ''
})

// 文件夹选择器
const showSdPathPicker = ref(false)
const showLibraryPicker = ref(false)

// 状态
const stats = ref({})
const preview = ref(null)
const scanResult = ref(null)
const importResult = ref(null)
const previewing = ref(false)
const scanning = ref(false)
const importing = ref(false)

// 进度模拟
const scanProgress = ref(0)
const importProgress = ref(0)
let progressTimer = null

const startProgressSimulation = (type) => {
  const progressRef = type === 'scan' ? scanProgress : importProgress
  progressRef.value = 0
  clearInterval(progressTimer)
  progressTimer = setInterval(() => {
    if (progressRef.value < 90) {
      progressRef.value += Math.random() * 15
    }
  }, 500)
}

const stopProgressSimulation = (type) => {
  const progressRef = type === 'scan' ? scanProgress : importProgress
  clearInterval(progressTimer)
  progressRef.value = 100
}

// 获取统计数据
const loadStats = async () => {
  try {
    const res = await getQuickStats()
    stats.value = res.data || {}
  } catch (error) {
    console.error('获取统计失败:', error)
  }
}

// 预览目录
const previewPath = async () => {
  if (!form.sdPath) {
    ElMessage.warning('请输入目录路径')
    return
  }
  
  previewing.value = true
  try {
    const res = await previewDirectory(form.sdPath)
    preview.value = res.data
    
    if (!res.data.valid) {
      ElMessage.error(res.data.message || '目录无效')
    }
  } catch (error) {
    ElMessage.error('预览失败: ' + error.message)
  } finally {
    previewing.value = false
  }
}

// 扫描照片
const handleScan = async () => {
  if (!form.sdPath) {
    ElMessage.warning('请输入SD卡目录路径')
    return
  }
  
  scanning.value = true
  scanResult.value = null
  startProgressSimulation('scan')
  
  try {
    const res = await scanDirectory(form.sdPath)
    scanResult.value = res.data
    ElMessage.success(res.message || '扫描完成')
    loadStats()
  } catch (error) {
    ElMessage.error('扫描失败，请检查目录路径是否正确')
  } finally {
    stopProgressSimulation('scan')
    scanning.value = false
  }
}

// 整理到图库
const handleImport = async () => {
  if (!form.libraryRoot) {
    ElMessage.warning('请输入本地图库目录')
    return
  }
  
  importing.value = true
  importResult.value = null
  startProgressSimulation('import')
  
  try {
    const res = await importToLibrary({
      library_root: form.libraryRoot
    })
    importResult.value = res.data
    ElMessage.success(res.message || '整理完成')
    loadStats()
  } catch (error) {
    ElMessage.error('整理失败，请检查目录权限')
  } finally {
    stopProgressSimulation('import')
    importing.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style lang="scss" scoped>
.import-page {
  max-width: 1200px;
  margin: 0 auto;
}

.stats-row {
  margin-bottom: 20px;
}

.import-form {
  margin-top: 20px;
  
  .form-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;
    
    code {
      background: #f5f7fa;
      padding: 2px 6px;
      border-radius: 4px;
    }
  }
}

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.scan-message {
  margin-top: 16px;
}

.error-list {
  margin-top: 16px;
  
  .error-item {
    font-size: 12px;
    color: #f56c6c;
    padding: 4px 0;
    border-bottom: 1px solid #eee;
  }
}

h3 {
  margin-bottom: 16px;
  color: #303133;
  font-size: 16px;
}

.progress-hint {
  margin-top: 20px;
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  
  p {
    margin-top: 12px;
    color: #606266;
    font-size: 14px;
    text-align: center;
  }
  
  .hint-small {
    font-size: 12px;
    color: #909399;
    margin-top: 4px;
  }
}
</style>
