export interface User {
  id: string;
  username: string;
  avatar?: string;
  email?: string;
  created_at: string;
  updated_at: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  items_per_page: number;
  default_search_type: 'items' | 'spells' | 'npcs' | 'zones';
  show_tooltips: boolean;
  auto_save_searches: boolean;
}

export interface GearList {
  id: number;
  name: string;
  description?: string;
  items: GearListItem[];
  created_at: string;
  updated_at: string;
}

export interface GearListItem {
  item_id: number;
  item_name: string;
  slot: string;
  priority: number;
}

export interface RestrictSet {
  id: number;
  name: string;
  description?: string;
  restrictions: Restriction[];
  created_at: string;
  updated_at: string;
}

export interface Restriction {
  item_id: number;
  item_name: string;
  restriction_type: 'exclude' | 'include' | 'max_count';
  value?: number;
}

export interface WeightSet {
  id: number;
  name: string;
  description?: string;
  weights: Weight[];
  created_at: string;
  updated_at: string;
}

export interface Weight {
  stat_name: string;
  weight: number;
  description?: string;
} 