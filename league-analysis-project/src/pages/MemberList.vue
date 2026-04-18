<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useMemberStore } from '../stores/memberStore'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

const store = useMemberStore()
const search = ref('')

onMounted(() => {
  store.fetchMembers()
})

const dialogVisible = ref(false)
const formData = ref({
  job: '',
  game_id: '',
  sub_job: '',
  remark: '',
  attendance: 0
})

const openAddDialog = () => {
  formData.value = { job: '', game_id: '', sub_job: '', remark: '', attendance: 0 }
  dialogVisible.value = true
}

const saveMember = async () => {
  if (!formData.value.game_id || !formData.value.job) {
    ElMessage.error('职业和ID为必填项')
    return
  }
  await store.saveMember(formData.value)
  dialogVisible.value = false
  ElMessage.success('保存成功')
}

const selectedMembers = ref<string[]>([])
const handleSelectionChange = (val: any[]) => {
  selectedMembers.value = val.map(v => v.game_id)
}

const batchDelete = async () => {
  if (selectedMembers.value.length === 0) return
  await ElMessageBox.confirm('确定要删除选中的成员吗？', '提示', { type: 'warning' })
  await store.deleteMembers(selectedMembers.value)
  ElMessage.success('删除成功')
}

const fileInput = ref<HTMLInputElement | null>(null)
const importSide = ref('ally')

const triggerImport = (side: string) => {
  importSide.value = side
  fileInput.value?.click()
}

const onFileChange = async (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const file = target.files[0]
    try {
      const res = await store.importMembers(file, importSide.value)
      ElMessage.success(`成功导入 ${res.imported} 条${importSide.value === 'ally' ? '我方' : '敌方'}记录`)
    } catch (err) {
      ElMessage.error('导入失败')
    }
  }
  if (fileInput.value) fileInput.value.value = ''
}
</script>

<template>
  <div class="p-8 h-full flex flex-col bg-[#f5f5f7]">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-semibold text-gray-900 tracking-tight">帮众管理</h1>
      <div class="flex gap-4">
        <input type="file" ref="fileInput" class="hidden" accept=".csv" @change="onFileChange" />
        <el-dropdown @command="triggerImport">
          <el-button type="primary">
            导入 CSV<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="ally">导入我方人员</el-dropdown-item>
              <el-dropdown-item command="enemy">导入敌方人员</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        <el-button type="danger" plain @click="batchDelete" :disabled="selectedMembers.length === 0">批量删除</el-button>
        <el-button type="primary" plain @click="openAddDialog">新增成员</el-button>
      </div>
    </div>

    <div class="flex-1 overflow-hidden bg-white p-4 rounded-2xl shadow-sm border border-gray-100">
      <el-table
        :data="store.members"
        style="width: 100%; height: 100%;"
        v-loading="store.loading"
        @selection-change="handleSelectionChange"
        :header-cell-style="{ background: '#f9fafb', color: '#374151', fontWeight: '600' }"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="job" label="职业" width="120" />
        <el-table-column prop="game_id" label="ID" />
        <el-table-column prop="sub_job" label="副职" />
        <el-table-column prop="remark" label="备注" />
        <el-table-column prop="attendance" label="出勤次数" width="120" />
      </el-table>
    </div>

    <!-- 弹窗 -->
    <el-dialog v-model="dialogVisible" title="成员信息" width="30%">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="职业">
          <el-input v-model="formData.job" />
        </el-form-item>
        <el-form-item label="游戏ID">
          <el-input v-model="formData.game_id" />
        </el-form-item>
        <el-form-item label="副职">
          <el-input v-model="formData.sub_job" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" />
        </el-form-item>
        <el-form-item label="出勤次数">
          <el-input-number v-model="formData.attendance" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="saveMember">保存</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>
