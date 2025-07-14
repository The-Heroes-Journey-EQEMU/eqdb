from sqlalchemy import text
from api.db_manager import db_manager

class ItemDB:
    def __init__(self):
        """Initialize the ItemDB class."""
        pass
    
    def get_item_raw_data(self, item_id=None, name=None, item_type=None):
        """Get raw item data from the database"""
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            if item_id:
                query = text("""
                    SELECT * FROM items 
                    WHERE id = :item_id
                """)
                result = conn.execute(query, {"item_id": item_id}).fetchone()
                if result:
                    return dict(result._mapping)
                return None
            elif name:
                query = text("""
                    SELECT * FROM items 
                    WHERE name LIKE :name
                    LIMIT 50
                """)
                results = conn.execute(query, {"name": f"%{name}%"}).fetchall()
                return [dict(row._mapping) for row in results]
            elif item_type:
                query = text("""
                    SELECT * FROM items 
                    WHERE type = :item_type
                    LIMIT 50
                """)
                results = conn.execute(query, {"item_type": item_type}).fetchall()
                return [dict(row._mapping) for row in results]
            return None

    def get_items_by_zone(self, zone_short_name):
        """Get items that drop in a specific zone"""
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            # First get the zone ID from the zone short name
            zone_query = text("SELECT zoneidnumber FROM zone WHERE short_name = :zone_short_name")
            zone_result = conn.execute(zone_query, {"zone_short_name": zone_short_name}).fetchone()
            
            if not zone_result:
                return []
            
            zone_id = zone_result._mapping['zoneidnumber']
            
            # Get items that drop from NPCs in this zone through loot tables
            query = text("""
                SELECT DISTINCT
                    i.id,
                    i.name,
                    i.itemtype,
                    i.itemclass,
                    i.weight,
                    i.size,
                    i.slots,
                    i.price,
                    i.icon,
                    i.lore,
                    i.nodrop,
                    i.norent,
                    i.magic,
                    i.races,
                    i.classes,
                    i.ac,
                    i.hp,
                    i.mana,
                    i.damage,
                    i.delay,
                    COUNT(DISTINCT le.item_id) as drop_count
                FROM items i
                INNER JOIN lootdrop_entries le ON i.id = le.item_id
                INNER JOIN loottable_entries lte ON le.lootdrop_id = lte.lootdrop_id
                INNER JOIN npc_types n ON lte.loottable_id = n.loottable_id
                INNER JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                WHERE z.short_name = :zone_short_name
                AND i.name NOT LIKE '#%'
                AND le.chance > 0
                GROUP BY i.id, i.name, i.itemtype, i.itemclass, i.weight, i.size, 
                         i.slots, i.price, i.icon, i.lore, i.nodrop, i.norent, 
                         i.magic, i.races, i.classes, i.ac, i.hp, i.mana, i.damage, i.delay
                ORDER BY i.itemtype, i.name
                LIMIT 100
            """)
            
            results = conn.execute(query, {"zone_short_name": zone_short_name}).fetchall()
            return [dict(row._mapping) for row in results]
