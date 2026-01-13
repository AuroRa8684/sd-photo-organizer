<template>
  <div class="gallery-page">
    <div class="page-header">
      <h1>🖼️ 照片墙</h1>
      <p>浏览、筛选和管理你的照片</p>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-item">
        <label>类别：</label>
        <el-select v-model="filters.category" placeholder="全部" clearable style="width: 120px">
          <el-option label="全部" value="" />
          <el-option v-for="cat in categories" :key="cat" :label="cat" :value="cat" />
        </el-select>
      </div>
      
      <div class="filter-item">
        <label>日期范围：</label>
        <el-date-picker
          v-model="filters.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          style="width: 260px"
        />
      </div>
      
      <div class="filter-item">
        <label>精选：</label>
        <el-select v-model="filters.isSelected" placeholder="全部" clearable style="width: 100px">
          <el-option label="全部" :value="null" />
          <el-option label="是" :value="true" />
          <el-option label="否" :value="false" />
        </el-select>
      </div>
      
      <div class="filter-item">
        <el-button type="primary" @click="loadPhotos">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetFilters">重置</el-button>
      </div>
      
      <div class="filter-item" style="margin-left: auto;">
        <el-button type="warning" @click="handleAIClassify" :loading="classifying" :disabled="selectedIds.length === 0">
          <el-icon><MagicStick /></el-icon>
          AI分类 ({{ selectedIds.length }})
        </el-button>
        <el-button type="success" @click="showExportDialog = true" :disabled="selectedCount === 0">
          <el-icon><Download /></el-icon>
          导出精选 ({{ selectedCount }})
        </el-button>
      </div>
    </div>

    <!-- 照片网格 -->
    <div class="content-card">
      <div class="photo-grid-header">
        <span>共 {{ total }} 张照片</span>
        <el-checkbox v-model="selectAll" @change="handleSelectAll">全选当前页</el-checkbox>
      </div>
      
      <div v-if="loading" class="loading-overlay">
        <el-icon class="is-loading" :size="48"><Loading /></el-icon>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="photos.length === 0" class="empty-state">
        <el-icon><Picture /></el-icon>
        <p>暂无照片，请先导入</p>
      </div>
      
      <div v-else class="photo-grid">
        <div
          v-for="photo in photos"
          :key="photo.id"
          class="photo-card"
          :class="{ selected: isPhotoSelected(photo.id) }"
          @click="togglePhotoSelect(photo)"
        >
          <img
            :src="getThumbUrl(photo.thumb_url)"
            :alt="photo.file_name"
            class="photo-thumb"
            loading="lazy"
          />
          <div class="photo-category" v-if="photo.category !== '未分类'">
            {{ photo.category }}
          </div>
          <div class="photo-select" @click.stop>
            <el-checkbox
              :model-value="photo.is_selected"
              @change="(val) => handleToggleSelected(photo, val)"
            />
          </div>
          <div class="photo-info">
            <div class="photo-name">{{ photo.file_name }}</div>
            <div class="photo-meta">
              {{ formatDate(photo.taken_at) }}
              <span v-if="photo.focal_length">| {{ photo.focal_length }}mm</span>
              <span v-if="photo.iso">| ISO{{ photo.iso }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="total > 0">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @update:current-page="handlePageChange"
          @update:page-size="handleSizeChange"
        />
      </div>
    </div>

    <!-- 导出对话框 -->
    <el-dialog v-model="showExportDialog" title="导出精选照片" width="500px">
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="导出目录">
          <el-input v-model="exportForm.exportDir" placeholder="例如: D:\Export" />
        </el-form-item>
        <el-form-item label="包含RAW">
          <el-switch v-model="exportForm.includeRaw" />
        </el-form-item>
        <el-form-item label="打包为ZIP">
          <el-switch v-model="exportForm.asZip" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="handleExport" :loading="exporting">
          开始导出
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, MagicStick, Download, Loading, Picture } from '@element-plus/icons-vue'
import { getPhotos, updatePhoto, getCategories, classifyPhotos, exportSelected } from '@/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// 数据
const photos = ref([])
const categories = ref(['人像', '风光', '街拍', '建筑', '美食', '夜景', '动物', '活动', '微距', '未分类'])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const loading = ref(false)
const classifying = ref(false)
const exporting = ref(false)
const showExportDialog = ref(false)
const selectAll = ref(false)
const selectedIds = ref([])

// 筛选条件
const filters = reactive({
  category: '',
  dateRange: null,
  isSelected: null
})

// 导出表单
const exportForm = reactive({
  exportDir: '',
  includeRaw: true,
  asZip: false
})

// 计算精选数量
const selectedCount = computed(() => {
  return photos.value.filter(p => p.is_selected).length
})

// 获取缩略图URL
const getThumbUrl = (thumbUrl) => {
  if (!thumbUrl) return ''
  return API_BASE + thumbUrl
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

// 加载类别
const loadCategories = async () => {
  try {
    const res = await getCategories()
    if (res.data) {
      categories.value = res.data
    }
  } catch (error) {
    console.error('获取类别失败:', error)
  }
}

// 加载照片列表
const loadPhotos = async () => {
  loading.value = true
  
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (filters.category) {
      params.category = filters.category
    }
    
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.date_from = filters.dateRange[0].toISOString()
      params.date_to = filters.dateRange[1].toISOString()
    }
    
    if (filters.isSelected !== null) {
      params.is_selected = filters.isSelected
    }
    
    const res = await getPhotos(params)
    photos.value = res.data.photos || []
    total.value = res.data.total || 0
    
  } catch (error) {
    ElMessage.error('加载照片失败')
  } finally {
    loading.value = false
  }
}

// 重置筛选
const resetFilters = () => {
  filters.category = ''
  filters.dateRange = null
  filters.isSelected = null
  currentPage.value = 1
  loadPhotos()
}

// 分页处理
const handlePageChange = (page) => {
  currentPage.value = page
  loadPhotos()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadPhotos()
}

// 切换照片选中状态（用于AI分类）
const isPhotoSelected = (id) => selectedIds.value.includes(id)

const togglePhotoSelect = (photo) => {
  const index = selectedIds.value.indexOf(photo.id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(photo.id)
  }
}

// 全选当前页
const handleSelectAll = (checked) => {
  if (checked) {
    selectedIds.value = photos.value.map(p => p.id)
  } else {
    selectedIds.value = []
  }
}

// 切换精选标记
const handleToggleSelected = async (photo, value) => {
  try {
    await updatePhoto(photo.id, { is_selected: value })
    photo.is_selected = value
    ElMessage.success(value ? '已添加到精选' : '已取消精选')
  } catch (error) {
    ElMessage.error('更新失败')
  }
}

// AI分类
const handleAIClassify = async () => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要分类的照片')
    return
  }
  
  classifying.value = true
  
  try {
    const res = await classifyPhotos(selectedIds.value)
    ElMessage.success(res.data.message || 'AI分类完成')
    loadPhotos() // 刷新列表
    selectedIds.value = []
    selectAll.value = false
  } catch (error) {
    ElMessage.error('AI分类失败: ' + error.message)
  } finally {
    classifying.value = false
  }
}

// 导出精选
const handleExport = async () => {
  if (!exportForm.exportDir) {
    ElMessage.warning('请输入导出目录')
    return
  }
  
  exporting.value = true
  
  try {
    const res = await exportSelected({
      export_dir: exportForm.exportDir,
      include_raw: exportForm.includeRaw,
      as_zip: exportForm.asZip
    })
    ElMessage.success(res.data.message || '导出完成')
    showExportDialog.value = false
  } catch (error) {
    ElMessage.error('导出失败: ' + error.message)
  } finally {
    exporting.value = false
  }
}

onMounted(() => {
  loadCategories()
  loadPhotos()
})
</script>

<style lang="scss" scoped>
.gallery-page {
  max-width: 1400px;
  margin: 0 auto;
}

.photo-grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.photo-card {
  &.selected {
    outline: 3px solid #409EFF;
  }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>
