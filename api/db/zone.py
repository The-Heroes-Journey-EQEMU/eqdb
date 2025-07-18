from sqlalchemy import text
import os
import logging
from api.db_manager import db_manager
from api.db.zone_settings import ZONE_LEVEL_CHART, continent_zones
from api.db.npc import NPCDB
from api.cache import cache_results

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZoneDB:
    # ZONE_LEVEL_CHART and continent_zones are now imported from zone_settings.py

    def __init__(self):
        """Initialize the ZoneDB class."""
        pass

    def get_zone_raw_data(self, zone_id=None, name=None):
        """Get raw zone data from the database"""
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            if zone_id:
                query = text("""
                    SELECT * FROM zone 
                    WHERE zoneidnumber = :zone_id
                """)
                result = conn.execute(query, {"zone_id": zone_id}).fetchone()
                if result:
                    data = dict(result._mapping)
                    logger.debug(f"Retrieved zone data for ID {zone_id}: {data}")
                    return data
                return None
            elif name:
                query = text("""
                    SELECT * FROM zone 
                    WHERE zoneidnumber = :name 
                    OR short_name LIKE :name
                    OR long_name LIKE :name
                    LIMIT 50
                """)
                results = conn.execute(query, {"name": f"%{name}%"}).fetchall()
                data = [dict(row._mapping) for row in results]
                logger.debug(f"Retrieved {len(data)} zones with name {name}: {data}")
                return data
            return None

    def get_map_data(self, short_name):
        """Get map data for a given zone short_name."""
        lines = []
        if short_name == 'Unknown':
            return lines
        
        # Determine the base directory of the script
        here = os.path.dirname(os.path.abspath(__file__))
        # Go up two levels to the project root
        project_root = os.path.dirname(os.path.dirname(here))
        
        # Check for the map file in both the root maps directory and subdirectories
        possible_paths = [
            os.path.join(project_root, 'maps', f'{short_name}.txt'),
            os.path.join(project_root, 'maps', 'brewall', f'{short_name}.txt')
        ]
        
        map_file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                map_file_path = path
                break

        if not map_file_path:
            logger.warning(f"Map file not found for zone: {short_name}")
            return lines

        with open(map_file_path, 'r') as fh:
            data = fh.read()
            for line in data.split('\n'):
                if line.startswith('L'):
                    try:
                        split_line = line.split()
                        lines.append({'x1': float(split_line[1].strip(',')),
                                      'y1': float(split_line[2].strip(',')),
                                      'z1': float(split_line[3].strip(',')),
                                      'x2': float(split_line[4].strip(',')),
                                      'y2': float(split_line[5].strip(',')),
                                      'z2': float(split_line[6].strip(',')),
                                      'rgb': f'{split_line[7].strip(",")}, {split_line[8].strip(",")}, {split_line[9].strip(",")}'})
                    except (IndexError, ValueError) as e:
                        logger.error(f"Could not parse line '{line}' in {short_name}.txt: {e}")
        return lines

    def get_zone_by_identifier(self, identifier):
        """Get a single zone by its ID or short_name."""
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            # Check if identifier is an integer (ID) or string (short_name)
            try:
                zone_id = int(identifier)
                query = text("SELECT * FROM zone WHERE zoneidnumber = :identifier")
                result = conn.execute(query, {"identifier": zone_id}).fetchone()
            except ValueError:
                query = text("SELECT * FROM zone WHERE short_name = :identifier")
                result = conn.execute(query, {"identifier": identifier}).fetchone()

            if result:
                zone_data = dict(result._mapping)
                zone_data['mapping'] = self.get_map_data(zone_data['short_name'])
                zone_data['waypoint'] = self.get_zone_waypoint(zone_data['short_name'])
                return zone_data
            return None

    @cache_results(ttl=86400)
    def get_connected_zones(self, short_name):
        """Get all connected zones for a given short_name, excluding those in the exclusion list."""
        from api.utils import get_exclusion_list
        
        exclusion_list = get_exclusion_list('zone')
        engine = db_manager.get_engine_for_table('zone_points')
        
        with engine.connect() as conn:
            # First, get the distinct target_zone_ids from zone_points
            query_ids = text("""
                SELECT DISTINCT zp.target_zone_id
                FROM zone_points zp
                JOIN zone z ON zp.target_zone_id = z.zoneidnumber
                WHERE zp.zone = :short_name
                AND z.short_name NOT IN :exclusion_list
            """)
            target_ids_results = conn.execute(
                query_ids, 
                {"short_name": short_name, "exclusion_list": tuple(exclusion_list)}
            ).fetchall()
            
            if not target_ids_results:
                return []

            target_ids = [row._mapping['target_zone_id'] for row in target_ids_results]

            # Now, get the zone details for those IDs
            engine_zone = db_manager.get_engine_for_table('zone')
            with engine_zone.connect() as conn_zone:
                query_zones = text("""
                    SELECT DISTINCT
                        zoneidnumber as target_zone_id,
                        short_name,
                        long_name
                    FROM
                        zone
                    WHERE
                        zoneidnumber IN :target_ids
                """)
                results = conn_zone.execute(query_zones, {"target_ids": tuple(target_ids)}).fetchall()
                # Filter out the current zone from the results
                return [dict(row._mapping) for row in results if row._mapping['short_name'] != short_name]

    @cache_results(ttl=86400)
    def get_zone_details_by_short_name(self, short_name):
        """Get extended zone details by short_name."""
        from api.db.expansion import ExpansionDB
        
        engine = db_manager.get_engine_for_table('zone')
        expansion_db = ExpansionDB(engine.url)

        with engine.connect() as conn:
            query = text("""
                SELECT
                    zoneidnumber,
                    expansion,
                    short_name,
                    canbind,
                    canlevitate,
                    castoutdoor,
                    zone_exp_multiplier,
                    safe_x,
                    safe_y,
                    safe_z
                FROM
                    zone
                WHERE
                    short_name = :short_name
            """)
            result = conn.execute(query, {"short_name": short_name}).fetchone()
            if result:
                zone_data = dict(result._mapping)
                
                # Get expansion name from ExpansionDB
                expansion_info = expansion_db.get_expansion_by_id(zone_data['expansion'])
                zone_data['expansion'] = expansion_info['name'] if expansion_info else 'Unknown'
                zone_data['zone_level_range'] = ZONE_LEVEL_CHART.get(short_name, "N/A")
                waypoint = self.get_zone_waypoint(short_name)
                zone_data['waypoint_x'] = waypoint.get('x')
                zone_data['waypoint_y'] = waypoint.get('y')
                zone_data['waypoint_z'] = waypoint.get('z')
                # Simple logic for newbie zones, can be expanded
                zone_data['newbie_zone'] = zone_data['zoneidnumber'] in [1, 2, 10, 19, 22, 24, 25, 29, 30, 34, 35, 40, 41, 42, 45, 46, 47, 52, 54, 55, 68]
                return zone_data
            return None

    @cache_results(ttl=86400)  # Cache for 24 hours
    def get_zone_long_name(self, shortname):
        """Get zone id and long name by shortname, using Redis cache."""
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            query = text("SELECT zoneidnumber, long_name FROM zone WHERE short_name = :shortname")
            result = conn.execute(query, {"shortname": shortname}).fetchone()
            if result:
                return result._mapping['zoneidnumber'], result._mapping['long_name']
        return None, "Unknown Zone"

    @cache_results(ttl=86400)
    def get_zone_waypoint(self, short_name):
        """Fetch waypoint for a given zone short_name from thj_waypoints."""
        engine = db_manager.get_engine_for_table('thj_waypoints')
        with engine.connect() as conn:
            query = text("""
                SELECT x, y, z, heading FROM thj_waypoints WHERE shortname = :short_name LIMIT 1
            """)
            result = conn.execute(query, {"short_name": short_name}).fetchone()
            if result:
                return {
                    'x': result._mapping['x'],
                    'y': result._mapping['y'],
                    'z': result._mapping['z'],
                    'heading': result._mapping['heading']
                }
            return {}

    def waypoint_listing(self):
        """Get a list of zones that have waypoints, grouped by continent/category (id <= 6)."""
        engine = db_manager.get_engine_for_table('thj_waypoints')
        with engine.connect() as conn:
            query = text("""
                SELECT w.shortname, w.long_name, w.x, w.y, w.z, w.heading, w.id as waypoint_id, w.category, c.name as category_name
                FROM thj_waypoints w
                JOIN thj_waypoints_categories c ON w.category = c.id
                WHERE c.id <= 6
                ORDER BY c.id, w.long_name
            """)
            results = conn.execute(query).fetchall()

            waypoints_by_continent = {}
            for row in results:
                continent = row._mapping['category_name']
                if continent not in waypoints_by_continent:
                    waypoints_by_continent[continent] = {}
                waypoints_by_continent[continent][row._mapping['long_name']] = {
                    'id': row._mapping['waypoint_id'],
                    'short_name': row._mapping['shortname'],
                    'waypoint': {
                        'x': row._mapping['x'],
                        'y': row._mapping['y'],
                        'z': row._mapping['z'],
                        'heading': row._mapping['heading']
                    },
                    'waypoint_name': row._mapping['long_name']
                }
            return waypoints_by_continent

    @cache_results(ttl=86400)
    def get_all_zones_by_expansion(self):
        """Get all zones grouped by expansion."""
        from api.db.expansion import ExpansionDB
        from api.utils import get_exclusion_list
        
        exclusion_list = get_exclusion_list('zone')
        engine = db_manager.get_engine_for_table('zone')
        expansion_db = ExpansionDB(engine.url)
        expansions = expansion_db.get_all_expansions()
        
        with engine.connect() as conn:
            query = text("""
                SELECT
                    z.expansion,
                    z.short_name,
                    z.long_name,
                    z.zone_exp_multiplier,
                    z.min_level,
                    z.max_level
                FROM
                    zone z
                WHERE
                    z.expansion <= 5
                ORDER BY
                    z.expansion, z.long_name;
            """)
            results = conn.execute(query).fetchall()
            
            zones_by_expansion = {}
            for row in results:
                row_dict = dict(row._mapping)
                if row_dict['short_name'] in exclusion_list:
                    continue
                
                expansion_id = row_dict['expansion']
                
                expansion_name = "Unknown"
                for exp in expansions:
                    if exp['id'] == expansion_id:
                        expansion_name = exp['name']
                        break
                
                if expansion_name not in zones_by_expansion:
                    zones_by_expansion[expansion_name] = []
                
                continent = 'Unknown'
                for c, zones in continent_zones.items():
                    if row_dict['short_name'] in zones:
                        continent = c
                        break

                level_range_str = ZONE_LEVEL_CHART.get(row_dict['short_name'])
                min_level = None
                max_level = None
                if level_range_str and '-' in level_range_str:
                    try:
                        min_level_str, max_level_str = level_range_str.split('-')
                        min_level = int(min_level_str.strip())
                        max_level = int(max_level_str.strip())
                    except ValueError:
                        logger.warning(f"Could not parse level range '{level_range_str}' for zone {row_dict['short_name']}.")
                        pass # Keep as None if parsing fails
                
                if min_level is None or max_level is None:
                    logger.warning(f"Zone '{row_dict['long_name']}' ({row_dict['short_name']}) is missing a valid level range.")

                zones_by_expansion[expansion_name].append({
                    'short_name': row_dict['short_name'],
                    'long_name': row_dict['long_name'],
                    'continent': continent,
                    'zone_exp_multiplier': row_dict['zone_exp_multiplier'],
                    'min_level': min_level,
                    'max_level': max_level,
                    'zone_level_range': level_range_str,
                    'expansion_id': expansion_id,
                    'expansion_name': expansion_name
                })
            return zones_by_expansion

    @cache_results(ttl=86400)
    def get_zone_spawns_by_short_name(self, short_name):
        """Get spawn data for a given zone short_name."""
        npc_db = NPCDB()
        engine = db_manager.get_engine_for_table('spawn2')
        with engine.connect() as conn:
            query = text("""
                SELECT
                    s2.x,
                    s2.y,
                    s2.z,
                    s2.respawntime,
                    sg.name as spawngroup_name,
                    nt.name as npc_name,
                    nt.id as npc_id,
                    nt.level as npc_level,
                    nt.race as npc_race,
                    nt.hp as npc_hp,
                    se.chance,
                    s2.id as spawn2_id,
                    s2.spawngroupID
                FROM
                    spawn2 s2
                JOIN
                    spawngroup sg ON s2.spawngroupID = sg.id
                JOIN
                    spawnentry se ON s2.spawngroupID = se.spawngroupID
                JOIN
                    npc_types nt ON se.npcID = nt.id
                WHERE
                    s2.zone = :short_name
                ORDER BY
                    sg.name, s2.id;
            """)
            results = conn.execute(query, {"short_name": short_name}).fetchall()

            spawn_groups = {}
            for row in results:
                row_dict = dict(row._mapping)
                # Use a combination of spawngroup_name and spawn2_id for a unique key
                spawn_key = f"{row_dict['spawngroup_name']}_{row_dict['spawn2_id']}"

                if spawn_key not in spawn_groups:
                    spawn_groups[spawn_key] = {
                        'x': row_dict['x'],
                        'y': row_dict['y'],
                        'z': row_dict['z'],
                        'respawn': row_dict['respawntime'],
                        'spawngroup_name': row_dict['spawngroup_name'],
                        'npcs': []
                    }

                race_id = row_dict['npc_race']
                race_name = npc_db.get_race_name(race_id)

                spawn_groups[spawn_key]['npcs'].append({
                    'npc_name': row_dict['npc_name'],
                    'npc_id': row_dict['npc_id'],
                    'npc_level': row_dict['npc_level'],
                    'npc_race': race_name,
                    'npc_hp': row_dict['npc_hp'],
                    'chance': row_dict['chance'],
                    'spawn2_id': row_dict['spawn2_id']
                })

            # Convert the dictionary to a list of values for the final output
            return list(spawn_groups.values())
