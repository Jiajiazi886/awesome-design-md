<template>
  <el-container class="h-screen w-screen overflow-hidden bg-slate-50 text-slate-800">
    <!-- 侧边导航栏 -->
    <el-aside width="240px" class="bg-white border-r border-slate-200 z-10 shadow-sm flex flex-col">
      <div class="p-5 text-xl font-semibold text-slate-800 border-b border-slate-100 flex items-center gap-3">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center shadow-md">
          <el-icon><DataBoard /></el-icon>
        </div>
        <span class="tracking-tight">逆水寒联赛分析</span>
      </div>
      <el-menu
        default-active="/"
        class="border-none bg-transparent flex-1 px-3 py-4"
        text-color="#64748b"
        active-text-color="#2563eb"
        router
      >
        <el-menu-item index="/" class="menu-item">
          <el-icon><DataBoard /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        <el-menu-item index="/members" class="menu-item">
          <el-icon><User /></el-icon>
          <span>帮众管理</span>
        </el-menu-item>
        <el-menu-item index="/team-builder" class="menu-item">
          <el-icon><Grid /></el-icon>
          <span>团队排表</span>
        </el-menu-item>
        <el-menu-item index="/analysis" class="menu-item">
          <el-icon><PieChart /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
        <el-menu-item index="/skills" class="menu-item">
          <el-icon><MagicStick /></el-icon>
          <span>内功计算</span>
        </el-menu-item>
        <el-menu-item index="/settings" class="menu-item">
          <el-icon><Setting /></el-icon>
          <span>职业颜色</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-main class="p-0 relative bg-slate-50/80">
      <div class="absolute inset-0 bg-white/40 backdrop-blur-3xl pointer-events-none z-0"></div>
      <div class="relative z-10 h-full overflow-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { DataBoard, User, Grid, PieChart, MagicStick, Setting } from '@element-plus/icons-vue'
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f8fafc;
}

/* 侧边栏菜单 Apple-like 风格 */
.menu-item {
  height: 44px !important;
  line-height: 44px !important;
  margin-bottom: 8px !important;
  border-radius: 12px !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  padding: 0 16px !important;
  display: flex !important;
  align-items: center !important;
}

.menu-item .el-icon {
  margin-right: 12px !important;
  font-size: 18px !important;
  transition: transform 0.2s ease !important;
}

.menu-item:hover {
  background-color: #f1f5f9 !important;
  color: #0f172a !important;
}

.menu-item.is-active {
  background-color: #eff6ff !important;
  color: #2563eb !important;
  font-weight: 600 !important;
  box-shadow: 0 1px 2px rgba(37, 99, 235, 0.05) !important;
}

.menu-item.is-active .el-icon {
  transform: scale(1.1);
  color: #2563eb !important;
}

.el-menu {
  border-right: none !important;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>