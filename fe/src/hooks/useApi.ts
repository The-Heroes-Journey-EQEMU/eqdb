import { useQuery, UseQueryOptions } from '@tanstack/react-query'
import { itemService, Item, ItemSearchParams } from '@/services/itemService'
import { spellService, Spell, SpellSearchParams } from '@/services/spellService'
import { npcService, NPC, NPCSearchParams } from '@/services/npcService'
import { zoneService, Zone, ZoneSearchParams } from '@/services/zoneService'
import { questService, Quest, QuestSearchParams } from '@/services/questService'
import { expansionService, Expansion } from '@/services/expansionService'

// Item hooks
export const useItems = (params: ItemSearchParams = {}, options?: Partial<UseQueryOptions<Item[], Error, Item[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['items', params],
    queryFn: () => itemService.searchItems(params),
    ...options,
  })
}

export const useItemById = (id: number, options?: Partial<UseQueryOptions<Item[], Error, Item[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['item', id],
    queryFn: () => itemService.getItemById(id),
    enabled: !!id,
    ...options,
  })
}

// Spell hooks
export const useSpells = (params: SpellSearchParams = {}, options?: Partial<UseQueryOptions<Spell[], Error, Spell[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['spells', params],
    queryFn: () => spellService.searchSpells(params),
    ...options,
  })
}

export const useSpellById = (id: number, options?: Partial<UseQueryOptions<Spell[], Error, Spell[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['spell', id],
    queryFn: () => spellService.getSpellById(id),
    enabled: !!id,
    ...options,
  })
}

// NPC hooks
export const useNPCs = (params: NPCSearchParams = {}, options?: Partial<UseQueryOptions<NPC[], Error, NPC[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['npcs', params],
    queryFn: () => npcService.searchNPCs(params),
    ...options,
  })
}

export const useNPCById = (id: number, options?: Partial<UseQueryOptions<NPC[], Error, NPC[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['npc', id],
    queryFn: () => npcService.getNPCById(id),
    enabled: !!id,
    ...options,
  })
}

// Zone hooks
export const useZones = (params: ZoneSearchParams = {}, options?: Partial<UseQueryOptions<Zone[], Error, Zone[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['zones', params],
    queryFn: () => zoneService.searchZones(params),
    ...options,
  })
}

// Quest hooks
export const useQuests = (params: QuestSearchParams = {}, options?: Partial<UseQueryOptions<Quest[], Error, Quest[], readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['quests', params],
    queryFn: () => questService.searchQuests(params),
    ...options,
  })
}

// Expansion hooks
export const useExpansions = (options?: Partial<UseQueryOptions<{ expansions: Expansion[] }, Error, { expansions: Expansion[] }, readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['expansions'],
    queryFn: () => expansionService.getAllExpansions(),
    ...options,
  })
}

export const useExpansionById = (id: number, options?: Partial<UseQueryOptions<Expansion, Error, Expansion, readonly unknown[]>>) => {
  return useQuery({
    queryKey: ['expansion', id],
    queryFn: () => expansionService.getExpansionById(id),
    enabled: !!id,
    ...options,
  })
} 