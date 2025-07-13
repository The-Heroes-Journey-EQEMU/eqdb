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

export const zoneService = {
  searchZones: async (params: ZoneSearchParams): Promise<Zone[]> => {
    const response = await api.get<Zone[]>('/zones', { params });
    return response.data;
  },
  getZonesByExpansion: async (): Promise<ZonesByExpansion> => {
    const response = await api.get<ZonesByExpansion>('/zones');
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
};
