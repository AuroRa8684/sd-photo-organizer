<template>
  <el-dialog
    v-model="visible"
    :title="photo?.file_name || '照片预览'"
    width="90%"
    :close-on-click-modal="true"
    class="photo-preview-dialog"
    destroy-on-close
    @keydown.left="hasPrev && $emit('prev')"
    @keydown.right="hasNext && $emit('next')"
  >
    <div class="preview-container">
      <!-- 图片区域 -->
      <div class="preview-image">
        <img
          :src="imageUrl"
          :alt="photo?.file_name"
          @load="imageLoaded = true"
          @error="handleImageError"
          v-show="imageLoaded"
        />
        <div v-if="!imageLoaded && !imageError" class="loading-placeholder">
          <el-icon class="is-loading" :size="48"><Loading /></el-icon>
          <p>加载中...</p>
        </div>
        <div v-if="imageError" class="loading-placeholder">
          <el-icon :size="48"><WarningFilled /></el-icon>
          <p>图片加载失败</p>
        </div>
      </div>

      <!-- 信息侧边栏 -->
      <div class="preview-sidebar">
        <h3>📷 照片信息</h3>
        
        <el-descriptions :column="1" border size="small">
          <el-descriptions-item label="文件名">
            {{ photo?.file_name }}
          </el-descriptions-item>
          <el-descriptions-item label="拍摄时间">
            {{ formatDate(photo?.taken_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="相机">
            {{ photo?.camera_model || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="镜头">
            {{ photo?.lens || '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="焦距">
            {{ photo?.focal_length ? photo.focal_length + 'mm' : '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="光圈">
            {{ photo?.aperture ? 'f/' + photo.aperture : '未知' }}
          </el-descriptions-item>
          <el-descriptions-item label="快门">
            {{ formatShutter(photo?.shutter) }}
          </el-descriptions-item>
          <el-descriptions-item label="ISO">
            {{ photo?.iso || '未知' }}
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 20px;">🏷️ 分类标签</h3>
        
        <div class="category-section">
          <el-tag :type="photo?.category === '未分类' ? 'info' : 'primary'" size="large">
            {{ photo?.category || '未分类' }}
          </el-tag>
        </div>

        <div class="tags-section" v-if="photo?.tags?.length">
          <el-tag
            v-for="tag in photo.tags"
            :key="tag"
            type="success"
            size="small"
            style="margin: 4px"
          >
            {{ tag }}
          </el-tag>
        </div>

        <div class="caption-section" v-if="photo?.caption">
          <p>{{ photo.caption }}</p>
        </div>

        <div class="actions-section">
          <el-button
            :type="photo?.is_selected ? 'warning' : 'success'"
            @click="toggleSelected"
          >
            {{ photo?.is_selected ? '取消精选' : '加入精选' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <template #footer>
      <div class="nav-footer">
        <el-button @click="$emit('prev')" :disabled="!hasPrev">
          <el-icon><ArrowLeft /></el-icon> 上一张 (←)
        </el-button>
        <span class="index-display">{{ currentIndex + 1 }} / {{ totalCount }}</span>
        <el-button @click="$emit('next')" :disabled="!hasNext">
          下一张 (→) <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
      <div class="keyboard-hint">使用方向键 ← → 快速浏览，ESC 关闭</div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Loading, ArrowLeft, ArrowRight, WarningFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { updatePhoto } from '@/api'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const props = defineProps({
  modelValue: Boolean,
  photo: Object,
  currentIndex: {
    type: Number,
    default: 0
  },
  totalCount: {
    type: Number,
    default: 0
  },
  hasPrev: Boolean,
  hasNext: Boolean
})

const emit = defineEmits(['update:modelValue', 'prev', 'next', 'updated'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const imageLoaded = ref(false)
const imageError = ref(false)

// 图片加载失败处理
const handleImageError = () => {
  imageError.value = true
  imageLoaded.value = false
}

// 获取图片URL（使用缩略图，因为原图可能不在服务器上）
const imageUrl = computed(() => {
  if (!props.photo?.thumb_url) return ''
  return API_BASE + props.photo.thumb_url
})

// 监听photo变化重置加载状态
watch(() => props.photo, () => {
  imageLoaded.value = false
  imageError.value = false
})

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 格式化快门速度
const formatShutter = (shutter) => {
  if (!shutter) return '未知'
  if (shutter >= 1) return shutter + 's'
  return '1/' + Math.round(1 / shutter) + 's'
}

// 切换精选状态
const toggleSelected = async () => {
  if (!props.photo) return
  
  try {
    const newValue = !props.photo.is_selected
    await updatePhoto(props.photo.id, { is_selected: newValue })
    emit('updated', { ...props.photo, is_selected: newValue })
    ElMessage.success(newValue ? '已加入精选' : '已取消精选')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

// 键盘导航
const handleKeydown = (e) => {
  if (!visible.value) return
  if (e.key === 'ArrowLeft' && props.hasPrev) emit('prev')
  if (e.key === 'ArrowRight' && props.hasNext) emit('next')
  if (e.key === 'Escape') visible.value = false
}

// 绑定键盘事件
watch(visible, (val) => {
  if (val) {
    window.addEventListener('keydown', handleKeydown)
  } else {
    window.removeEventListener('keydown', handleKeydown)
  }
})
</script>

<style lang="scss" scoped>
.preview-container {
  display: flex;
  gap: 16px;
  height: 85vh;
}

.preview-image {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a1a;
  border-radius: 8px;
  overflow: hidden;
  min-width: 0; // 防止 flex 子元素撑开
  
  img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    width: auto;
    height: auto;
  }
  
  .loading-placeholder {
    color: #fff;
    text-align: center;
    
    p {
      margin-top: 12px;
      font-size: 14px;
    }
  }
}

.preview-sidebar {
  width: 220px;
  flex-shrink: 0;
  overflow-y: auto;
  
  h3 {
    font-size: 14px;
    color: #303133;
    margin-bottom: 12px;
  }
  
  .category-section {
    margin-bottom: 12px;
  }
  
  .tags-section {
    margin-bottom: 12px;
  }
  
  .caption-section {
    background: #f5f7fa;
    padding: 12px;
    border-radius: 4px;
    font-size: 14px;
    color: #606266;
    margin-bottom: 16px;
  }
  
  .actions-section {
    margin-top: 20px;
  }
}

.nav-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  
  .index-display {
    color: #909399;
    font-size: 14px;
  }
}

.keyboard-hint {
  text-align: center;
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 8px;
}

:deep(.photo-preview-dialog) {
  .el-dialog__body {
    padding: 12px 16px;
  }
  .el-dialog__header {
    padding: 12px 16px;
  }
}
</style>
