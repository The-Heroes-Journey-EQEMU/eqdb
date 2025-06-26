export interface Tradeskill {
  id: number;
  name: string;
  skill: string;
  recipe_count: number;
}

export interface TradeskillSearchParams {
  id?: number;
  name?: string;
  skill?: string;
}

export interface TradeskillSearchResponse {
  tradeskills: Tradeskill[];
  total?: number;
  page?: number;
  per_page?: number;
}

export interface TradeskillDetail extends Tradeskill {
  // Extended tradeskill details
  description?: string;
  recipes?: Recipe[];
  skill_levels?: SkillLevel[];
}

export interface Recipe {
  id: number;
  name: string;
  tradeskill: number;
  tradeskill_name: string;
  skillneeded: number;
  trivial: number;
  nofail: number;
  replace_container: number;
  must_learn: number;
  enabled: number;
  min_expansion: number;
  components: ComponentItem[];
  success_items: ComponentItem[];
  fail_items: ComponentItem[];
}

export interface ComponentItem {
  item_id: number;
  item_name: string;
  count: number;
}

export interface SkillLevel {
  level: number;
  description: string;
  recipes_available: number;
} 