import { api } from './api'

export interface Quest {
  npc_id: number
  npc_name: string
  quest_name: string
  level: number
  zone_name: string
  zone_long_name: string
  zone_expansion: number
  item_id: number
  item_name: string
  itemtype: number
  classes: number
  slots: number
  is_quest_item: boolean
  expansion: string
}

export interface QuestSearchParams {
  name?: string
  npc_name?: string
  item_id?: number
  item_name?: string
  min_level?: number
  max_level?: number
  zone?: string
  expansion?: number
}

export const questService = {
  // Search quests with various filters
  searchQuests: async (params: QuestSearchParams = {}): Promise<Quest[]> => {
    const response = await api.get<Quest[]>('/quests', params)
    return response.data
  },

  // Search quests by name
  searchQuestsByName: async (name: string): Promise<Quest[]> => {
    const response = await api.get<Quest[]>('/quests', { name })
    return response.data
  },

  // Search quests by NPC name
  searchQuestsByNPC: async (npcName: string): Promise<Quest[]> => {
    const response = await api.get<Quest[]>('/quests', { npc_name: npcName })
    return response.data
  },

  // Get quests by item ID
  getQuestsByItemId: async (itemId: number): Promise<Quest[]> => {
    const response = await api.get<Quest[]>('/quests', { item_id: itemId })
    return response.data
  },

  // Get quests by zone
  getQuestsByZone: async (zone: string): Promise<Quest[]> => {
    const response = await api.get<Quest[]>('/quests', { zone })
    return response.data
  },

  // Get quests by expansion
  getQuestsByExpansion: async (expansion: number): Promise<Quest[]> => {
    const response = await api.get<Quest[]>('/quests', { expansion })
    return response.data
  }
} 