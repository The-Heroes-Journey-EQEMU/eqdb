from sqlalchemy import text
import os
import logging
from api.db_manager import db_manager

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ZoneDB:
    _zone_cache = None  # Class-level cache for shortname -> (zoneidnumber, long_name)
    _zone_cache_populated = False
    ZONE_LEVEL_CHART = {
        'abysmal': '1 - 65',
        'acrylia': '50 - 60',
        'airplane': '50 - 60',
        'akanon': '1 - 10',
        'akheva': '55 - 60',
        'arcstone': '65 - 75',
        'bazaar': '1 - 65',
        'befallen': '5 - 20',
        'beholder': '35 - 40',
        'blackburrow': '5 - 15',
        'bloodfields': '60 - 65',
        'buriedsea': '65 - 75',
        'burningwood': '50 - 60',
        'butcher': '1 - 20',
        'cabeast': '1 - 75',
        'cabwest': '1- 75',
        'cauldron': '15 - 25',
        'cazicthule': '40 - 60',
        'charasis': '50 - 60',
        'chardok': '50 - 60',
        'citymist': '45 - 55',
        'commons': '10 - 50',
        'corathus': '50 - 65',
        'cragstone': '20 - 30',
        'crescent': '1 - 20',
        'crushbone': '5 - 15',
        'cryptofshade': '65 - 70',
        'dalnir': '35 - 45',
        'devastation': '65 - 75',
        'dragonlair': '60 - 65',
        'dragonscale': '70 - 80',
        'dranik': '60 - 65',
        'draniksscar': '60 - 65',
        'dreadlands': '45 - 60',
        'droga': '35 - 50',
        'drowned': '50 - 65',
        'eastkarana': '15 - 25',
        'eastwastes': '35 - 50',
        'ecommons': '5 - 15',
        'emeraldjungle': '45 - 55',
        'erudnext': '1 - 10',
        'erudnint': '1 - 10',
        'erudsxing': '10 - 20',
        'everfrost': '1 - 10',
        'fearplane': '50 - 60',
        'feerrott': '1 - 10',
        'felwithea': '1 - 10',
        'fieldofbone': '1 - 20',
        'firiona': '30 - 40',
        'freporte': '1 - 10',
        'freportw': '1 - 10',
        'frontiermtns': '35 - 45',
        'frozenshadow': '30 - 50',
        'fungusgrove': '50 - 60',
        'gfaydark': '1 - 15',
        'griegsend': '55 - 60',
        'grobb': '1-75',
        'growthplane': '50 - 60',
        'halas': '1 - 10',
        'harbingers': '60 - 65',
        'hateplaneb': '50 - 60',
        'highkeep': '20 - 30',
        'highpass': '10-20',
        'hohonora': '60 - 65',
        'hohonorb': '60 - 65',
        'hole': '45 - 60',
        'iceclad': '25 - 40',
        'innothule': '5 - 15',
        'kael': '50 - 60',
        'kaladima': '1 - 10',
        'kaladimb': '1 - 10',
        'karnor': '45 - 60',
        'kedge': '45 - 55',
        'kelethin': '1 - 10',
        'kerraridge': '10 - 20',
        'kithicor': '10 - 50',
        'lakeofillomen': '15 - 30',
        'lakerathe': '10 - 25',
        'lavastorm': '5 - 15',
        'lfaydark': '10 - 25',
        'maiden': '50 - 60',
        'mesa': '35 - 55',
        'mischiefplane': '50 - 60',
        'misty': '1 - 10',
        'moors': '30 - 45',
        'mseru': '35 - 50',
        'najena': '15 - 25',
        'nektulos': '5 - 15',
        'neriaka': '1 - 10',
        'neriakb': '1 - 10',
        'neriakc': '1 - 10',
        'netherbian': '30 - 45',
        'northkarana': '10 - 20',
        'nro': '5 - 15',
        'oggok': '1 - 10',
        'oldhighpass': '10 - 20',
        'oldkurn': '10 - 25',
        'oot': '10 - 20',
        'overthere': '25 - 40',
        'paineel': '1 - 10',
        'paludal': '15 - 30',
        'paw': '30 - 40',
        'poair': '65 - 70',
        'podisease': '50 - 60',
        'poearthb': '65 - 70',
        'pofire': '65 - 70',
        'poinnovation': '50 - 60',
        'pojustice': '45 - 55',
        'poknowledge': '1 - 65',
        'ponightmare': '50 - 60',
        'postorms': '55 - 65',
        'potactics': '60 - 65',
        'potimeb': '65 - 70',
        'potorment': '60 - 65',
        'potranquility': '1 - 65',
        'povalor': '55 - 65',
        'powater': '65 - 70',
        'provinggrounds': '60 - 65',
        'qcat': '5 - 15',
        'qey2hh1': '10 - 20',
        'qeynos': '1 - 10',
        'qeynos2': '1 - 10',
        'qeytoqrg': '1 - 10',
        'qrg': '1 - 10',
        'rathemtn': '15 - 30',
        'riftseekers': '65 - 70',
        'rivervale': '1 - 10',
        'scarlet': '35 - 50',
        'sebilis': '55 - 60',
        'sirens': '50 - 60',
        'skyfire': '50 - 60',
        'sleeper': '60 - 65',
        'soldunga': '20 - 30',
        'soldungb': '40 - 60',        
        'soltemple': '35 - 45',
        'southkarana': '20 - 30',
        'sro': '15 - 25',
        'sseru': '45 - 55',
        'ssratemple': '55 - 60',
        'steamfactory': '70 - 80',
        'steamfont': '1 - 15',
        'steamfontmts': '1 - 15',
        'steppes': '70 - 80',
        'swampofnohope': '20 - 35',
        'templeveeshan': '60 - 65',
        'tenebrous': '25 - 40',
        'thedeep': '45 - 60',
        'thegrey': '45 - 55',
        'thurgadina': '1 - 10',
        'timorous': '25 - 40',
        'toxxulia': '1 - 10',
        'trakanon': '45 - 55',
        'twilight': '45 - 55',
        'umbral': '55 - 60',
        'unrest': '15 - 30',
        'wakening': '45 - 60',
        'wallofslaughter': '60 - 65',
        'warrens': '15 - 30',
        'westwastes': '55 - 60',
    }
    
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
                zone_data['zone_level_range'] = self.ZONE_LEVEL_CHART.get(short_name, "N/A")
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

    def waypoint_listing(self):
        """Get a list of zones that have waypoints."""
        if not self._zone_cache_populated:
            self._populate_zone_cache()

        continent_zones = {
            'Antonica': ['blackburrow', 'commons','eastkarana', 'ecommons', 'everfrost', 'feerrott', 'freportw', 'grobb', 'gukbottom', 'halas', 'highkeep', 'lakerathe', 'lavastorm', 'neriakb', 'northkarana', 'oasis', 'oggok', 'oot', 'qey2hh1', 'qeynos2', 'qrg', 'rivervale', 'southkarana'],
            'Faydwer': ['akanon', 'cauldron', 'felwithea', 'gfaydark', 'kaladima', 'mistmoore'],
            'Odus': ['dulak', 'erudnext', 'gunthak', 'hole', 'paineel', 'stonebrunt', 'tox'],
            'Kunark': ['burningwood', 'cabeast', 'chardokb', 'citymist', 'dreadlands', 'fieldofbone', 'firiona', 'frontiermtns', 'karnor', 'lakeofillomen', 'overthere', 'skyfire', 'timorous', 'trakanon'],
            'Velious': ['cobaltscar', 'eastwastes', 'greatdivide', 'iceclad', 'sirens', 'wakening', 'westwastes'],
            'Luclin': ['bazaar', 'dawnshroud', 'fungusgrove', 'paludal', 'scarlet', 'sharvahl', 'ssratemple', 'tenebrous', 'twilight', 'umbral'],
            'Planes': ['airplane', 'fearplane', 'hateplaneb', 'nightmareb', 'podisease', 'poknowledge', 'potimea', 'potranquility']
        }

        waypoints_by_continent = {}
        for continent, zones in continent_zones.items():
            continent_waypoints = []
            for short_name in zones:
                waypoint = self.get_zone_waypoint(short_name)
                if waypoint:
                    zone_id, long_name = self.get_zone_long_name(short_name)
                    if zone_id is not None:
                        continent_waypoints.append({
                            'long_name': long_name,
                            'id': zone_id,
                            'short_name': short_name,
                            'waypoint': waypoint
                        })
            
            # Sort by long_name
            continent_waypoints.sort(key=lambda x: x['long_name'])
            
            # Convert to the desired dictionary format
            waypoints_by_continent[continent] = {
                item['long_name']: {
                    'id': item['id'],
                    'short_name': item['short_name'],
                    'waypoint': item['waypoint']
                } for item in continent_waypoints
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
        
        continent_zones = {
            'Antonica': [
                'befallen', 'beholder', 'blackburrow', 'cazicthule', 'commons', 'eastkarana', 'ecommons', 'everfrost', 'feerrott',
                'freporte', 'freportn', 'freportw', 'grobb', 'gukbottom', 'guktop', 'halas', 'highkeep', 'highpass',
                'innothule', 'kithicor', 'lakerathe', 'lavastorm', 'misty', 'najena', 'nektulos', 'neriakb', 'neriaka',
                'neriakc', 'neriakd', 'northkarana', 'nro', 'oasis', 'oggok', 'oot', 'paw', 'permafrost', 'qcat', 'qey2hh1',
                'qeynos', 'qeynos2', 'qeytoqrg', 'qrg', 'rathemtn', 'rivervale', 'runnyeye', 'soldunga', 'soldungb',
                'soltemple', 'southkarana', 'sro'
            ],
            'Faydwer': [
                'akanon', 'butcher', 'cauldron', 'crushbone', 'felwithea', 'felwitheb', 'gfaydark', 'kaladima', 'kaladimb',
                'kedge', 'lfaydark', 'mistmoore', 'steamfont', 'unrest'
            ],
            'Odus': [
                'erudnext', 'erudnint', 'erudsxing', 'hole', 'kerraridge', 'paineel', 'stonebrunt', 'tox', 'warrens'
            ],
            'Kunark': [
                'burningwood', 'cabeast', 'cabwest', 'chardok', 'charasis', 'citymist', 'dalnir', 'dreadlands', 'droga',
                'emeraldjungle', 'fieldofbone', 'firiona', 'frontiermtns', 'howlingstones', 'kaesora', 'karnor', 'kurn',
                'lakeofillomen', 'nurga', 'overthere', 'sebilis', 'skyfire', 'swampofnohope', 'timorous', 'trakanon',
                'veeshan', 'veksar', 'warslikswood'
            ],
            'Velious': [
                'cobaltscar', 'crystal', 'dragonnecrop', 'eastwastes', 'frozenshadow', 'greatdivide', 'growthplane',
                'iceclad', 'kael', 'necropolis', 'sirens', 'skyshrine', 'sleeper', 'templeveeshan', 'thurgadina',
                'thurgadinb', 'towerfrozen', 'velketor', 'wakening', 'westwastes'
            ],
            'Luclin': [
                'acrylia', 'akheva', 'bazaar', 'dawnshroud', 'echo', 'fungusgrove', 'griegsend', 'grimling', 'hollowshade',
                'jaggedpine', 'katta', 'letalis', 'maiden', 'marusseru', 'mseru', 'netherbian', 'nexus', 'paludal',
                'scarlet', 'shadeweaver', 'shadowhaven', 'sharvahl', 'sseru', 'ssratemple', 'tenebrous', 'thedeep',
                'thegrey', 'twilight', 'umbral', 'vexthal'
            ],
            'Planes': [
                'airplane', 'bothunder', 'codecay', 'fearplane', 'hateplane', 'hateplaneb', 'hohonora', 'hohonorb',
                'mischiefplane', 'nightmareb', 'podisease', 'poair', 'poeartha', 'poearthb', 'pofire', 'pohonora',
                'pohonorb', 'poinnovation', 'pojustice', 'poknowledge', 'ponightmare', 'postagnation', 'postorms',
                'potactics', 'potimea', 'potimeb', 'potorment', 'pothunder', 'potranquility', 'povalor', 'powar',
                'powater', 'solrotower'
            ]
        }
        
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
                    z.expansion <= 4
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
                    'zone_level_range': self.ZONE_LEVEL_CHART.get(row_dict['short_name'], "N/A")
                })
            return zones_by_expansion

    def get_zone_waypoint(self, short_name):
        if short_name == 'blackburrow':
            return {'y': 38, 'x': -7, 'z': 3}
        elif short_name == 'commons':
            return {'y': -127, 'x': 503, 'z': -51}
        elif short_name == 'ecommons':
            return {'y': -1603, 'x': -356, 'z': 3}
        elif short_name == 'feerrott':
            return {'y': -430, 'x': -1830, 'z': -51}
        elif short_name == 'freportw':
            return {'y': -283, 'x': -396, 'z': -23}
        elif short_name == 'grobb':
            return {'y': 223, 'x': -200, 'z': 3.75}
        elif short_name == 'everfrost':
            return {'y': 2133, 'x': -6972, 'z': -58}
        elif short_name == 'halas':
            return {'y': 26, 'x': 0, 'z': 3.75}
        elif short_name == 'highkeep':
            return {'y': -17, 'x': -1, 'z': -4}
        elif short_name == 'lavastorm':
            return {'y': 918, 'x': 1318, 'z': 119}
        elif short_name == 'neriakb':
            return {'y': 3, 'x': -493, 'z': -10}
        elif short_name == 'northkarana':
            return {'y': -688, 'x': -175, 'z': -7.5}
        elif short_name == 'eastkarana':
            return {'y': 1333, 'x': 423, 'z': 1}
        elif short_name == 'oasis':
            return {'y': 532, 'x': 110, 'z': 6}
        elif short_name == 'oggok':
            return {'y': 465, 'x': 513, 'z': 3.75}
        elif short_name == 'oot':
            return {'y': 394, 'x': -9172, 'z': 6}
        elif short_name == 'qey2hh1':
            return {'y': -3570, 'x': -14816, 'z': 36}
        elif short_name == 'qeynos2':
            return {'y': 165, 'x': 392, 'z': 4}
        elif short_name == 'qrg':
            return {'y': 45, 'x': -66, 'z': 4}
        elif short_name == 'rivervale':
            return {'y': -10, 'x': -140, 'z': 4}
        elif short_name == 'gukbottom':
            return {'y': 1157, 'x': -233, 'z': -80}
        elif short_name == 'lakerathe':
            return {'y': 2404, 'x': 2673, 'z': 95}
        elif short_name == 'southkarana':
            return {'y': -6689, 'x': 1027, 'z': 0}
        elif short_name == 'akanon':
            return {'y': 1279, 'x': -761, 'z': -24.25}
        elif short_name == 'cauldron':
            return {'y': -1790, 'x': -700, 'z': 100}
        elif short_name == 'felwithea':
            return {'y': 240, 'x': -626, 'z': -10.25}
        elif short_name == 'gfaydark':
            return {'y': 458, 'x': -385, 'z': 0}
        elif short_name == 'kaladima':
            return {'y': 90, 'x': 197, 'z': 3.75}
        elif short_name == 'mistmoore':
            return {'y': -294, 'x': 122, 'z': -179}
        elif short_name == 'erudnext':
            return {'y': -1216, 'x': -240, 'z': 52}
        elif short_name == 'hole':
            return {'y': 287, 'x': -543, 'z': -140}
        elif short_name == 'paineel':
            return {'y': 839, 'x': 210, 'z': 4}
        elif short_name == 'tox':
            return {'y': -1510, 'x': -916, 'z': -33}
        elif short_name == 'stonebrunt':
            return {'y': -4531, 'x': 673, 'z': 0}
        elif short_name == 'dulak':
            return {'y': -190, 'x': -1190, 'z': 4}
        elif short_name == 'gunthak':
            return {'y': 1402, 'x': -410, 'z': 3}
        elif short_name == 'burningwood':
            return {'y': 7407, 'x': -3876, 'z': -233}
        elif short_name == 'cabeast':
            return {'y': 969, 'x': -136, 'z': 4.68}
        elif short_name == 'citymist':
            return {'y': 249, 'x': -572, 'z': 4}
        elif short_name == 'dreadlands':
            return {'y': 3005, 'x': 9633, 'z': 1049}
        elif short_name == 'fieldofbone':
            return {'y': -1684, 'x': 1617, 'z': -55}
        elif short_name == 'firiona':
            return {'y': -2397, 'x': 1825, 'z': -98}
        elif short_name == 'frontiermtns':
            return {'y': 53, 'x': 392, 'z': -102}
        elif short_name == 'karnor':
            return {'y': 251, 'x': 160, 'z': 3.75}
        elif short_name == 'lakeofillomen':
            return {'y': 985, 'x': -1070, 'z': 78}
        elif short_name == 'overthere':
            return {'y': -2757, 'x': 1480, 'z': 11}
        elif short_name == 'skyfire':
            return {'y': -3100, 'x': 780, 'z': -158}
        elif short_name == 'timorous':
            return {'y': -12256.8, 'x': 4366.5, 'z': -278}
        elif short_name == 'trakanon':
            return {'y': -1620, 'x': -4720, 'z': -473}
        elif short_name == 'chardokb':
            return {'y': 315, 'x': -210, 'z': 1.5}
        elif short_name == 'cobaltscar':
            return {'y': -1064, 'x': -1633, 'z': 296}
        elif short_name == 'eastwastes':
            return {'y': -4037, 'x': 464, 'z': 144}
        elif short_name == 'greatdivide':
            return {'y': -6646, 'x': 3287, 'z': -35}
        elif short_name == 'iceclad':
            return {'y': 1300, 'x': 3127, 'z': 111}
        elif short_name == 'wakening':
            return {'y': 1455, 'x': 4552, 'z': -60}
        elif short_name == 'westwastes':
            return {'y': 1323, 'x': 808, 'z': -196}
        elif short_name == 'cobaltscar':
            return {'y': -1065, 'x': -1634, 'z': 299}
        elif short_name == 'sirens':
            return {'y': -590, 'x': 20, 'z': -93}
        elif short_name == 'dawnshroud':
            return {'y': -280, 'x': -1260, 'z': 97}
        elif short_name == 'fungusgrove':
            return {'y': 2398, 'x': 1359, 'z': -261}
        elif short_name == 'sharvahl':
            return {'y': 55, 'x': 250, 'z': -188}
        elif short_name == 'ssratemple':
            return {'y': 0, 'x': -6.5, 'z': 4}
        elif short_name == 'tenebrous':
            return {'y': -1514, 'x': -967, 'z': -56}
        elif short_name == 'umbral':
            return {'y': -640, 'x': 1840, 'z': 24}
        elif short_name == 'twilight':
            return {'y': 1338, 'x': -1028, 'z': 39}
        elif short_name == 'scarlet':
            return {'y': -956, 'x': -1777, 'z': -99}
        elif short_name == 'paludal':
            return {'y': -1175, 'x': 220, 'z': -236}
        elif short_name == 'bazaar':
            return {'y': -175, 'x': 105, 'z': -15}
        elif short_name == 'airplane':
            return {'y': 1560, 'x': 700, 'z': -680}
        elif short_name == 'fearplane':
            return {'y': -1305, 'x': 1065, 'z': 3}
        elif short_name == 'hateplaneb':
            return {'y': 680, 'x': -400, 'z': 4}
        elif short_name == 'poknowledge':
            return {'y': 50, 'x': -215, 'z': -160}
        elif short_name == 'potranquility':
            return {'y': -192, 'x': -8, 'z': -628}
        elif short_name == 'potimea':
            return {'y': 110, 'x': 0, 'z': 8}
        elif short_name == 'barindu':
            return {'y': -515, 'x': 210, 'z': -117}
        elif short_name == 'kodtaz':
            return {'y': -2422, 'x': 1536, 'z': -348}
        elif short_name == 'natimbi':
            return {'y': 125, 'x': -310, 'z': 520}
        elif short_name == 'qvic':
            return {'y': -1403, 'x': -1018, 'z': -490}
        elif short_name == 'txevu':
            return {'y': -20, 'x': -316, 'z': -420}
        elif short_name == 'wallofslaughter':
            return {'y': 13, 'x': -943, 'z': 130}
        else:
            return {}
