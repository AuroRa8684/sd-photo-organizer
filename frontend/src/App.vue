<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 侧边导航栏 -->
      <el-aside width="200px" class="app-aside">
        <div class="logo">
          <el-icon size="24"><Camera /></el-icon>
          <span>SD Photo Organizer</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="app-menu"
          router
        >
          <el-menu-item index="/">
            <el-icon><Upload /></el-icon>
            <span>导入照片</span>
          </el-menu-item>
          <el-menu-item index="/gallery">
            <el-icon><Picture /></el-icon>
            <span>照片墙</span>
          </el-menu-item>
          <el-menu-item index="/summary">
            <el-icon><DataAnalysis /></el-icon>
            <span>拍摄总结</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Camera, Upload, Picture, DataAnalysis } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => {
  return route.path
})
</script>

<style lang="scss">
.app-container {
  height: 100vh;
}

.app-aside {
  background: #304156;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #fff;
    font-size: 16px;
    font-weight: bold;
    border-bottom: 1px solid #3d4a5e;
  }
  
  .app-menu {
    border: none;
    background: transparent;
    
    .el-menu-item {
      color: #bfcbd9;
      
      &:hover {
        background: #263445;
      }
      
      &.is-active {
        color: #409EFF;
        background: #263445;
      }
    }
  }
}

.app-main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
