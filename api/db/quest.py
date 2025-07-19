from sqlalchemy import text
import os
from api.db_manager import db_manager

def get_quest_item_ids(zone_id=None):
    """Get all quest item IDs from the item files, optionally filtered by zone."""
    item_files_dir = os.path.join(os.path.dirname(__file__), '..', 'item_files')
    quest_files = []

    if zone_id:
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            query = text("SELECT expansion FROM zone WHERE zoneidnumber = :zone_id")
            result = conn.execute(query, {"zone_id": zone_id}).fetchone()
            if result:
                expansion_id = result[0]
                expansion_map = {
                    0: 'Classic.txt', 1: 'Kunark.txt', 2: 'Velious.txt', 3: 'Luclin.txt',
                    4: 'Planes.txt', 5: 'LoY.txt', 6: 'LDoN.txt', 7: 'GoD.txt',
                    8: 'OoW.txt', 9: 'DoN.txt'
                }
                if expansion_id in expansion_map:
                    quest_files.append(expansion_map[expansion_id])
    else:
        quest_files = [
            'Classic.txt', 'Kunark.txt', 'Velious.txt', 'Luclin.txt', 
            'Planes.txt', 'GoD.txt', 'OoW.txt', 'DoN.txt', 'LDoN.txt', 'LoY.txt'
        ]

    quest_item_ids = []
    for filename in quest_files:
        filepath = os.path.join(item_files_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read().strip()
                if content:
                    quest_item_ids.extend(content.split('\n'))
    
    return [int(item_id) for item_id in quest_item_ids if item_id.strip().isdigit()]

class QuestDB:
    def __init__(self):
        """Initialize the QuestDB class."""
        self.quest_item_ids = get_quest_item_ids()
    
    def get_quest_raw_data(self, name=None, npc_name=None, item_id=None, item_name=None, 
                          min_level=None, max_level=None, zone=None, expansion=None, class_name=None):
        """Get raw quest data from the database"""
        if name or npc_name:
            engine = db_manager.get_engine_for_table('npc_types')
        elif item_id or item_name:
            engine = db_manager.get_engine_for_table('items')
        else:
            return None

        with engine.connect() as conn:
            if name:
                # Search by quest name - look for NPCs with matching names
                query = text("""
                    SELECT DISTINCT n.id as npc_id, n.name as npc_name, n.level, z.short_name as zone_name,
                           z.long_name as zone_long_name, z.expansion as zone_expansion
                    FROM npc_types n
                    JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                    WHERE n.name LIKE :name
                    AND (:min_level IS NULL OR n.level >= :min_level)
                    AND (:max_level IS NULL OR n.level <= :max_level)
                    AND (:zone IS NULL OR z.short_name = :zone)
                    AND (:expansion IS NULL OR z.expansion = :expansion)
                    ORDER BY n.name
                    LIMIT 50
                """)
                results = conn.execute(query, {
                    "name": f"%{name}%",
                    "min_level": min_level,
                    "max_level": max_level,
                    "zone": zone,
                    "expansion": expansion
                }).fetchall()
                quests = []
                for row in results:
                    quest_data = dict(row._mapping)
                    quest_data['quest_name'] = f"Quest from {quest_data['npc_name']}"
                    quests.append(quest_data)
                return quests
                
            elif npc_name:
                # Search by NPC name
                query = text("""
                    SELECT DISTINCT n.id as npc_id, n.name as npc_name, n.level, z.short_name as zone_name,
                           z.long_name as zone_long_name, z.expansion as zone_expansion
                    FROM npc_types n
                    JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                    WHERE n.name LIKE :npc_name
                    AND (:min_level IS NULL OR n.level >= :min_level)
                    AND (:max_level IS NULL OR n.level <= :max_level)
                    AND (:zone IS NULL OR z.short_name = :zone)
                    AND (:expansion IS NULL OR z.expansion = :expansion)
                    ORDER BY n.name
                    LIMIT 50
                """)
                results = conn.execute(query, {
                    "npc_name": f"%{npc_name}%",
                    "min_level": min_level,
                    "max_level": max_level,
                    "zone": zone,
                    "expansion": expansion
                }).fetchall()
                quests = []
                for row in results:
                    quest_data = dict(row._mapping)
                    quest_data['quest_name'] = f"Quest from {quest_data['npc_name']}"
                    quests.append(quest_data)
                return quests
                
            elif item_id:
                # Search by item ID - check if it's a quest item
                if int(item_id) in self.quest_item_ids:
                    # Get item details
                    query = text("""
                        SELECT i.id as item_id, i.Name as item_name, i.itemtype, i.classes, i.slots
                        FROM items i
                        WHERE i.id = :item_id
                    """)
                    result = conn.execute(query, {"item_id": item_id}).fetchone()
                    if result:
                        item_data = dict(result._mapping)
                        item_data['quest_name'] = f"Quest Item: {item_data['item_name']}"
                        item_data['is_quest_item'] = True
                        return item_data
                return None
                
            elif item_name:
                # Search by item name - check if it's a quest item
                query = text("""
                    SELECT i.id as item_id, i.Name as item_name, i.itemtype, i.classes, i.slots
                    FROM items i
                    WHERE i.Name LIKE :item_name
                    AND i.id IN ({})
                    ORDER BY i.Name
                    LIMIT 50
                """.format(','.join(map(str, self.quest_item_ids))))
                results = conn.execute(query, {"item_name": f"%{item_name}%"}).fetchall()
                quest_items = []
                for row in results:
                    item_data = dict(row._mapping)
                    item_data['quest_name'] = f"Quest Item: {item_data['item_name']}"
                    item_data['is_quest_item'] = True
                    quest_items.append(item_data)
                return quest_items
                
            return None
    
    def get_quest_chains(self, npc_id=None, faction_id=None):
        """Get quest chains based on NPC or faction"""
        engine = db_manager.get_engine_for_table('npc_types')
        with engine.connect() as conn:
            if npc_id:
                # Get NPC details
                query = text("""
                    SELECT DISTINCT n.id as npc_id, n.name as npc_name, n.level, z.short_name as zone_name
                    FROM npc_types n
                    JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                    WHERE n.id = :npc_id
                """)
                results = conn.execute(query, {"npc_id": npc_id}).fetchall()
                return [dict(row._mapping) for row in results]
                
            elif faction_id:
                # Get NPCs from a specific faction (if faction system exists)
                query = text("""
                    SELECT DISTINCT n.id as npc_id, n.name as npc_name, n.level, z.short_name as zone_name
                    FROM npc_types n
                    JOIN zone z ON z.zoneidnumber = FLOOR(n.id / 1000)
                    WHERE n.npc_faction_id = :faction_id
                    ORDER BY n.level, n.name
                    LIMIT 50
                """)
                results = conn.execute(query, {"faction_id": faction_id}).fetchall()
                return [dict(row._mapping) for row in results]
                
            return []
    
    def get_quest_items_by_expansion(self, expansion=None):
        """Get quest items by expansion"""
        if not expansion:
            return []
        
        expansion_files = {
            'classic': 'Classic.txt',
            'kunark': 'Kunark.txt',
            'velious': 'Velious.txt',
            'luclin': 'Luclin.txt',
            'planes': 'Planes.txt',
            'god': 'GoD.txt',
            'oow': 'OoW.txt',
            'don': 'DoN.txt',
            'ldon': 'LDoN.txt',
            'loy': 'LoY.txt'
        }
        
        filename = expansion_files.get(expansion.lower())
        if not filename:
            return []
        
        filepath = os.path.join(os.path.dirname(__file__), '..', 'item_files', filename)
        if not os.path.exists(filepath):
            return []
        
        with open(filepath, 'r') as f:
            content = f.read().strip()
            if not content:
                return []
            
            item_ids = [int(item_id) for item_id in content.split('\n') if item_id.strip().isdigit()]
            
            engine = db_manager.get_engine_for_table('items')
            with engine.connect() as conn:
                if not item_ids:
                    return []
                
                query = text("""
                    SELECT i.id as item_id, i.Name as item_name, i.itemtype, i.classes, i.slots
                    FROM items i
                    WHERE i.id IN ({})
                    ORDER BY i.Name
                    LIMIT 50
                """.format(','.join(map(str, item_ids))))
                
                results = conn.execute(query).fetchall()
                quest_items = []
                for row in results:
                    item_data = dict(row._mapping)
                    item_data['quest_name'] = f"Quest Item: {item_data['item_name']}"
                    item_data['is_quest_item'] = True
                    item_data['expansion'] = expansion
                    quest_items.append(item_data)
                return quest_items
    
    def get_zones_by_expansion(self):
        """Get zones grouped by expansion for the two-tiered selector"""
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            query = text("""
                SELECT DISTINCT z.expansion, z.short_name, z.long_name
                FROM zone z
                WHERE z.expansion IS NOT NULL
                ORDER BY z.expansion, z.long_name
            """)
            results = conn.execute(query).fetchall()
            
            zones_by_expansion = {}
            for row in results:
                expansion = row[0]
                zone_data = {
                    'short_name': row[1],
                    'long_name': row[2]
                }
                
                if expansion not in zones_by_expansion:
                    zones_by_expansion[expansion] = []
                zones_by_expansion[expansion].append(zone_data)
            
            return zones_by_expansion
    
    def get_expansions(self):
        """Get list of available expansions"""
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            query = text("""
                SELECT DISTINCT expansion
                FROM zone
                WHERE expansion IS NOT NULL
                ORDER BY expansion
            """)
            results = conn.execute(query).fetchall()
            return [row[0] for row in results]
    
    def get_zones_in_expansion(self, expansion):
        """Get zones for a specific expansion"""
        engine = db_manager.get_engine_for_table('zone')
        with engine.connect() as conn:
            query = text("""
                SELECT short_name, long_name
                FROM zone
                WHERE expansion = :expansion
                ORDER BY long_name
            """)
            results = conn.execute(query, {"expansion": expansion}).fetchall()
            return [{'short_name': row[0], 'long_name': row[1]} for row in results]
