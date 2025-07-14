import { api } from './api';

export interface Zone {
  short_name: string;
  long_name: string;
  continent: string;
  expansion_name?: string;
  mapping?: { x1: number; y1: number; x2: number; y2: number; z1: number; z2: number; rgb: string }[];
  waypoint?: { x: number; y: number; z: number };
  safe_x?: number;
  safe_y?: number;
  safe_z?: number;
  zone_exp_multiplier?: number;
  zone_level_range?: string;
}

export interface ZoneSearchParams {
  name?: string;
}

export interface ZonesByExpansion {
  [expansion_name: string]: Zone[];
}

export interface ZoneDetails {
  zoneidnumber: number;
  expansion: string;
  short_name: string;
  canbind: number;
  canlevitate: number;
  castoutdoor: number;
  zone_level_range: string;
  zone_exp_multiplier: number;
  safe_x: number;
  safe_y: number;
  safe_z: number;
  newbie_zone: boolean;
  waypoint_x: number;
  waypoint_y: number;
  waypoint_z: number;
}

export interface ConnectedZone {
  target_zone_id: number;
  short_name: string;
  long_name: string;
}

interface Waypoint {
    x: number;
    y: number;
    z: number;
}

interface ZoneData {
    id: number;
    short_name: string;
    waypoint: Waypoint;
}

interface ContinentData {
    [zoneName: string]: ZoneData;
}

interface WaypointsByContinent {
    [continentName: string]: ContinentData;
}

export interface ZoneNPC {
  id: number;
  name: string;
  level: number;
  race: string;
  class: string;
  hp: number;
  mindmg: number;
  maxdmg: number;
  attackspeed: number;
  special_abilities: string;
  aggroradius: number;
  npcspecialattks: string;
  zone_name: string;
  zone_long_name: string;
}

export interface ZoneItem {
  id: number;
  name: string;
  itemtype: number;
  itemclass: number;
  weight: number;
  size: number;
  slots: number;
  price: number;
  icon: number;
  lore: string;
  nodrop: number;
  norent: number;
  magic: number;
  races: number;
  classes: number;
  ac: number;
  hp: number;
  mana: number;
  damage: number;
  delay: number;
  drop_count: number;
}

export const zoneService = {
  searchZones: async (params: ZoneSearchParams): Promise<Zone[]> => {
    const response = await api.get<Zone[]>('/zones', { params });
    return response.data;
  },
  getZonesByExpansion: async (): Promise<ZonesByExpansion> => {
    const response = await api.get<ZonesByExpansion>('/zones', {
      params: {
        // cache bust
        t: new Date().getTime(),
      }
    });
    return response.data;
  },
  getZonesWithWaypoints: async (): Promise<WaypointsByContinent> => {
    const response = await api.get<WaypointsByContinent>('/zones/waypoints');
    return response.data;
  },
  getZoneByIdentifier: async (identifier: string): Promise<Zone> => {
    const response = await api.get<Zone>(`/zones/${identifier}`);
    return response.data;
  },
  getZoneDetails: async (shortName: string): Promise<ZoneDetails> => {
    const response = await api.get<ZoneDetails>(`/zones/${shortName}/details`);
    return response.data;
  },
  getConnectedZones: async (shortName: string): Promise<ConnectedZone[]> => {
    const response = await api.get<ConnectedZone[]>(`/zones/${shortName}/connected`);
    return response.data;
  },
  getZoneNPCs: async (shortName: string): Promise<ZoneNPC[]> => {
    const response = await api.get<ZoneNPC[]>(`/zones/${shortName}/npcs`);
    return response.data;
  },
  getZoneItems: async (shortName: string): Promise<ZoneItem[]> => {
    const response = await api.get<ZoneItem[]>(`/zones/${shortName}/items`);
    return response.data;
  },
};
