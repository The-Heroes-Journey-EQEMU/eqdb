export interface Spell {
  id: number;
  name: string;
  class?: string;
  level?: number;
  // Additional fields from the API
  classes?: number;
  level_required?: number;
  mana_cost?: number;
  cast_time?: number;
  range?: number;
  duration?: number;
  effects?: string[];
}

export interface SpellSearchParams {
  id?: number;
  name?: string;
  class?: string;
  level_min?: number;
  level_max?: number;
}

export interface SpellSearchResponse {
  spells: Spell[];
  total?: number;
  page?: number;
  per_page?: number;
}

export interface SpellDetail extends Spell {
  // Extended spell details
  description?: string;
  target_type?: string;
  resist_type?: string;
  effect_description?: string;
  components?: string[];
  skill?: string;
} 