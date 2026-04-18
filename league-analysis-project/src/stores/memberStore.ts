import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface Member {
  id: number
  job: string
  game_id: string
  sub_job: string | null
  remark: string | null
  attendance: number
}

export const useMemberStore = defineStore('member', () => {
  const members = ref<Member[]>([])
  const loading = ref(false)

  const fetchMembers = async () => {
    loading.value = true
    try {
      const res = await axios.get('/api/members')
      members.value = res.data
    } catch (error) {
      console.error('Failed to fetch members:', error)
    } finally {
      loading.value = false
    }
  }

  const saveMember = async (member: Omit<Member, 'id'>) => {
    try {
      await axios.post('/api/members', member)
      await fetchMembers()
    } catch (error) {
      console.error('Failed to save member:', error)
    }
  }

  const deleteMembers = async (game_ids: string[]) => {
    try {
      await axios.post('/api/members/delete-batch', game_ids)
      await fetchMembers()
    } catch (error) {
      console.error('Failed to delete members:', error)
    }
  }

  const importMembers = async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await axios.post('/api/members/import', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchMembers()
      return res.data
    } catch (error) {
      console.error('Failed to import members:', error)
      throw error
    }
  }

  return { members, loading, fetchMembers, saveMember, deleteMembers, importMembers }
})