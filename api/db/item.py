from sqlalchemy import text
from api.db_manager import db_manager
from api.db.quest import get_quest_item_ids

class ItemDB:
    def __init__(self):
        """Initialize the ItemDB class."""
        pass
    
    def get_item_raw_data(self, item_id=None, name=None, item_type=None):
        """Get raw item data from the database"""
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            if item_id:
                quest_item_ids = get_quest_item_ids()
                is_quest_item = item_id in quest_item_ids

                query = text("""
                    SELECT 
                        i.*,
                        e.name as expansion_name,
                        :is_quest_item as is_quest_item
                    FROM items i
                    LEFT JOIN (
                        SELECT 
                            le.item_id, 
                            MIN(z.expansion) as expansion_id
                        FROM lootdrop_entries le
                        INNER JOIN loottable_entries lte ON le.lootdrop_id = lte.lootdrop_id
                        INNER JOIN npc_types n ON lte.loottable_id = n.loottable_id
                        INNER JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                        WHERE le.item_id = :item_id
                        GROUP BY le.item_id
                    ) as item_expansion ON i.id = item_expansion.item_id
                    LEFT JOIN merchantlist m ON i.id = m.item
                    LEFT JOIN npc_types nt ON m.merchantid = nt.id
                    LEFT JOIN zone z_merchant ON z_merchant.zoneidnumber = FLOOR(nt.id / 1000)
                    LEFT JOIN expansion e ON COALESCE(item_expansion.expansion_id, z_merchant.expansion) = e.id
                    WHERE i.id = :item_id
                """)
                result = conn.execute(query, {"item_id": item_id, "is_quest_item": is_quest_item}).fetchone()
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
                    e.name as expansion_name,
                    COUNT(DISTINCT le.item_id) as drop_count
                FROM items i
                LEFT JOIN lootdrop_entries le ON i.id = le.item_id
                LEFT JOIN loottable_entries lte ON le.lootdrop_id = lte.lootdrop_id
                LEFT JOIN npc_types n ON lte.loottable_id = n.loottable_id
                LEFT JOIN merchantlist m ON i.id = m.item
                LEFT JOIN npc_types nt ON m.merchantid = nt.id
                LEFT JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000) OR z.zoneidnumber = FLOOR(nt.id / 1000)
                LEFT JOIN expansion e ON z.expansion = e.id
                WHERE z.short_name = :zone_short_name
                AND i.name NOT LIKE '#%'
                AND (le.chance > 0 OR m.item IS NOT NULL)
                GROUP BY i.id, i.name, i.itemtype, i.itemclass, i.weight, i.size, 
                         i.slots, i.price, i.icon, i.lore, i.nodrop, i.norent, 
                         i.magic, i.races, i.classes, i.ac, i.hp, i.mana, i.damage, i.delay, e.name
                ORDER BY i.itemtype, i.name
                LIMIT 100
            """)
            
            results = conn.execute(query, {"zone_short_name": zone_short_name}).fetchall()
            return [dict(row._mapping) for row in results]

    def get_items_by_expansion(self, expansion_id):
        """Get items that drop in a specific expansion"""
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
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
                    e.name as expansion_name,
                    COUNT(DISTINCT le.item_id) as drop_count
                FROM items i
                LEFT JOIN lootdrop_entries le ON i.id = le.item_id
                LEFT JOIN loottable_entries lte ON le.lootdrop_id = lte.lootdrop_id
                LEFT JOIN npc_types n ON lte.loottable_id = n.loottable_id
                LEFT JOIN merchantlist m ON i.id = m.item
                LEFT JOIN npc_types nt ON m.merchantid = nt.id
                LEFT JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000) OR z.zoneidnumber = FLOOR(nt.id / 1000)
                LEFT JOIN expansion e ON z.expansion = e.id
                WHERE z.expansion = :expansion_id
                AND i.name NOT LIKE '#%'
                AND (le.chance > 0 OR m.item IS NOT NULL)
                GROUP BY i.id, i.name, i.itemtype, i.itemclass, i.weight, i.size, 
                         i.slots, i.price, i.icon, i.lore, i.nodrop, i.norent, 
                         i.magic, i.races, i.classes, i.ac, i.hp, i.mana, i.damage, i.delay, e.name
                ORDER BY i.itemtype, i.name
                LIMIT 100
            """)
            
            results = conn.execute(query, {"expansion_id": expansion_id}).fetchall()
            return [dict(row._mapping) for row in results]
