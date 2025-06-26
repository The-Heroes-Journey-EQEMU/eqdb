import { api } from './api'

export interface Expansion {
  id: number
  name: string
  short_name: string
  release_date: string
  description: string
}

export interface ExpansionSummary {
  expansion_id: number
  regular: number
  tradeskill: number
  special: number
  custom: number
  total: number
}

export const expansionService = {
  // Get all expansions
  getAllExpansions: async (): Promise<{ expansions: Expansion[] }> => {
    const response = await api.get<{ expansions: Expansion[] }>('/expansions')
    return response.data
  },

  // Get expansion by ID
  getExpansionById: async (id: number): Promise<Expansion> => {
    const response = await api.get<Expansion>(`/expansions/${id}`)
    return response.data
  },

  // Search expansions by name
  searchExpansionsByName: async (name: string): Promise<Expansion> => {
    const response = await api.get<Expansion>('/expansions/search', { name })
    return response.data
  },

  // Get zones by expansion
  getZonesByExpansion: async (expansionId: number): Promise<{ zones: any[] }> => {
    const response = await api.get<{ zones: any[] }>(`/expansions/${expansionId}/zones`)
    return response.data
  },

  // Get expansion items summary
  getExpansionItemsSummary: async (): Promise<{ summaries: ExpansionSummary[] }> => {
    const response = await api.get<{ summaries: ExpansionSummary[] }>('/expansion-items/summary')
    return response.data
  }
} 