export interface Quest {
  npc_id: number;
  npc_name: string;
  quest_name: string;
  level: number;
  zone_name: string;
  zone_long_name: string;
  zone_expansion: number;
  item_id: number;
  item_name: string;
  itemtype: number;
  classes: number;
  slots: number;
  is_quest_item: boolean;
  expansion: string;
}

export interface QuestSearchParams {
  name?: string;
  npc_name?: string;
  item_id?: number;
  item_name?: string;
  min_level?: number;
  max_level?: number;
  zone?: string;
  expansion?: number;
}

export interface QuestSearchResponse {
  quests: Quest[];
  total?: number;
  page?: number;
  per_page?: number;
}

export interface QuestDetail extends Quest {
  // Extended quest details
  description?: string;
  requirements?: QuestRequirement[];
  rewards?: QuestReward[];
  steps?: QuestStep[];
  related_quests?: Quest[];
}

export interface QuestRequirement {
  type: 'level' | 'faction' | 'item' | 'skill' | 'class' | 'race';
  value: string | number;
  description: string;
}

export interface QuestReward {
  type: 'item' | 'experience' | 'faction' | 'money' | 'skill';
  value: string | number;
  description: string;
}

export interface QuestStep {
  step_number: number;
  description: string;
  location?: string;
  npc_name?: string;
  item_name?: string;
} 