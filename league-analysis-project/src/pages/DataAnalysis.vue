<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'

const teams = ref<any[]>([])
const selectedTeamId = ref<number | null>(null)
const uploadedMatchId = ref<number | null>(null)
const matchData = ref<any>(null)

const lineChartRef = ref<HTMLElement | null>(null)
const radarChartRef = ref<HTMLElement | null>(null)

onMounted(async () => {
  try {
    const res = await axios.get('/api/teams')
    teams.value = res.data
  } catch (e) {
    console.error(e)
  }
})

const handleUploadSuccess = (response: any) => {
  uploadedMatchId.value = response.match_id
  ElMessage.success('上传成功，请选择团配进行分析')
}

const handleUploadError = () => {
  ElMessage.error('上传失败')
}

const analyzeData = async () => {
  if (!selectedTeamId.value || !uploadedMatchId.value) {
    ElMessage.warning('请确保已上传数据并选择团配')
    return
  }
  
  try {
    const res = await axios.get(`/api/analysis/team-data?team_id=${selectedTeamId.value}&match_id=${uploadedMatchId.value}`)
    matchData.value = res.data
    ElMessage.success('分析数据加载成功')
    
    await nextTick()
    renderCharts()
  } catch (e) {
    ElMessage.error('分析数据加载失败')
  }
}

const renderCharts = () => {
  if (!lineChartRef.value || !radarChartRef.value || !matchData.value) return
  
  // 模拟数据处理逻辑
  const lineChart = echarts.init(lineChartRef.value)
  const radarChart = echarts.init(radarChartRef.value)
  
  lineChart.setOption({
    backgroundColor: 'transparent',
    title: { text: '小队伤害波动趋势', textStyle: { color: '#666' } },
    tooltip: { trigger: 'axis' },
    xAxis: { 
      type: 'category', 
      data: ['小队1', '小队2', '小队3', '小队4', '小队5', '小队6'], 
      axisLine: { lineStyle: { color: '#E5E5EA' } }, 
      axisLabel: { color: '#666' } 
    },
    yAxis: { 
      type: 'value', 
      splitLine: { lineStyle: { color: '#F2F2F7' } }, 
      axisLabel: { color: '#666' } 
    },
    series: [
      {
        data: [150, 230, 224, 218, 135, 147],
        type: 'line',
        smooth: true,
        lineStyle: { color: '#FF2D55', width: 3 }, // Apple Health Pink
        itemStyle: { color: '#FF2D55' }
      }
    ]
  })
  
  radarChart.setOption({
    backgroundColor: 'transparent',
    title: { text: '多小队综合能力对比', textStyle: { color: '#666' } },
    tooltip: {},
    legend: { data: ['小队1', '小队2'], textStyle: { color: '#666' }, bottom: 0 },
    radar: {
      indicator: [
        { name: '总伤害', max: 6500 },
        { name: '承伤', max: 16000 },
        { name: '治疗', max: 30000 },
        { name: '击杀', max: 38000 },
        { name: '助攻', max: 52000 }
      ],
      splitArea: { areaStyle: { color: ['#FFFFFF', '#F2F2F7'] } },
      axisLine: { lineStyle: { color: '#E5E5EA' } },
      splitLine: { lineStyle: { color: '#E5E5EA' } },
      axisName: { color: '#666' }
    },
    series: [
      {
        name: '能力对比',
        type: 'radar',
        data: [
          {
            value: [4200, 3000, 20000, 35000, 50000],
            name: '小队1',
            areaStyle: { color: 'rgba(255, 45, 85, 0.2)' }, // #FF2D55
            lineStyle: { color: '#FF2D55', width: 2 },
            itemStyle: { color: '#FF2D55' }
          },
          {
            value: [5000, 14000, 28000, 26000, 42000],
            name: '小队2',
            areaStyle: { color: 'rgba(0, 122, 255, 0.2)' }, // #007AFF
            lineStyle: { color: '#007AFF', width: 2 },
            itemStyle: { color: '#007AFF' }
          }
        ]
      }
    ]
  })
}
</script>

<template>
  <div class="h-full flex text-gray-800 bg-[#F2F2F7]">
    <!-- 左侧数据概览区 -->
    <div class="w-1/3 bg-white border-r border-gray-200 p-6 flex flex-col gap-6 shadow-sm z-10">
      <h2 class="text-2xl font-bold text-gray-900">分析面板</h2>
      
      <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
        <h3 class="text-lg mb-2 font-bold text-gray-800">1. 上传比赛数据</h3>
        <el-upload
          class="upload-demo"
          drag
          action="/api/analysis/upload"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          accept=".csv"
        >
          <el-icon class="el-icon--upload text-gray-400"><upload-filled /></el-icon>
          <div class="el-upload__text text-gray-500">
            拖拽 CSV 文件到此处或 <em class="text-[#007AFF]">点击上传</em>
          </div>
        </el-upload>
      </div>

      <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
        <h3 class="text-lg mb-2 font-bold text-gray-800">2. 选择关联团配</h3>
        <el-select v-model="selectedTeamId" placeholder="选择保存的团配" class="w-full">
          <el-option
            v-for="team in teams"
            :key="team.id"
            :label="team.name"
            :value="team.id"
          />
        </el-select>
      </div>

      <el-button 
        type="primary" 
        class="w-full mt-4 rounded-xl shadow-sm font-medium" 
        color="#007AFF"
        size="large"
        @click="analyzeData"
      >
        开始生成分析图表
      </el-button>

      <!-- 概览指标卡片 -->
      <div v-if="matchData" class="mt-4 space-y-4">
        <h3 class="text-lg font-bold border-b border-gray-100 pb-2 text-gray-800">本场核心指标</h3>
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-white rounded-2xl shadow-sm p-4 border-l-4 border-[#FF2D55] text-center hover:shadow-md transition-shadow">
            <div class="text-gray-500 text-sm font-medium">总输出</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">1.2M</div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-4 border-l-4 border-[#007AFF] text-center hover:shadow-md transition-shadow">
            <div class="text-gray-500 text-sm font-medium">总承伤</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">850K</div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-4 border-l-4 border-[#34C759] text-center hover:shadow-md transition-shadow">
            <div class="text-gray-500 text-sm font-medium">有效治疗</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">980K</div>
          </div>
          <div class="bg-white rounded-2xl shadow-sm p-4 border-l-4 border-[#FF9500] text-center hover:shadow-md transition-shadow">
            <div class="text-gray-500 text-sm font-medium">击杀/死亡</div>
            <div class="text-2xl font-bold text-gray-900 mt-1">450/120</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧图表区 -->
    <div class="flex-1 bg-[#F2F2F7] p-6 overflow-y-auto">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">可视化分析</h2>
      
      <div v-if="!matchData" class="h-full flex items-center justify-center text-gray-400 font-medium">
        请在左侧完成数据上传与团配选择
      </div>
      
      <div v-else class="space-y-8 pb-12">
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <div ref="lineChartRef" class="w-full h-[400px]"></div>
        </div>
        
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
          <div ref="radarChartRef" class="w-full h-[500px]"></div>
        </div>
        
        <!-- 团队切片滚动展示占位 -->
        <div class="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 min-h-[300px]">
          <h3 class="text-lg font-bold text-gray-800 mb-4">团队切片滚动展示</h3>
          <div class="flex items-center justify-center h-[200px] text-gray-400 border-2 border-dashed border-gray-200 rounded-2xl bg-gray-50">
            向下滚动以展示各小队详细切片数据
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
:deep(.el-upload-dragger) {
  background-color: #FAFAFA !important;
  border-color: #E5E5EA !important;
  border-radius: 12px !important;
  transition: all 0.3s;
}
:deep(.el-upload-dragger:hover) {
  border-color: #007AFF !important;
  background-color: #F0F8FF !important;
}
:deep(.el-input__wrapper) {
  background-color: #F2F2F7 !important;
  box-shadow: none !important;
  border-radius: 8px !important;
}
:deep(.el-input__inner) {
  color: #333 !important;
}
</style>
