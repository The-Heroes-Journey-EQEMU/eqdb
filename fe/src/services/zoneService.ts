import { api } from './api';

export interface Zone {
  short_name: string;
  long_name: string;
  continent: string;
}

export interface ZoneSearchParams {
  name?: string;
}

export interface ZonesByExpansion {
  [expansion_name: string]: Zone[];
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
};
