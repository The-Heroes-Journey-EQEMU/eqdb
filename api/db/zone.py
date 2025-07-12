from sqlalchemy import create_engine, text
import configparser
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_config():
    """Get configuration from configuration.ini file"""
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    return config

class ZoneDB:
    _zone_cache = None  # Class-level cache for shortname -> (zoneidnumber, long_name)
    _zone_cache_populated = False

    def __init__(self):
        """Initialize the zone database connection"""
        config = get_config()
        db_config = config['database']
        url = f"{db_config['driver']}{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(url)

    def _populate_zone_cache(self):
        """Populate the in-memory cache for zone long names."""
        with self.engine.connect() as conn:
            query = text("SELECT short_name, zoneidnumber, long_name FROM zone")
            results = conn.execute(query).fetchall()
            ZoneDB._zone_cache = {row._mapping['short_name']: (row._mapping['zoneidnumber'], row._mapping['long_name']) for row in results}
            ZoneDB._zone_cache_populated = True
            logger.info(f"Zone cache populated with {len(ZoneDB._zone_cache)} entries.")

    def get_zone_raw_data(self, zone_id=None, name=None):
        """Get raw zone data from the database"""
        with self.engine.connect() as conn:
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
            'Antonica': ['blackburrow', 'commons', 'ecommons', 'feerrott', 'freportw', 'grobb', 'everfrost', 'halas', 'highkeep', 'lavastorm', 'neriakb', 'northkarana', 'eastkarana', 'oasis', 'oggok', 'oot', 'qey2hh1', 'qeynos2', 'qrg', 'rivervale', 'gukbottom', 'lakerathe', 'southkarana'],
            'Faydwer': ['akanon', 'cauldron', 'felwithea', 'gfaydark', 'kaladima', 'mistmoore'],
            'Odus': ['erudnext', 'hole', 'paineel', 'tox', 'stonebrunt', 'dulak', 'gunthak'],
            'Kunark': ['burningwood', 'cabeast', 'citymist', 'dreadlands', 'fieldofbone', 'firiona', 'frontiermtns', 'karnor', 'lakeofillomen', 'overthere', 'skyfire', 'timorous', 'trakanon', 'chardokb'],
            'Velious': ['cobaltscar', 'eastwastes', 'greatdivide', 'iceclad', 'wakening', 'westwastes', 'sirens'],
            'Luclin': ['dawnshroud', 'fungusgrove', 'sharvahl', 'ssratemple', 'tenebrous', 'umbral', 'twilight', 'scarlet', 'paludal', 'bazaar'],
            'Planes': ['airplane', 'fearplane', 'hateplaneb', 'poknowledge', 'potranquility', 'potimea']
        }

        waypoints_by_continent = {}
        for continent, zones in continent_zones.items():
            waypoints_by_continent[continent] = {}
            for short_name in zones:
                waypoint = self.get_zone_waypoint(short_name)
                if waypoint:
                    zone_id, long_name = self.get_zone_long_name(short_name)
                    if zone_id is not None:
                        waypoints_by_continent[continent][long_name] = {
                            'id': zone_id,
                            'short_name': short_name,
                            'waypoint': waypoint
                        }
        
        return waypoints_by_continent

    def get_all_zones_by_expansion(self):
        """Get all zones grouped by expansion."""
        from api.db.expansion import ExpansionDB
        from api.utils import get_exclusion_list
        
        exclusion_list = get_exclusion_list('zone')
        expansion_db = ExpansionDB(self.engine.url)
        expansions = expansion_db.get_all_expansions()
        
        with self.engine.connect() as conn:
            query = text("""
                SELECT
                    z.expansion,
                    z.short_name,
                    z.long_name
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
                
                zones_by_expansion[expansion_name].append({
                    'short_name': row_dict['short_name'],
                    'long_name': row_dict['long_name']
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
