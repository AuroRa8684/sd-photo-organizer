<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="600px"
    :close-on-click-modal="false"
  >
    <!-- 当前路径导航 -->
    <div class="path-nav">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item @click="goToRoot">
          <el-icon><HomeFilled /></el-icon>
        </el-breadcrumb-item>
        <el-breadcrumb-item
          v-for="(part, index) in pathParts"
          :key="index"
          @click="goToPath(index)"
        >
          {{ part }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </div>

      <!-- 目录列表 -->
      <div class="folder-list" v-loading="loading" element-loading-text="加载目录中...">
        <!-- 返回上级 -->
        <div
          v-if="currentData?.parent"
          class="folder-item parent"
          @click="navigateTo(currentData.parent)"
          @dblclick="navigateTo(currentData.parent)"
        >
          <el-icon><Back /></el-icon>
          <span>.. 返回上级目录</span>
        </div>

      <!-- 驱动器列表 -->
      <div
        v-for="drive in drives"
        :key="drive.path"
        class="folder-item drive"
        :class="{ selected: selectedPath === drive.path }"
        @click="selectedPath = drive.path"
        @dblclick="navigateTo(drive.path)"
      >
        <el-icon><Monitor /></el-icon>
        <span class="name">{{ drive.name }}</span>
        <span class="size" v-if="drive.free">
          {{ formatSize(drive.free) }} 可用
        </span>
      </div>

      <!-- 目录列表 -->
      <div
        v-for="item in currentData?.items || []"
        :key="item.path"
        class="folder-item"
        :class="{ 
          selected: selectedPath === item.path,
          disabled: !item.accessible 
        }"
        @click="item.accessible && (selectedPath = item.path)"
        @dblclick="item.accessible && navigateTo(item.path)"
      >
        <el-icon><Folder /></el-icon>
        <span class="name">{{ item.name }}</span>
        <span class="hint" v-if="!item.accessible">无权限</span>
      </div>

      <!-- 空状态 -->
      <div v-if="!loading && !drives.length && !currentData?.items?.length" class="empty">
        <el-icon><FolderOpened /></el-icon>
        <p>没有可用目录</p>
      </div>
    </div>

    <!-- 选中路径显示 -->
    <div class="selected-display">
      <el-input v-model="selectedPath" placeholder="选中的路径" readonly>
        <template #prepend>已选择</template>
        <template #append>
          <el-button @click="refreshCurrent" :loading="loading">
            刷新
          </el-button>
        </template>
      </el-input>
      <div class="path-hint">单击选择，双击进入目录</div>
    </div>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="confirmSelect" :disabled="!selectedPath">
        确认选择
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { HomeFilled, Back, Monitor, Folder, FolderOpened } from '@element-plus/icons-vue'
import { browseDirectory, getSystemDrives } from '@/api'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: '选择文件夹'
  },
  initialPath: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'select'])

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const loading = ref(false)
const drives = ref([])
const currentData = ref(null)
const selectedPath = ref('')
const currentPath = ref('')

// 计算路径部分
const pathParts = computed(() => {
  if (!currentPath.value) return []
  // Windows路径处理
  const parts = currentPath.value.split(/[/\\]/).filter(Boolean)
  return parts
})

// 格式化大小
const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 初始化
watch(visible, async (val) => {
  if (val) {
    selectedPath.value = props.initialPath || ''
    if (props.initialPath) {
      await navigateTo(props.initialPath)
    } else {
      await loadDrives()
    }
  }
})

// 加载驱动器
const loadDrives = async () => {
  loading.value = true
  drives.value = []
  currentData.value = null
  currentPath.value = ''
  
  try {
    const res = await getSystemDrives()
    drives.value = res.data || []
  } catch (e) {
    console.error('加载驱动器失败:', e)
  } finally {
    loading.value = false
  }
}

// 导航到目录
const navigateTo = async (path) => {
  loading.value = true
  drives.value = []
  
  try {
    const res = await browseDirectory(path)
    if (res.error) {
      ElMessage.error(res.error)
      return
    }
    currentData.value = res.data
    currentPath.value = res.data?.current || ''
    selectedPath.value = currentPath.value
  } catch (e) {
    console.error('浏览目录失败:', e)
  } finally {
    loading.value = false
  }
}

// 返回根目录
const goToRoot = () => {
  loadDrives()
}

// 导航到指定路径层级
const goToPath = (index) => {
  const parts = currentPath.value.split(/[/\\]/).filter(Boolean)
  const newPath = parts.slice(0, index + 1).join('\\')
  // Windows盘符需要加反斜杠
  const fullPath = newPath.includes(':') ? newPath + '\\' : newPath
  navigateTo(fullPath)
}

// 确认选择
const confirmSelect = () => {
  emit('select', selectedPath.value)
  visible.value = false
}

// 刷新当前目录
const refreshCurrent = () => {
  if (currentPath.value) {
    navigateTo(currentPath.value)
  } else {
    loadDrives()
  }
}
</script>

<style lang="scss" scoped>
.path-nav {
  margin-bottom: 16px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  
  :deep(.el-breadcrumb__item) {
    cursor: pointer;
    
    &:hover {
      color: #409EFF;
    }
  }
}

.folder-list {
  height: 300px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  
  .folder-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.2s;
    
    &:hover {
      background: #f5f7fa;
    }
    
    &.selected {
      background: #ecf5ff;
      color: #409EFF;
    }
    
    &.disabled {
      color: #c0c4cc;
      cursor: not-allowed;
    }
    
    &.parent {
      color: #909399;
      font-style: italic;
    }
    
    &.drive {
      .el-icon {
        color: #409EFF;
      }
    }
    
    .name {
      flex: 1;
    }
    
    .size, .hint {
      font-size: 12px;
      color: #909399;
    }
  }
  
  .empty {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: #909399;
    
    .el-icon {
      font-size: 48px;
      margin-bottom: 12px;
    }
  }
}

.selected-display {
  margin-top: 16px;
  
  .path-hint {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;
    text-align: center;
  }
}
</style>
