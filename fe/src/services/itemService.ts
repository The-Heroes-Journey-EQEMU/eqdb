import { api } from './api'

export interface Item {
  id: number
  name: string
  type: string
  serialized: string
}

export interface ItemSearchParams {
  id?: number
  name?: string
  type?: string
}

export const itemService = {
  // Search items with various filters
  searchItems: async (params: ItemSearchParams = {}): Promise<Item[]> => {
    const response = await api.get<Item[]>('/items', params)
    return response.data
  },

  // Get item by ID
  getItemById: async (id: number): Promise<Item[]> => {
    const response = await api.get<Item[]>('/items', { id })
    return response.data
  },

  // Search items by name
  searchItemsByName: async (name: string): Promise<Item[]> => {
    const response = await api.get<Item[]>('/items', { name })
    return response.data
  },

  // Get items by type
  getItemsByType: async (type: string): Promise<Item[]> => {
    const response = await api.get<Item[]>('/items', { type })
    return response.data
  }
} 