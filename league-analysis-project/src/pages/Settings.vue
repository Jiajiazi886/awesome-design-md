<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSettingsStore } from '../stores/settingsStore'
import { useMemberStore } from '../stores/memberStore'

const settingsStore = useSettingsStore()
const memberStore = useMemberStore()

// 自动提取目前所有存在的职业
const availableJobs = computed(() => {
  const jobs = new Set<string>()
  memberStore.members.forEach(m => {
    if (m.job) jobs.add(m.job)
  })
  
  // 确保 store 里有默认颜色，如果没有就设置一个白色
  jobs.forEach(job => {
    if (!settingsStore.jobColors[job]) {
      settingsStore.updateJobColor(job, '#ffffff')
    }
  })
  
  return Array.from(jobs)
})

const handleColorChange = (job: string, newColor: string) => {
  settingsStore.updateJobColor(job, newColor)
}

const predefinedColors = [
  '#e8f5e9', '#ffebee', '#fff8e1', '#f3e5f5', 
  '#e0f7fa', '#fce4ec', '#e3f2fd', '#e0f2f1', 
  '#fff3e0', '#e8eaf6', '#fafafa', '#ffffff',
  '#fecaca', '#fef08a', '#bbf7d0', '#bfdbfe', '#e9d5ff'
]
</script>

<template>
  <div class="p-8 h-full flex flex-col bg-[#f5f5f7] text-gray-900">
    <div class="mb-6">
      <h1 class="text-3xl font-semibold tracking-tight">界面设置</h1>
      <p class="text-gray-500 mt-2">自定义各个职业的专属背景颜色，这些颜色将应用于排表和人员卡片中。</p>
    </div>

    <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 max-w-3xl">
      <h2 class="text-xl font-medium mb-6">职业背景色配置</h2>
      
      <div v-if="availableJobs.length === 0" class="text-gray-400 py-8 text-center bg-gray-50 rounded-xl">
        目前没有发现任何职业数据，请先前往“帮众管理”导入人员。
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="job in availableJobs" 
          :key="job"
          class="flex items-center justify-between p-4 rounded-xl border border-gray-100 bg-gray-50/50 hover:bg-gray-50 transition-colors"
        >
          <div class="flex items-center gap-3">
            <div 
              class="w-4 h-4 rounded-full border border-gray-200 shadow-sm"
              :style="{ backgroundColor: settingsStore.getJobColor(job) }"
            ></div>
            <span class="font-medium">{{ job }}</span>
          </div>
          
          <el-color-picker 
            v-model="settingsStore.jobColors[job]" 
            show-alpha
            :predefine="predefinedColors"
            @change="(val) => handleColorChange(job, val)"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.el-color-picker__trigger) {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 4px;
}
</style>