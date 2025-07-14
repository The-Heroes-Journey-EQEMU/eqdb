from sqlalchemy import text
from api.db_manager import db_manager
import logging

logger = logging.getLogger(__name__)

class NPCDB:
    _race_cache = None

    def __init__(self):
        """Initialize the NPCDB class."""
        if NPCDB._race_cache is None:
            self._populate_race_cache()

    def _populate_race_cache(self):
        """Populate the in-memory cache for race names from the 'old' database."""
        logger.info("Populating race cache...")
        try:
            # Explicitly use the 'old' database engine for the db_str table
            engine = db_manager._engines['old']
            with engine.connect() as conn:
                query = text("SELECT id, value FROM db_str WHERE type = 12")
                results = conn.execute(query).fetchall()
                NPCDB._race_cache = {row._mapping['id']: row._mapping['value'] for row in results}
                logger.info(f"Race cache populated with {len(NPCDB._race_cache)} entries.")
        except Exception as e:
            logger.error(f"Failed to populate race cache: {e}")
            # Initialize with an empty cache on failure to prevent repeated attempts
            NPCDB._race_cache = {}

    def get_npc_raw_data(self, npc_id=None, name=None, zone=None):
        """Get raw NPC data from the database"""
        engine = db_manager.get_engine_for_table('npc_types')
        with engine.connect() as conn:
            if npc_id:
                query = text("""
                    SELECT n.*, z.short_name as zone_name, z.long_name as zone_long_name, z.expansion as zone_expansion
                    FROM npc_types n
                    LEFT JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                    WHERE n.id = :npc_id
                """)
                result = conn.execute(query, {"npc_id": npc_id}).fetchone()
                if result:
                    return dict(result._mapping)
                return None
            elif name:
                query = text("""
                    SELECT n.*, z.short_name as zone_name, z.long_name as zone_long_name, z.expansion as zone_expansion
                    FROM npc_types n
                    LEFT JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                    WHERE n.name LIKE :name
                    AND (:zone IS NULL OR z.short_name = :zone)
                    ORDER BY n.name
                    LIMIT 50
                """)
                results = conn.execute(query, {"name": f"%{name}%", "zone": zone}).fetchall()
                return [dict(row._mapping) for row in results]
            return None

    def get_npcs_by_zone(self, zone_short_name):
        """Get NPCs for a specific zone by short name"""
        engine = db_manager.get_engine_for_table('npc_types')
        with engine.connect() as conn:
            # First get the zone ID from the zone short name
            zone_query = text("SELECT zoneidnumber FROM zone WHERE short_name = :zone_short_name")
            zone_result = conn.execute(zone_query, {"zone_short_name": zone_short_name}).fetchone()
            
            if not zone_result:
                return []
            
            zone_id = zone_result._mapping['zoneidnumber']
            
            # Get NPCs that belong to this zone, without joining db_str
            query = text("""
                SELECT 
                    n.id,
                    n.name,
                    n.level,
                    n.race,
                    n.class,
                    n.hp,
                    n.mindmg,
                    n.maxdmg,
                    z.short_name as zone_name,
                    z.long_name as zone_long_name
                FROM npc_types n
                LEFT JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                WHERE z.short_name = :zone_short_name
                AND n.name NOT LIKE '#%'
                AND n.name NOT LIKE 'a_%'
                AND n.name NOT LIKE 'an_%'
                ORDER BY n.level DESC, n.name
                LIMIT 100
            """)
            
            results = conn.execute(query, {"zone_short_name": zone_short_name}).fetchall()
            
            # Map race IDs to names using the cache
            npcs = []
            for row in results:
                npc_data = dict(row._mapping)
                race_id = npc_data.get('race')
                # Use the cache, with a fallback to the ID itself if not found
                npc_data['race'] = NPCDB._race_cache.get(race_id, str(race_id))
                npcs.append(npc_data)
                
            return npcs
