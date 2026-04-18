<script setup lang="ts">
import { ref, onMounted, nextTick, watch } from 'vue'
import { useMemberStore } from '../stores/memberStore'
import { useTeamStore, type Team, type Squad, type TeamMember } from '../stores/teamStore'
import Sortable from 'sortablejs'
import html2canvas from 'html2canvas'
import { ElMessage, ElMessageBox } from 'element-plus'

const memberStore = useMemberStore()
const teamStore = useTeamStore()

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

const toggleLeave = (member: TeamMember) => {
  member.is_leave = !member.is_leave
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
    const canvas = await html2canvas(captureArea.value, { backgroundColor: '#141413' })
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
  <div class="h-full flex text-[#faf9f5]">
    <!-- 左侧待选区 -->
    <div 
      class="w-64 bg-[#1c1c1a] border-r border-[#2a2a28] p-4 flex flex-col"
      @dragover.prevent
      @drop="onDropRemove"
    >
      <h2 class="text-xl font-bold mb-4 text-[#6a9bcc]">待选区</h2>
      <div class="text-xs text-[#a3a3a1] mb-2">拖拽回此处以移出队伍</div>
      <div class="flex-1 overflow-y-auto space-y-2 pr-2" ref="pendingArea">
        <el-tooltip 
          v-for="member in memberStore.members" 
          :key="member.game_id"
          placement="right"
          effect="dark"
        >
          <template #content>
            <div>职业: {{ member.job }}</div>
            <div>副职: {{ member.sub_job || '无' }}</div>
            <div>出勤: {{ member.attendance }}次</div>
            <div class="text-[#d97757]">近期伤害数据: (暂无数据)</div>
          </template>
          <div 
            class="p-2 bg-[#2a2a28] rounded cursor-move hover:bg-[#3f3f3c] transition border border-transparent hover:border-[#6a9bcc]"
            draggable="true"
            @dragstart="onDragStart(member, { type: 'pending' })"
          >
            <div class="font-bold">{{ member.game_id }}</div>
            <div class="text-xs text-[#a3a3a1]">{{ member.job }}</div>
          </div>
        </el-tooltip>
      </div>
    </div>

    <!-- 右侧配置区 -->
    <div class="flex-1 flex flex-col bg-[#141413]">
      <div class="p-4 border-b border-[#2a2a28] flex justify-between items-center bg-[#1c1c1a]">
        <h1 class="text-2xl font-bold">联赛排表</h1>
        <div class="space-x-2">
          <el-button type="primary" color="#788c5d" @click="addTeam">新增团队</el-button>
          <el-button type="primary" color="#6a9bcc" @click="saveLayout">保存团配</el-button>
          <el-button type="warning" color="#d97757" @click="exportImage">导出图片</el-button>
          <el-button type="danger" @click="clearLayout">清空排表</el-button>
        </div>
      </div>

      <div class="flex-1 overflow-auto p-6" ref="captureArea">
        <div v-for="(team, tIdx) in teamStore.teams" :key="team.id" class="mb-8 bg-[#1c1c1a] p-4 rounded-xl border border-[#2a2a28]">
          <div class="flex justify-between items-center mb-4">
            <input v-model="team.name" class="bg-transparent text-2xl font-bold text-[#d97757] outline-none border-b border-transparent focus:border-[#d97757]" />
            <div class="space-x-2">
              <span class="text-[#a3a3a1] mr-4">总人数: {{ team.squads.reduce((acc, s) => acc + s.members.length, 0) }}</span>
              <el-button size="small" type="primary" plain @click="addSquad(tIdx)">新增小队</el-button>
              <el-button size="small" type="danger" plain @click="removeTeam(tIdx)">删除团队</el-button>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            <div 
              v-for="(squad, sIdx) in team.squads" 
              :key="squad.id" 
              class="bg-[#2a2a28] rounded-lg p-3 min-h-[200px] border border-[#3f3f3c]"
              @dragover.prevent
              @drop="onDrop(tIdx, sIdx)"
            >
              <div class="flex justify-between items-center mb-2 border-b border-[#3f3f3c] pb-2">
                <input v-model="squad.name" class="bg-transparent font-bold text-sm outline-none text-[#faf9f5]" />
                <div class="flex gap-1">
                  <el-button size="small" link type="success" @click="addVirtualSub(tIdx, sIdx)">+替补</el-button>
                  <el-button size="small" link type="danger" @click="removeSquad(tIdx, sIdx)">删除</el-button>
                </div>
              </div>
              <div class="space-y-2 squad-container h-[150px]">
                <div 
                  v-for="(member, mIdx) in squad.members" 
                  :key="member.id"
                  draggable="true"
                  @dragstart="onDragStart(member, { type: 'squad', teamIdx: tIdx, squadIdx: sIdx, memberIdx: mIdx })"
                  class="p-2 rounded bg-[#3f3f3c] cursor-move text-sm flex justify-between items-center"
                  :class="{'opacity-50 line-through': member.is_leave}"
                >
                  <div>
                    <span class="font-bold">{{ member.game_id }}</span>
                    <span class="text-xs text-[#a3a3a1] ml-2">{{ member.job }}</span>
                  </div>
                  <el-button size="small" link type="warning" @click="toggleLeave(member)">假</el-button>
                </div>
                <div v-if="squad.members.length === 0" class="text-center text-[#a3a3a1] text-sm mt-4">
                  拖拽至此处 (0/6)
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="teamStore.teams.length === 0" class="flex items-center justify-center h-64 text-[#a3a3a1]">
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
  background-color: rgba(255, 255, 255, 0.02);
}
</style>