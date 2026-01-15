<template>
  <div id="app">
    <el-container class="app-container">
      <!-- 侧边导航栏 -->
      <el-aside width="200px" class="app-aside">
        <div class="logo">
          <el-icon size="24"><Camera /></el-icon>
          <span>PhotoFlow</span>
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
        
        <!-- 版本信息 -->
        <div class="app-footer">
          <div class="version">v1.0.0</div>
          <a href="https://github.com" target="_blank" class="help-link">帮助文档</a>
        </div>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <keep-alive>
            <component :is="Component" />
          </keep-alive>
        </router-view>
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
  display: flex;
  flex-direction: column;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #fff;
    font-size: 15px;
    font-weight: bold;
    border-bottom: 1px solid #3d4a5e;
  }
  
  .app-menu {
    flex: 1;
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
  
  .app-footer {
    padding: 16px;
    text-align: center;
    border-top: 1px solid #3d4a5e;
    
    .version {
      font-size: 11px;
      color: #5a6270;
      margin-bottom: 4px;
    }
    
    .help-link {
      font-size: 12px;
      color: #909399;
      text-decoration: none;
      
      &:hover {
        color: #409EFF;
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
