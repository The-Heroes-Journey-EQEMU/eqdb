import { api } from './api'

export interface Spell {
  id: number
  name: string
  class: string
  level: number
}

export interface SpellSearchParams {
  id?: number
  name?: string
  class?: string
}

export const spellService = {
  // Search spells with various filters
  searchSpells: async (params: SpellSearchParams = {}): Promise<Spell[]> => {
    const response = await api.get<Spell[]>('/spells', params)
    return response.data
  },

  // Get spell by ID
  getSpellById: async (id: number): Promise<Spell[]> => {
    const response = await api.get<Spell[]>('/spells', { id })
    return response.data
  },

  // Search spells by name
  searchSpellsByName: async (name: string): Promise<Spell[]> => {
    const response = await api.get<Spell[]>('/spells', { name })
    return response.data
  },

  // Get spells by class
  getSpellsByClass: async (spellClass: string): Promise<Spell[]> => {
    const response = await api.get<Spell[]>('/spells', { class: spellClass })
    return response.data
  }
} 