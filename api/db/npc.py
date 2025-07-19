from sqlalchemy import text
from api.db_manager import db_manager
import logging
from api.cache import cache_results
from utils import get_bane_dmg_race

logger = logging.getLogger(__name__)

class NPCDB:
    def __init__(self):
        """Initialize the NPCDB class."""
        pass

    @cache_results(ttl=86400)  # Cache for 24 hours
    def get_race_name(self, race_id):
        """Get the name of a race by its ID."""
        try:
            # Use canonical Python mapping first
            race_name = get_bane_dmg_race(race_id)
            if race_name and not race_name.startswith('Unknown'):
                return race_name
            # Fallback to DB query for rare/legacy cases
            engine = db_manager._engines['old']
            with engine.connect() as conn:
                query = text("SELECT value FROM db_str WHERE id = :race_id AND type = 12")
                result = conn.execute(query, {"race_id": race_id}).fetchone()
                return result[0] if result else str(race_id)
        except Exception as e:
            logger.error(f"Failed to get race name for ID {race_id}: {e}")
            return str(race_id)

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

    @cache_results(ttl=900)
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
            
            # Map race IDs to names using the new method
            npcs = []
            for row in results:
                npc_data = dict(row._mapping)
                race_id = npc_data.get('race')
                npc_data['race'] = self.get_race_name(race_id)
                npcs.append(npc_data)
                
            return npcs
