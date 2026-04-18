import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

export interface TeamMember {
  id: string
  game_id: string
  job: string
  is_sub?: boolean
  is_leave?: boolean
  sub_members?: TeamMember[] // for the "替补" feature
}

export interface Squad {
  id: string
  name: string
  members: TeamMember[]
}

export interface Team {
  id: string
  name: string
  squads: Squad[]
}

export const useTeamStore = defineStore('team', () => {
  // state
  const teams = ref<Team[]>([])

  const saveToDB = async (name: string) => {
    try {
      const payload = {
        name,
        layout_data: teams.value
      }
      await axios.post('/api/teams', payload)
    } catch (e) {
      console.error(e)
    }
  }

  return { teams, saveToDB }
}, {
  persist: true
})