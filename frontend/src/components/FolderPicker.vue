<template>
  <el-dialog
    v-model="visible"
    :title="title"
    width="720px"
    :close-on-click-modal="false"
    class="folder-picker-dialog"
  >
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="nav-buttons">
        <el-button-group>
          <el-button :disabled="!canGoBack" @click="goBack" size="small">
            <el-icon><ArrowLeft /></el-icon>
          </el-button>
          <el-button :disabled="!currentData?.parent" @click="goUp" size="small">
            <el-icon><Top /></el-icon>
          </el-button>
        </el-button-group>
        <el-button @click="goToRoot" size="small" title="返回驱动器列表">
          <el-icon><HomeFilled /></el-icon>
        </el-button>
        <el-button @click="refreshCurrent" :loading="loading" size="small">
          <el-icon><Refresh /></el-icon>
        </el-button>
      </div>
      
      <!-- 地址栏 -->
      <div class="address-bar">
        <el-input 
          v-model="addressInput" 
          size="small"
          placeholder="输入路径后按回车"
          @keyup.enter="navigateToAddress"
        >
          <template #prefix>
            <el-icon><FolderOpened /></el-icon>
          </template>
        </el-input>
      </div>
    </div>

    <!-- 路径面包屑 -->
    <div class="path-nav">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item @click="goToRoot">
          <el-icon><Monitor /></el-icon> 此电脑
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

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 侧边栏快捷访问 -->
      <div class="sidebar">
        <div class="sidebar-title">快捷访问</div>
        <div 
          v-for="quick in quickAccess" 
          :key="quick.path"
          class="quick-item"
          @click="navigateTo(quick.path)"
        >
          <el-icon><component :is="quick.icon" /></el-icon>
          <span>{{ quick.name }}</span>
        </div>
        
        <div class="sidebar-title" style="margin-top: 16px;">驱动器</div>
        <div 
          v-for="drive in cachedDrives" 
          :key="drive.path"
          class="quick-item drive"
          :class="{ active: currentPath.startsWith(drive.path) }"
          @click="navigateTo(drive.path)"
        >
          <el-icon><Monitor /></el-icon>
          <span>{{ drive.name }}</span>
        </div>
      </div>

      <!-- 目录列表 -->
      <div class="folder-list" v-loading="loading" element-loading-text="加载中...">
        <!-- 返回上级 -->
        <div
          v-if="currentData?.parent"
          class="folder-item parent"
          @dblclick="navigateTo(currentData.parent)"
        >
          <el-icon><Back /></el-icon>
          <span class="name">.. (上级目录)</span>
        </div>

        <!-- 驱动器列表（在根目录时显示） -->
        <div
          v-for="drive in drives"
          :key="drive.path"
          class="folder-item drive"
          :class="{ selected: selectedPath === drive.path }"
          @click="selectItem(drive.path)"
          @dblclick="navigateTo(drive.path)"
        >
          <el-icon class="drive-icon"><Monitor /></el-icon>
          <div class="item-info">
            <div class="name">{{ drive.name }}</div>
            <div class="meta" v-if="drive.total">
              <el-progress 
                :percentage="Math.round((1 - drive.free / drive.total) * 100)" 
                :stroke-width="4"
                :show-text="false"
                style="width: 100px;"
              />
              <span>{{ formatSize(drive.free) }} 可用，共 {{ formatSize(drive.total) }}</span>
            </div>
          </div>
        </div>

        <!-- 文件夹列表 -->
        <div
          v-for="item in currentData?.items || []"
          :key="item.path"
          class="folder-item"
          :class="{ 
            selected: selectedPath === item.path,
            disabled: !item.accessible 
          }"
          @click="item.accessible && selectItem(item.path)"
          @dblclick="item.accessible && navigateTo(item.path)"
        >
          <el-icon class="folder-icon"><Folder /></el-icon>
          <div class="item-info">
            <div class="name">{{ item.name }}</div>
            <div class="meta" v-if="!item.accessible">
              <el-tag size="small" type="danger">无权限访问</el-tag>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="!loading && !drives.length && !currentData?.items?.length" class="empty">
          <el-icon><FolderOpened /></el-icon>
          <p>此文件夹为空</p>
        </div>
      </div>
    </div>

    <!-- 底部选择栏 -->
    <div class="selection-bar">
      <span class="label">已选择:</span>
      <el-input v-model="selectedPath" placeholder="未选择任何文件夹" readonly size="small" />
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="createFolder" size="small">
          <el-icon><FolderAdd /></el-icon> 新建文件夹
        </el-button>
        <div style="flex: 1;"></div>
        <el-button @click="visible = false">取消</el-button>
        <el-button type="primary" @click="confirmSelect" :disabled="!selectedPath">
          选择此文件夹
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  HomeFilled, Back, Monitor, Folder, FolderOpened, 
  ArrowLeft, Top, Refresh, FolderAdd, Document
} from '@element-plus/icons-vue'
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
const cachedDrives = ref([])
const currentData = ref(null)
const selectedPath = ref('')
const currentPath = ref('')
const addressInput = ref('')
const history = ref([])
const historyIndex = ref(-1)

// 快捷访问（使用通用路径，实际会在后端处理）
const quickAccess = [
  { name: '桌面', path: 'C:\\Users\\Public\\Desktop', icon: Document },
  { name: '下载', path: 'C:\\Users\\Public\\Downloads', icon: Document },
  { name: '图片', path: 'C:\\Users\\Public\\Pictures', icon: Document },
]

// 计算路径部分
const pathParts = computed(() => {
  if (!currentPath.value) return []
  const parts = currentPath.value.split(/[/\\]/).filter(Boolean)
  return parts
})

// 是否可以后退
const canGoBack = computed(() => historyIndex.value > 0)

// 格式化大小
const formatSize = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

// 选择项目
const selectItem = (path) => {
  selectedPath.value = path
}

// 初始化
watch(visible, async (val) => {
  if (val) {
    selectedPath.value = props.initialPath || ''
    addressInput.value = props.initialPath || ''
    history.value = []
    historyIndex.value = -1
    
    // 先加载驱动器缓存
    await loadDrivesCache()
    
    if (props.initialPath) {
      await navigateTo(props.initialPath)
    } else {
      await loadDrives()
    }
  }
})

// 加载驱动器缓存（用于侧边栏）
const loadDrivesCache = async () => {
  try {
    const res = await getSystemDrives()
    cachedDrives.value = res.data || []
  } catch (e) {
    console.error('加载驱动器失败:', e)
  }
}

// 加载驱动器
const loadDrives = async () => {
  loading.value = true
  drives.value = []
  currentData.value = null
  currentPath.value = ''
  addressInput.value = ''
  
  try {
    const res = await getSystemDrives()
    drives.value = res.data || []
    cachedDrives.value = res.data || []
  } catch (e) {
    console.error('加载驱动器失败:', e)
  } finally {
    loading.value = false
  }
}

// 导航到目录
const navigateTo = async (path, addToHistory = true) => {
  loading.value = true
  drives.value = []
  
  try {
    const res = await browseDirectory(path)
    if (res.error) {
      ElMessage.error(res.message || '无法访问此目录')
      return
    }
    currentData.value = res.data
    currentPath.value = res.data?.current || ''
    addressInput.value = currentPath.value
    selectedPath.value = currentPath.value
    
    // 添加到历史
    if (addToHistory) {
      history.value = history.value.slice(0, historyIndex.value + 1)
      history.value.push(currentPath.value)
      historyIndex.value = history.value.length - 1
    }
  } catch (e) {
    console.error('浏览目录失败:', e)
    ElMessage.error('浏览目录失败')
  } finally {
    loading.value = false
  }
}

// 地址栏导航
const navigateToAddress = () => {
  if (addressInput.value) {
    navigateTo(addressInput.value)
  }
}

// 后退
const goBack = () => {
  if (historyIndex.value > 0) {
    historyIndex.value--
    const path = history.value[historyIndex.value]
    navigateTo(path, false)
  }
}

// 上级目录
const goUp = () => {
  if (currentData.value?.parent) {
    navigateTo(currentData.value.parent)
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
  const fullPath = newPath.includes(':') ? newPath + '\\' : newPath
  navigateTo(fullPath)
}

// 新建文件夹（提示功能）
const createFolder = () => {
  ElMessageBox.prompt('请输入新文件夹名称', '新建文件夹', {
    confirmButtonText: '创建',
    cancelButtonText: '取消',
    inputPattern: /^[^<>:"/\\|?*]+$/,
    inputErrorMessage: '文件夹名称不能包含特殊字符'
  }).then(({ value }) => {
    ElMessage.info(`新建文件夹功能需要后端支持，文件夹名: ${value}`)
  }).catch(() => {})
}

// 确认选择
const confirmSelect = () => {
  emit('select', selectedPath.value)
  visible.value = false
}

// 刷新当前目录
const refreshCurrent = () => {
  if (currentPath.value) {
    navigateTo(currentPath.value, false)
  } else {
    loadDrives()
  }
}
</script>

<style lang="scss" scoped>
.folder-picker-dialog {
  :deep(.el-dialog__body) {
    padding: 0 20px 20px;
  }
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
  
  .nav-buttons {
    display: flex;
    gap: 8px;
  }
  
  .address-bar {
    flex: 1;
  }
}

.path-nav {
  padding: 10px 0;
  
  :deep(.el-breadcrumb__item) {
    cursor: pointer;
    
    &:hover .el-breadcrumb__inner {
      color: #409EFF;
    }
  }
}

.main-content {
  display: flex;
  gap: 16px;
  height: 360px;
}

.sidebar {
  width: 160px;
  flex-shrink: 0;
  border-right: 1px solid #eee;
  padding-right: 12px;
  overflow-y: auto;
  
  .sidebar-title {
    font-size: 12px;
    color: #909399;
    font-weight: 600;
    margin-bottom: 8px;
    text-transform: uppercase;
  }
  
  .quick-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    color: #606266;
    transition: all 0.2s;
    
    &:hover {
      background: #f5f7fa;
    }
    
    &.active {
      background: #ecf5ff;
      color: #409EFF;
    }
    
    .el-icon {
      font-size: 16px;
    }
  }
}

.folder-list {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background: #fafafa;
  
  .folder-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 16px;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
    background: #fff;
    transition: all 0.15s;
    
    &:hover {
      background: #f5f7fa;
    }
    
    &.selected {
      background: #ecf5ff;
      border-left: 3px solid #409EFF;
    }
    
    &.disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    &.parent {
      color: #909399;
      background: #fafafa;
    }
    
    .folder-icon {
      font-size: 24px;
      color: #E6A23C;
    }
    
    .drive-icon {
      font-size: 24px;
      color: #409EFF;
    }
    
    .item-info {
      flex: 1;
      
      .name {
        font-weight: 500;
        color: #303133;
      }
      
      .meta {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 4px;
        font-size: 12px;
        color: #909399;
      }
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
      color: #dcdfe6;
    }
  }
}

.selection-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  
  .label {
    font-size: 13px;
    color: #606266;
    white-space: nowrap;
  }
  
  .el-input {
    flex: 1;
  }
}

.dialog-footer {
  display: flex;
  align-items: center;
  width: 100%;
}
</style>
