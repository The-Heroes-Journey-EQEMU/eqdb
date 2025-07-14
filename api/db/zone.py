from sqlalchemy import text
import os
import logging
from api.db_manager import db_manager
from api.db.zone_settings import ZONE_LEVEL_CHART, continent_zones

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZoneDB:
    _zone_cache = None  # Class-level cache for shortname -> (zoneidnumber, long_name)
    _zone_cache_populated = False
    # ZONE_LEVEL_CHART and continent_zones are now imported from zone_settings.py

    def __init__(self):
        """Initialize the ZoneDB class."""
        pass

    def _populate_zone_cache(self):
        """Populate the in-memory cache for zone long names."""
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            query = text("SELECT short_name, zoneidnumber, long_name FROM zone")
            results = conn.execute(query).fetchall()
            ZoneDB._zone_cache = {row._mapping['short_name']: (row._mapping['zoneidnumber'], row._mapping['long_name']) for row in results}
            ZoneDB._zone_cache_populated = True
            logger.info(f"Zone cache populated with {len(ZoneDB._zone_cache)} entries.")

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

    def get_zone_long_name(self, shortname):
        """Get zone id and long name by shortname, using cache if available."""
        if ZoneDB._zone_cache is None or not ZoneDB._zone_cache_populated:
            logger.debug("Zone cache not populated, loading from database.")
            self._populate_zone_cache()
        if shortname in ZoneDB._zone_cache:
            logger.debug(f"Zone lookup for shortname {shortname} served from cache.")
            return ZoneDB._zone_cache[shortname]
        logger.warning(f"Zone shortname {shortname} not found in cache.")
        return None, "Unknown Zone"

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
                    z.zone_exp_multiplier
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

                zones_by_expansion[expansion_name].append({
                    'short_name': row_dict['short_name'],
                    'long_name': row_dict['long_name'],
                    'continent': continent,
                    'zone_exp_multiplier': row_dict['zone_exp_multiplier'],
                    'zone_level_range': ZONE_LEVEL_CHART.get(row_dict['short_name'], "N/A")
                })
            return zones_by_expansion
