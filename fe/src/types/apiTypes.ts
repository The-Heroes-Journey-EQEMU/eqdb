export interface ItemType {
  items_tab: string[];
  weapons_tab?: {
    Weapons: { [key: string]: string };
    'Held Items': { [key: string]: string };
  };
  armor_tab?: {
    Armor: { [key: string]: string };
  };
}

export interface ItemSlot {
  General: { [key: string]: string };
  Armor: { [key: string]: string };
}
