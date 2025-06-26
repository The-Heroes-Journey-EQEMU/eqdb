import { api } from './api'

export interface NPC {
  id: number
  name: string
  zone: string
  level: number
}

export interface NPCSearchParams {
  id?: number
  name?: string
  zone?: string
}

export const npcService = {
  // Search NPCs with various filters
  searchNPCs: async (params: NPCSearchParams = {}): Promise<NPC[]> => {
    const response = await api.get<NPC[]>('/npcs', params)
    return response.data
  },

  // Get NPC by ID
  getNPCById: async (id: number): Promise<NPC[]> => {
    const response = await api.get<NPC[]>('/npcs', { id })
    return response.data
  },

  // Search NPCs by name
  searchNPCsByName: async (name: string): Promise<NPC[]> => {
    const response = await api.get<NPC[]>('/npcs', { name })
    return response.data
  },

  // Get NPCs by zone
  getNPCsByZone: async (zone: string): Promise<NPC[]> => {
    const response = await api.get<NPC[]>('/npcs', { zone })
    return response.data
  }
} 