from sqlalchemy import text
from api.db_manager import db_manager

class NPCDB:
    def __init__(self):
        """Initialize the NPCDB class."""
        pass
    
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
