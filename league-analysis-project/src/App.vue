<template>
  <el-container class="h-screen w-screen overflow-hidden bg-[#141413] text-[#faf9f5]">
    <!-- 侧边导航栏 -->
    <el-aside width="200px" class="bg-[#1c1c1a] border-r border-[#2a2a28]">
      <div class="p-4 text-xl font-bold text-[#d97757] border-b border-[#2a2a28]">
        逆水寒联赛分析
      </div>
      <el-menu
        default-active="/"
        class="border-none bg-transparent"
        text-color="#a3a3a1"
        active-text-color="#d97757"
        router
      >
        <el-menu-item index="/">
          <el-icon><DataBoard /></el-icon>
          <span>首页概览</span>
        </el-menu-item>
        <el-menu-item index="/members">
          <el-icon><User /></el-icon>
          <span>帮众管理</span>
        </el-menu-item>
        <el-menu-item index="/team-builder">
          <el-icon><Grid /></el-icon>
          <span>团队排表</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><PieChart /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
        <el-menu-item index="/skills">
          <el-icon><MagicStick /></el-icon>
          <span>内功计算</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-main class="p-0 bg-[#141413]">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { DataBoard, User, Grid, PieChart, MagicStick } from '@element-plus/icons-vue'
</script>

<style>
body {
  margin: 0;
  font-family: 'Poppins', 'Lora', sans-serif;
  background-color: #141413;
}
.el-menu-item:hover {
  background-color: #2a2a28 !important;
}
.el-menu-item.is-active {
  background-color: #2a2a28 !important;
  font-weight: bold;
}
</style>