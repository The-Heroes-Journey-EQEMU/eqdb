export interface Item {
  id: number;
  name: string;
  type?: string;
  serialized?: string;
  // Additional fields from the API
  itemtype?: number;
  classes?: number;
  slots?: number;
  is_quest_item?: boolean;
  expansion?: string;
}

export interface ItemSearchParams {
  id?: number;
  name?: string;
  type?: string;
}

export interface ItemSearchResponse {
  items: Item[];
  total?: number;
  page?: number;
  per_page?: number;
}

export interface ItemDetail extends Item {
  // Extended item details
  stats?: Record<string, any>;
  effects?: string[];
  requirements?: Record<string, any>;
  drops?: NPCDrop[];
  recipes?: ItemRecipe[];
}

export interface NPCDrop {
  npc_id: number;
  npc_name: string;
  zone_name: string;
  drop_rate?: number;
}

export interface ItemRecipe {
  id: number;
  name: string;
  tradeskill: number;
  tradeskill_name: string;
  skillneeded: number;
  trivial: number;
  components: ItemComponent[];
  success_items: ItemComponent[];
  fail_items: ItemComponent[];
}

export interface ItemComponent {
  item_id: number;
  item_name: string;
  count: number;
} 