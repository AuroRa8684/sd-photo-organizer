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
        <el-button @click="resetFilters">重置筛选</el-button>
      </div>
      
      <div class="filter-item" style="margin-left: auto;">
        <el-dropdown @command="handleBatchAction" :disabled="selectedIds.length === 0">
          <el-button :disabled="selectedIds.length === 0">
            批量操作 ({{ selectedIds.length }}) <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="classifySkip">
                <el-icon><MagicStick /></el-icon> AI智能分类
              </el-dropdown-item>
              <el-dropdown-item divided command="select">设为精选</el-dropdown-item>
              <el-dropdown-item command="unselect">取消精选</el-dropdown-item>
              <el-dropdown-item divided command="delete" style="color: #f56c6c">
                删除照片
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="success" @click="showExportDialog = true" :disabled="selectedCount === 0">
          <el-icon><Download /></el-icon>
          导出精选 ({{ selectedCount }})
        </el-button>
      </div>
    </div>

    <!-- 照片网格 -->
    <div class="content-card">
      <div class="photo-grid-header">
        <span>共 {{ total }} 张照片 | 已选 {{ selectedIds.length }} 张</span>
        <el-checkbox v-model="selectAll" @change="handleSelectAll">全选当前页</el-checkbox>
      </div>
      
      <div v-if="loading" class="skeleton-grid">
        <div v-for="i in 12" :key="i" class="skeleton-card">
          <div class="skeleton-image"></div>
          <div class="skeleton-text">
            <div class="skeleton-line"></div>
            <div class="skeleton-line"></div>
          </div>
        </div>
      </div>
      
      <div v-else-if="photos.length === 0" class="empty-state">
        <el-icon><Picture /></el-icon>
        <p>暂无照片</p>
        <p class="empty-sub">点击左侧"导入照片"开始扫描SD卡或照片目录</p>
        <el-button type="primary" @click="$router.push('/')" style="margin-top: 16px">
          去导入照片
        </el-button>
      </div>
      
      <div v-else class="photo-grid">
        <div
          v-for="photo in photos"
          :key="photo.id"
          class="photo-card"
          :class="{ 
            checked: isPhotoChecked(photo.id),
            starred: photo.is_selected 
          }"
        >
          <img
            :src="getThumbUrl(photo.thumb_url)"
            :alt="photo.file_name"
            class="photo-thumb"
            loading="lazy"
            @click="openPreview(photo)"
          />
          <div class="photo-category" v-if="photo.category !== '未分类'">
            {{ photo.category }}
          </div>
          <!-- 勾选框(用于批量操作) -->
          <div class="photo-check" @click.stop="togglePhotoCheck(photo)">
            <el-checkbox :model-value="isPhotoChecked(photo.id)" class="no-pointer" />
          </div>
          <!-- 精选标记 -->
          <div 
            class="photo-star" 
            :class="{ active: photo.is_selected }"
            @click.stop="handleToggleSelected(photo, !photo.is_selected)"
          >
            <el-icon><Star /></el-icon>
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

    <!-- 图片预览 -->
    <PhotoPreview
      v-model="showPreview"
      :photo="previewPhoto"
      :current-index="previewIndex"
      :total-count="photos.length"
      :has-prev="previewIndex > 0"
      :has-next="previewIndex < photos.length - 1"
      @prev="previewPrev"
      @next="previewNext"
      @updated="handlePhotoUpdated"
    />

    <!-- 导出对话框 -->
    <el-dialog v-model="showExportDialog" title="导出精选照片" width="500px">
      <el-form :model="exportForm" label-width="120px">
        <el-form-item label="导出目录">
          <el-input v-model="exportForm.exportDir" placeholder="例如: D:\Export">
            <template #append>
              <el-button @click="showExportPicker = true">
                <el-icon><FolderOpened /></el-icon>
              </el-button>
            </template>
          </el-input>
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

    <!-- 导出目录选择器 -->
    <FolderPicker
      v-model="showExportPicker"
      title="选择导出目录"
      :initial-path="exportForm.exportDir"
      @select="(path) => exportForm.exportDir = path"
    />

    <!-- AI分类进度 -->
    <el-dialog v-model="showClassifyProgress" title="AI分类中" width="450px" :close-on-click-modal="false">
      <div class="classify-progress">
        <el-icon class="is-loading" :size="48"><Loading /></el-icon>
        <p>正在对 {{ classifyTotal }} 张照片进行AI分类...</p>
        <p class="tip">每张照片约需 2-5 秒，请耐心等待</p>
        <p class="tip">预计耗时：约 {{ Math.ceil(classifyTotal * 3 / 60) }} 分钟</p>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, Loading, Picture, Star, ArrowDown, FolderOpened, MagicStick } from '@element-plus/icons-vue'
import { getPhotos, updatePhoto, getCategories, classifyPhotos, exportSelected, batchDeletePhotos, batchUpdatePhotos } from '@/api'
import PhotoPreview from '@/components/PhotoPreview.vue'
import FolderPicker from '@/components/FolderPicker.vue'

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
const showExportPicker = ref(false)
const selectAll = ref(false)
const selectedIds = ref([])  // 勾选的照片ID(用于批量操作)

// 预览相关
const showPreview = ref(false)
const previewPhoto = ref(null)
const previewIndex = ref(0)

// AI分类进度
const showClassifyProgress = ref(false)
const classifyTotal = ref(0)

// 筛选条件
const filters = reactive({
  category: '',
  dateRange: null,
  isSelected: null
})

// 监听筛选条件变化，自动搜索（防抖）
let filterDebounce = null
watch(filters, () => {
  clearTimeout(filterDebounce)
  filterDebounce = setTimeout(() => {
    currentPage.value = 1
    loadPhotos()
  }, 300)
}, { deep: true })

// 常量：localStorage键名
const STORAGE_KEY_EXPORT = 'sd_organizer_export_dir'

// 导出表单
const exportForm = reactive({
  exportDir: localStorage.getItem(STORAGE_KEY_EXPORT) || '',
  includeRaw: true,
  asZip: false
})

// 监听导出目录变化，自动保存
watch(() => exportForm.exportDir, (val) => {
  if (val) localStorage.setItem(STORAGE_KEY_EXPORT, val)
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
    
    // 清空勾选
    selectedIds.value = []
    selectAll.value = false
    
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

// 勾选状态检查（用于批量操作）
const isPhotoChecked = (id) => selectedIds.value.includes(id)

const togglePhotoCheck = (photo) => {
  const index = selectedIds.value.indexOf(photo.id)
  if (index > -1) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(photo.id)
  }
  // 更新全选状态
  selectAll.value = selectedIds.value.length === photos.value.length
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

// 批量操作处理
const handleBatchAction = async (command) => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择照片')
    return
  }

  switch (command) {
    case 'classify':
      await handleAIClassify(false)
      break
    case 'classifySkip':
      await handleAIClassify(true)
      break
    case 'select':
      await handleBatchSelect(true)
      break
    case 'unselect':
      await handleBatchSelect(false)
      break
    case 'delete':
      await handleBatchDelete()
      break
  }
}

// AI分类
const handleAIClassify = async (skipClassified = false) => {
  if (selectedIds.value.length === 0) {
    ElMessage.warning('请先选择要分类的照片')
    return
  }
  
  classifyTotal.value = selectedIds.value.length
  showClassifyProgress.value = true
  classifying.value = true
  
  try {
    const res = await classifyPhotos(selectedIds.value, 4, skipClassified)
    ElMessage.success(res.data.message || 'AI分类完成')
    loadPhotos()
    selectedIds.value = []
    selectAll.value = false
  } catch (error) {
    ElMessage.error('AI分类失败: ' + error.message)
  } finally {
    classifying.value = false
    showClassifyProgress.value = false
  }
}

// 批量设置精选
const handleBatchSelect = async (isSelected) => {
  try {
    await batchUpdatePhotos(selectedIds.value, { is_selected: isSelected })
    ElMessage.success(isSelected ? '已批量加入精选' : '已批量取消精选')
    loadPhotos()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 批量删除
const handleBatchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要从照片墙移除这 ${selectedIds.value.length} 张照片吗？此操作不会删除原始文件。`,
      '确认移除',
      { type: 'warning' }
    )
    
    await batchDeletePhotos(selectedIds.value)
    ElMessage.success('已从照片墙移除')
    loadPhotos()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

// 预览相关
const openPreview = (photo) => {
  previewPhoto.value = photo
  previewIndex.value = photos.value.findIndex(p => p.id === photo.id)
  showPreview.value = true
}

const previewPrev = () => {
  if (previewIndex.value > 0) {
    previewIndex.value--
    previewPhoto.value = photos.value[previewIndex.value]
  }
}

const previewNext = () => {
  if (previewIndex.value < photos.value.length - 1) {
    previewIndex.value++
    previewPhoto.value = photos.value[previewIndex.value]
  }
}

const handlePhotoUpdated = (updatedPhoto) => {
  const index = photos.value.findIndex(p => p.id === updatedPhoto.id)
  if (index > -1) {
    photos.value[index] = updatedPhoto
  }
  previewPhoto.value = updatedPhoto
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
  position: relative;
  
  &.checked {
    outline: 3px solid #409EFF;
  }
  
  &.starred {
    &::after {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      border: 3px solid #E6A23C;
      border-radius: 8px;
      pointer-events: none;
    }
  }
  
  .photo-check {
    position: absolute;
    top: 8px;
    left: 8px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 4px;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    
    .no-pointer {
      pointer-events: none; // checkbox不拦截点击，由父div处理
    }
  }
  
  .photo-star {
    position: absolute;
    top: 8px;
    right: 8px;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 50%;
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #c0c4cc;
    transition: color 0.2s;
    
    &:hover {
      color: #E6A23C;
    }
    
    &.active {
      color: #E6A23C;
      background: #fdf6ec;
    }
  }
  
  .photo-thumb {
    cursor: pointer;
  }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.classify-progress {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30px;
  
  p {
    margin-top: 16px;
    color: #303133;
  }
  
  .tip {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;
  }
}

.empty-sub {
  font-size: 13px;
  color: #c0c4cc;
  margin-top: 8px;
}
</style>
