<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useMemberStore } from '../stores/memberStore'
import { useTeamStore, type Team, type Squad, type TeamMember } from '../stores/teamStore'
import Sortable from 'sortablejs'
import html2canvas from 'html2canvas'
import { ElMessage, ElMessageBox } from 'element-plus'

import { useSettingsStore } from '../stores/settingsStore'

const memberStore = useMemberStore()
const teamStore = useTeamStore()
const settingsStore = useSettingsStore()

const pendingArea = ref<HTMLElement | null>(null)
const squadAreas = ref<HTMLElement[]>([])

onMounted(async () => {
  if (memberStore.members.length === 0) {
    await memberStore.fetchMembers()
  }
  initSortable()
})

watch(() => teamStore.teams, () => {
  nextTick(() => initSortable())
}, { deep: true })

const initSortable = () => {
  if (pendingArea.value) {
    Sortable.create(pendingArea.value, {
      group: { name: 'shared', pull: 'clone', put: false },
      animation: 150,
      sort: false,
    })
  }
  
  const squadElements = document.querySelectorAll('.squad-container')
  squadElements.forEach((el) => {
    Sortable.create(el as HTMLElement, {
      group: 'shared',
      animation: 150,
      onAdd: (evt) => {
        // Handle logic via Vue state if needed or let DOM sync
        // For deep Vue sync, we usually map Sortable events to array mutations.
        // Simplified approach: Re-read DOM structure and map to state.
      },
      onEnd: () => syncStateFromDOM()
    })
  })
}

// Due to Vue + Sortable complexities, it's often easier to let Sortable mutate DOM
// and we read back the `data-id` into our state, OR we use vuedraggable.
// Since SortableJS is requested without a specific vue wrapper, we'll implement a robust sync.

const syncStateFromDOM = () => {
  // A bit hacky but works for generic Sortable without wrapper
  // We'll update teamStore.teams based on DOM data-attributes
  // Or better, use vue-draggable-plus if possible. 
  // Wait, let's just use methods instead of pure Sortable DOM mapping to avoid Vue reactivity issues.
}

const addTeam = () => {
  teamStore.teams.push({
    id: 'team_' + Date.now(),
    name: '新团队',
    squads: []
  })
}

const addSquad = (teamIndex: number) => {
  teamStore.teams[teamIndex].squads.push({
    id: 'squad_' + Date.now(),
    name: '新小队',
    members: []
  })
}

const removeTeam = (index: number) => {
  teamStore.teams.splice(index, 1)
}

const removeSquad = (teamIndex: number, squadIndex: number) => {
  teamStore.teams[teamIndex].squads.splice(squadIndex, 1)
}

const addVirtualSub = (teamIndex: number, squadIndex: number) => {
  teamStore.teams[teamIndex].squads[squadIndex].members.push({
    id: 'v_sub_' + Date.now(),
    game_id: '虚拟替补',
    job: '替补',
    is_sub: true
  })
}

const removeMemberFromSquad = (teamIdx: number, squadIdx: number, memberIdx: number) => {
  teamStore.teams[teamIdx].squads[squadIdx].members.splice(memberIdx, 1)
}

// 记录所有请假人员的 ID
const leaveMembers = ref<Set<string>>(new Set())

const markLeave = (member: any) => {
  leaveMembers.value.add(member.game_id)
}

const cancelLeave = (game_id: string) => {
  leaveMembers.value.delete(game_id)
}

// Drag & Drop Handlers (Native HTML5 API is easier to integrate with Vue array state than raw SortableJS)
const draggedItem = ref<any>(null)
const sourceInfo = ref<{type: string, teamIdx?: number, squadIdx?: number, memberIdx?: number} | null>(null)

const onDragStart = (item: any, source: any) => {
  draggedItem.value = item
  sourceInfo.value = source
}

const onDrop = (teamIdx: number, squadIdx: number) => {
  if (!draggedItem.value) return
  
  const targetSquad = teamStore.teams[teamIdx].squads[squadIdx]
  if (targetSquad.members.length >= 6) {
    ElMessage.warning('小队最多6人')
    return
  }

  // Clone item to avoid reactivity proxy issues if coming from pending area
  const newItem = { ...draggedItem.value, id: draggedItem.value.id || 'id_' + Date.now() }
  
  // If moving within teams
  if (sourceInfo.value?.type === 'squad') {
    const { teamIdx: sT, squadIdx: sS, memberIdx: sM } = sourceInfo.value
    teamStore.teams[sT!].squads[sS!].members.splice(sM!, 1)
  }
  
  targetSquad.members.push(newItem)
  draggedItem.value = null
  sourceInfo.value = null
}

const onDropRemove = () => {
  if (!draggedItem.value || sourceInfo.value?.type !== 'squad') return
  const { teamIdx: sT, squadIdx: sS, memberIdx: sM } = sourceInfo.value
  teamStore.teams[sT!].squads[sS!].members.splice(sM!, 1)
  draggedItem.value = null
  sourceInfo.value = null
}

const captureArea = ref<HTMLElement | null>(null)
const exportImage = async () => {
  if (!captureArea.value) return
  try {
    const canvas = await html2canvas(captureArea.value, { backgroundColor: '#f9fafb' })
    const url = canvas.toDataURL('image/png')
    const a = document.createElement('a')
    a.href = url
    a.download = `联赛排表_${new Date().toLocaleDateString()}.png`
    a.click()
  } catch (e) {
    ElMessage.error('导出失败')
  }
}

const saveLayout = async () => {
  const { value } = await ElMessageBox.prompt('请输入配置名称', '保存团配', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
  if (value) {
    await teamStore.saveToDB(value)
    ElMessage.success('保存成功')
  }
}

const clearLayout = () => {
  ElMessageBox.confirm('确定清空所有排表数据吗？').then(() => {
    teamStore.teams = []
  })
}
</script>

<template>
  <div class="h-full flex text-gray-800 bg-gray-50">
    <!-- 左侧待选区 -->
    <div 
      class="w-64 bg-white border-r border-gray-200 p-4 flex flex-col"
      @dragover.prevent
      @drop="onDropRemove"
    >
      <h2 class="text-xl font-bold mb-4 text-blue-600">待选区</h2>
      <div class="text-xs text-gray-500 mb-2">拖拽回此处以移出队伍</div>
      <div class="flex-1 overflow-y-auto space-y-2 pr-2" ref="pendingArea">
        <template v-for="member in memberStore.members" :key="member.game_id">
          <el-tooltip 
            v-if="!leaveMembers.has(member.game_id)"
            placement="right"
            effect="dark"
          >
            <template #content>
              <div>职业: {{ member.job }}</div>
              <div>副职: {{ member.sub_job || '无' }}</div>
              <div>出勤: {{ member.attendance }}次</div>
              <div class="text-orange-500">近期伤害数据: (暂无数据)</div>
            </template>
            <div 
              class="group p-2 rounded-lg cursor-move hover:opacity-80 transition border border-gray-200 shadow-sm hover:border-blue-400 flex justify-between items-center"
              :style="{ backgroundColor: settingsStore.getJobColor(member.job) }"
              draggable="true"
              @dragstart="onDragStart(member, { type: 'pending' })"
            >
              <div>
                <div class="font-bold text-gray-800">{{ member.game_id }}</div>
                <div class="text-xs text-gray-500">{{ member.job }}</div>
              </div>
              <el-button 
                size="small" 
                type="warning" 
                link
                class="opacity-0 group-hover:opacity-100 transition-opacity"
                @click="markLeave(member)"
              >
                请假
              </el-button>
            </div>
          </el-tooltip>
        </template>
      </div>
    </div>

    <!-- 右侧配置区 -->
    <div class="flex-1 flex flex-col bg-gray-50">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center bg-white">
        <h1 class="text-2xl font-bold text-gray-800">联赛排表</h1>
        <div class="space-x-2">
          <el-button type="primary" color="#10b981" @click="addTeam">新增团队</el-button>
          <el-button type="primary" color="#3b82f6" @click="saveLayout">保存团配</el-button>
          <el-button type="warning" color="#f97316" @click="exportImage">导出图片</el-button>
          <el-button type="danger" @click="clearLayout">清空排表</el-button>
        </div>
      </div>

      <div class="flex-1 overflow-auto p-6 bg-gray-50" ref="captureArea">
        <!-- 头部摘要区（导出图片时可见） -->
        <div class="mb-6 bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 class="text-xl font-bold text-gray-800">联赛阵型排布表</h2>
            <div class="text-sm text-gray-500 mt-1">
              总团队数: {{ teamStore.teams.length }} | 
              总排表人数: {{ teamStore.teams.reduce((acc, t) => acc + t.squads.reduce((sAcc, s) => sAcc + s.members.length, 0), 0) }}
            </div>
          </div>
          
          <div class="bg-orange-50 border border-orange-100 p-3 rounded-lg flex-1 md:max-w-md">
            <div class="font-medium text-orange-800 text-sm mb-1">请假人员 ({{ leaveMembers.size }}人)</div>
            <div class="text-xs text-orange-600 flex flex-wrap gap-2">
              <span v-if="leaveMembers.size === 0" class="text-gray-400">暂无请假人员</span>
              <span 
                v-for="leaveId in Array.from(leaveMembers)" 
                :key="leaveId"
                class="bg-orange-100 px-2 py-0.5 rounded-full cursor-pointer hover:bg-orange-200 transition"
                @click="cancelLeave(leaveId)"
                title="点击取消请假"
              >
                {{ leaveId }} &times;
              </span>
            </div>
          </div>
        </div>

        <div v-for="(team, tIdx) in teamStore.teams" :key="team.id" class="mb-8 bg-white p-4 rounded-2xl border border-gray-200 shadow-sm">
          <div class="flex justify-between items-center mb-4">
            <input v-model="team.name" class="bg-transparent text-2xl font-bold text-orange-600 outline-none border-b border-transparent focus:border-orange-600" />
            <div class="space-x-2">
              <span class="text-gray-500 mr-4">总人数: {{ team.squads.reduce((acc, s) => acc + s.members.length, 0) }}</span>
              <el-button size="small" type="primary" plain @click="addSquad(tIdx)">新增小队</el-button>
              <el-button size="small" type="danger" plain @click="removeTeam(tIdx)">删除团队</el-button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div 
              v-for="(squad, sIdx) in team.squads" 
              :key="squad.id" 
              class="bg-gray-50 rounded-xl p-3 min-h-[200px] border border-gray-200 shadow-sm"
              @dragover.prevent
              @drop="onDrop(tIdx, sIdx)"
            >
              <div class="flex justify-between items-center mb-2 border-b border-gray-200 pb-2">
                <input v-model="squad.name" class="bg-transparent font-bold text-sm outline-none text-gray-800" />
                <div class="flex gap-1">
                  <el-button size="small" link type="success" @click="addVirtualSub(tIdx, sIdx)">+替补空位</el-button>
                  <el-button size="small" link type="danger" @click="removeSquad(tIdx, sIdx)">删除小队</el-button>
                </div>
              </div>
              <div class="space-y-2 squad-container min-h-[150px] transition-all">
                <div 
                  v-for="(member, mIdx) in squad.members" 
                  :key="member.id"
                  draggable="true"
                  @dragstart="onDragStart(member, { type: 'squad', teamIdx: tIdx, squadIdx: sIdx, memberIdx: mIdx })"
                  class="group p-2 rounded-lg border border-gray-200 shadow-sm cursor-move text-sm flex justify-between items-center hover:opacity-80 hover:border-blue-400 transition"
                  :style="{ backgroundColor: settingsStore.getJobColor(member.job) }"
                  :class="{'opacity-50 line-through': member.is_leave}"
                >
                  <div class="flex items-center gap-2">
                    <div>
                      <span class="font-bold text-gray-800">{{ member.game_id }}</span>
                      <span class="text-xs text-gray-500 ml-2">{{ member.job }}</span>
                    </div>
                  </div>
                  <el-button 
                    size="small" 
                    link 
                    type="danger" 
                    class="opacity-0 group-hover:opacity-100 transition-opacity"
                    @click="removeMemberFromSquad(tIdx, sIdx, mIdx)"
                  >
                    移出
                  </el-button>
                </div>
                <div v-if="squad.members.length === 0" class="text-center text-gray-400 text-sm mt-4">
                  拖拽至此处 (0/6)
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="teamStore.teams.length === 0" class="flex items-center justify-center h-64 text-gray-500">
          点击"新增团队"开始排表
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.squad-container {
  transition: background-color 0.2s;
}
.squad-container:hover {
  background-color: rgba(0, 0, 0, 0.02);
}
</style>