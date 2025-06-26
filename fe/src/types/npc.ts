import { Spell } from './spell'
import { Quest } from './quest'

export interface NPC {
  id: number;
  name: string;
  zone?: string;
  level?: number;
  // Additional fields from the API
  race?: number;
  class?: number;
  faction_id?: number;
  hp?: number;
  mana?: number;
  ac?: number;
  attack?: number;
  defense?: number;
}

export interface NPCSearchParams {
  id?: number;
  name?: string;
  zone?: string;
  level_min?: number;
  level_max?: number;
  race?: number;
  class?: number;
}

export interface NPCSearchResponse {
  npcs: NPC[];
  total?: number;
  page?: number;
  per_page?: number;
}

export interface NPCDetail extends NPC {
  // Extended NPC details
  zone_long_name?: string;
  expansion?: string;
  drops?: ItemDrop[];
  spells?: Spell[];
  quests?: Quest[];
  faction_standing?: Record<string, number>;
}

export interface ItemDrop {
  item_id: number;
  item_name: string;
  drop_rate?: number;
  quest_item?: boolean;
} 