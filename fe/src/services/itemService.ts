import { api } from './api'
import { ItemType, ItemSlot } from '@/types/apiTypes'

export interface Item {
  id: number
  name: string
  type: string
  serialized: string
}

export interface ItemSearchResponse {
  results: Item[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ItemSearchParams {
  id?: number;
  name?: string;
  tradeskill_only?: boolean;
  equippable_only?: boolean;
  exclude_glamours?: boolean;
  only_augments?: boolean;
  item_type?: string;
  item_slot?: string;
}

export const itemService = {
  // Search items with various filters
  searchItems: async (params: ItemSearchParams = {}): Promise<ItemSearchResponse> => {
    const response = await api.get<ItemSearchResponse>('/items', params)
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
  },

  // Get all item types
  getItemTypes: async (): Promise<ItemType> => {
    const response = await api.get<ItemType>('/items/types')
    return response.data
  },

  // Get all item slots
  getItemSlots: async (): Promise<ItemSlot> => {
    const response = await api.get<ItemSlot>('/items/slots')
    return response.data
  }
}
