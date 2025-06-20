import { api } from './api'

export interface Zone {
  short_name: string
  long_name: string
  expansion_id: number
  expansion_name: string
}

export interface ZoneSearchParams {
  name?: string
}

export const zoneService = {
  // Search zones with various filters
  searchZones: async (params: ZoneSearchParams = {}): Promise<Zone[]> => {
    const response = await api.get<Zone[]>('/zones', params)
    return response.data
  },

  // Search zones by name
  searchZonesByName: async (name: string): Promise<Zone[]> => {
    const response = await api.get<Zone[]>('/zones', { name })
    return response.data
  }
} 