import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  const jobColors = ref<Record<string, string>>({
    '素问': '#e8f5e9', // 浅绿色
    '血河': '#ffebee', // 浅红色
    '铁衣': '#fff8e1', // 浅黄色
    '鸿音': '#f3e5f5', // 浅紫色
    '玄机': '#e0f7fa', // 浅青色
    '九灵': '#fce4ec', // 浅紫粉
    '神相': '#e3f2fd', // 浅蓝色
    '潮光': '#e0f2f1', // 水蓝色
    '龙吟': '#fff3e0', // 浅橙黄
    '沧澜': '#e8eaf6', // 青灰色
    '碎梦': '#fafafa', // 极浅灰
    '未知': '#ffffff'  // 纯白
  })

  const updateJobColor = (job: string, color: string) => {
    jobColors.value[job] = color
  }

  const getJobColor = (job: string) => {
    return jobColors.value[job] || '#ffffff'
  }

  return { jobColors, updateJobColor, getJobColor }
}, {
  persist: true
})