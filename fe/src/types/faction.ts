import { NPC } from './npc'
import { Quest } from './quest'
import { Zone } from './zone'

export interface Faction {
  id: number;
  name: string;
  description?: string;
  base_value?: number;
}

export interface FactionSearchParams {
  id?: number;
  name?: string;
}

export interface FactionSearchResponse {
  factions: Faction[];
  total?: number;
  page?: number;
  per_page?: number;
}

export interface FactionDetail extends Faction {
  // Extended faction details
  npcs?: NPC[];
  quests?: Quest[];
  zones?: Zone[];
  modifiers?: FactionModifier[];
}

export interface FactionModifier {
  npc_id: number;
  npc_name: string;
  modifier: number;
  quest_name?: string;
}

export interface FactionStanding {
  faction_id: number;
  faction_name: string;
  standing: number;
  rank: string;
} 