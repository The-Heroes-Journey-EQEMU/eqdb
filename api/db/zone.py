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