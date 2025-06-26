import { NPC } from './npc'
import { Item } from './item'

export interface Zone {
  short_name: string;
  long_name: string;
  expansion_id: number;
  expansion_name: string;
  // Additional fields from the API
  safe_x?: number;
  safe_y?: number;
  safe_z?: number;
  safe_heading?: number;
  min_level?: number;
  max_level?: number;
}

export interface ZoneSearchParams {
  name?: string;
  expansion_id?: number;
  min_level?: number;
  max_level?: number;
}

export interface ZoneSearchResponse {
  zones: Zone[];
  total?: number;
  page?: number;
  per_page?: number;
}

export interface ZoneDetail extends Zone {
  // Extended zone details
  description?: string;
  npcs?: NPC[];
  items?: Item[];
  waypoints?: Waypoint[];
  connections?: ZoneConnection[];
}

export interface Waypoint {
  id: number;
  name: string;
  x: number;
  y: number;
  z: number;
  heading: number;
  description?: string;
}

export interface ZoneConnection {
  zone_short_name: string;
  zone_long_name: string;
  x: number;
  y: number;
  z: number;
  heading: number;
} 