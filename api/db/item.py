from sqlalchemy import text
from api.db_manager import db_manager
from api.db.quest import get_quest_item_ids
from utils import get_type_string, get_slot_string, Util, get_class_string
from api.db.expansion import ExpansionDB
from api.db.expansion_items import ExpansionItemsDB
from api.cache import cache_results
from api.db.item_indexer_utils import index_item
import logging

class ItemDB:
    def __init__(self):
        """Initialize the ItemDB class."""
        self.expansion_items_db = ExpansionItemsDB('sqlite:///expansion_items.db')
    
    def search_items(self, name=None, item_type=None, tradeskill_only=False, equippable_only=False, exclude_glamours=False, only_augments=False, quality=None, item_slot=None, itemtype_name=None, slot_names=None, itemclass_name=None, page=1, page_size=20):
        """Search for items with extended filters and pagination support."""
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            params = {}
            conditions = []

            if name:
                conditions.append("name LIKE :name")
                params["name"] = f"%{name}%"
            
            if item_type:
                conditions.append("itemtype = :item_type")
                params["item_type"] = item_type

            if tradeskill_only:
                conditions.append("tradeskills = 1")

            if equippable_only:
                conditions.append("slots > 0")

            if exclude_glamours:
                conditions.append("itemtype != 'Glamour'")

            if only_augments:
                conditions.append("itemtype = 'Augmentation'")

            if quality:
                conditions.append("quality = :quality")
                params["quality"] = quality

            if item_slot:
                conditions.append("slots & :item_slot > 0")
                params["item_slot"] = item_slot

            # Use Util for itemtype_name
            if itemtype_name:
                type_map = Util.get_categorized_item_types()
                type_id = None
                for k, v in type_map.items():
                    if v.lower() == itemtype_name.lower():
                        type_id = k
                        break
                if type_id is not None:
                    conditions.append("itemtype = :itemtype_name_id")
                    params["itemtype_name_id"] = type_id
                else:
                    # If the type is not found, return no results
                    return {'results': [], 'total': 0, 'page': page, 'page_size': page_size, 'pages': 0}

            # Use Util for slot_names
            if slot_names:
                slot_map = Util.get_categorized_item_slots()
                slot_id = None
                for k, v in slot_map.items():
                    if v.lower() == slot_names.lower():
                        slot_id = k
                        break
                if slot_id is not None:
                    conditions.append("slots & :slot_name_bitmask > 0")
                    params["slot_name_bitmask"] = slot_id

            # Use Util for itemclass_name (Weapon/Armor only)
            if itemclass_name:
                if itemclass_name.lower() == 'weapon':
                    weapon_type_ids = list(Util.get_categorized_item_types('weapon').keys())
                    if weapon_type_ids:
                        conditions.append(f"itemtype IN ({', '.join([str(i) for i in weapon_type_ids])})")
                elif itemclass_name.lower() == 'armor':
                    armor_type_ids = list(Util.get_categorized_item_types('armor').keys())
                    if armor_type_ids:
                        conditions.append(f"itemtype IN ({', '.join([str(i) for i in armor_type_ids])})")

            # Pagination
            try:
                page = int(page)
                page_size = int(page_size)
                if page < 1:
                    page = 1
                if page_size < 1 or page_size > 200:
                    page_size = 20
            except Exception:
                page = 1
                page_size = 20
            offset = (page - 1) * page_size

            query_str = "SELECT id, name, itemtype, icon FROM items"
            if conditions:
                query_str += " WHERE " + " AND ".join(conditions)
            
            # Get total count for pagination
            count_query_str = query_str.replace("SELECT id, name, itemtype, icon", "SELECT COUNT(*) as total")
            count_query = text(count_query_str)
            total_count = conn.execute(count_query, params).fetchone()[0]

            query_str += f" LIMIT {page_size} OFFSET {offset}"
            query = text(query_str)
            results = conn.execute(query, params).fetchall()
            items = [dict(row._mapping) for row in results]
            return {
                'results': items,
                'total': total_count,
                'page': page,
                'page_size': page_size,
                'pages': (total_count + page_size - 1) // page_size
            }

    def get_item_types(self):
        """Get all item types using canonical Util mappings."""
        return {
            "all": Util.get_categorized_item_types(),
            "weapons": Util.get_categorized_item_types('weapon'),
            "armor": Util.get_categorized_item_types('armor')
        }

    def get_item_slots(self):
        """Get all item slots using canonical Util mappings."""
        return {
            "all": Util.get_categorized_item_slots(),
            "weapons": Util.get_categorized_item_slots('weapon'),
            "armor": Util.get_categorized_item_slots('armor')
        }

    def get_item_classes(self):
        """Get all item classes using canonical Python mapping."""
        # There are 16 standard EQ classes (1-16)
        return {i: get_class_string(i) for i in range(1, 17)}

    def get_item_details(self, item_id):
        """Get full details for a single item."""
        engine = db_manager.get_engine_for_table('items')
        expansion_db = ExpansionDB()
        expansions = {exp['id']: exp['name'] for exp in expansion_db.get_all_expansions()}

        with engine.connect() as conn:
            quest_item_ids = get_quest_item_ids()
            is_quest_item = item_id in quest_item_ids

            expansion_item = self.expansion_items_db.search_items(item_id=item_id)
            expansion_name = "Classic"
            if expansion_item:
                expansion_id = expansion_item[0]['expansion_id']
                expansion_name = expansions.get(expansion_id, "Classic")

            query = text("SELECT * FROM items WHERE id = :item_id")
            result = conn.execute(query, {"item_id": item_id}).fetchone()
            if result:
                item = dict(result._mapping)
                item['expansion_name'] = expansion_name
                item['is_quest_item'] = is_quest_item
                # Add human-readable itemtype and slots
                item['itemtype_name'] = get_type_string(item.get('itemtype', 0))
                item['slot_names'] = get_slot_string(item.get('slots', 0))
                index_item(item_id)
                return item
        return None

    @cache_results(ttl=900)
    def get_items_by_zone(self, zone_short_name):
        """Get items that drop in a specific zone by first fetching NPCs."""
        engine = db_manager.get_engine_for_table('items')

        with engine.connect() as conn:
            zone_query = text("SELECT zoneidnumber FROM zone WHERE short_name = :zone_short_name")
            zone_result = conn.execute(zone_query, {"zone_short_name": zone_short_name}).fetchone()

            if not zone_result:
                return []

            zone_id = zone_result[0]

            # Step 1: Get all NPCs in the zone
            npc_query = text("""
                SELECT DISTINCT nt.id, nt.loottable_id, nt.merchant_id
                FROM npc_types nt
                JOIN spawnentry se ON nt.id = se.npcID
                JOIN spawngroup sg ON se.spawngroupID = sg.id
                JOIN spawn2 s2 ON sg.id = s2.spawngroupID
                WHERE s2.zone = :zone_short_name
            """)
            npcs = conn.execute(npc_query, {"zone_short_name": zone_short_name}).fetchall()

            loottable_ids = {npc.loottable_id for npc in npcs if npc.loottable_id > 0}
            merchant_ids = {npc.merchant_id for npc in npcs if npc.merchant_id > 0}

            if not loottable_ids and not merchant_ids:
                return []

            # Step 2: Get all lootdrop_ids from the loottables
            lootdrop_ids = set()
            if loottable_ids:
                loottable_query = text("SELECT lootdrop_id FROM loottable_entries WHERE loottable_id IN :loottable_ids")
                lootdrop_results = conn.execute(loottable_query, {"loottable_ids": tuple(loottable_ids)}).fetchall()
                lootdrop_ids.update(row[0] for row in lootdrop_results)

            # Step 3: Get all item_ids from lootdrop_entries and merchantlists
            item_ids = set()
            if lootdrop_ids:
                lootdrop_entries_query = text("SELECT item_id FROM lootdrop_entries WHERE lootdrop_id IN :lootdrop_ids AND chance > 0")
                item_id_results = conn.execute(lootdrop_entries_query, {"lootdrop_ids": tuple(lootdrop_ids)}).fetchall()
                item_ids.update(row[0] for row in item_id_results)

            if merchant_ids:
                merchantlist_query = text("SELECT item FROM merchantlist WHERE merchantid IN :merchant_ids")
                merchant_item_results = conn.execute(merchantlist_query, {"merchant_ids": tuple(merchant_ids)}).fetchall()
                item_ids.update(row[0] for row in merchant_item_results)

            quest_item_ids = get_quest_item_ids(zone_id=zone_id)
            item_ids.update(quest_item_ids)

            if not item_ids:
                return []

            # Step 4: Get all item details for the collected item_ids
            items = []
            if item_ids:
                # Fetch basic info for all items at once
                item_query = text("SELECT id, name, itemtype, icon FROM items WHERE id IN :item_ids")
                item_results = conn.execute(item_query, {"item_ids": tuple(item_ids[:500])}).fetchall()
                
                # Create a dictionary for quick lookups
                item_dict = {row[0]: dict(row._mapping) for row in item_results}
                
                # Add expansion and quest info
                quest_item_ids = get_quest_item_ids()
                
                for item_id in item_ids:
                    if item_id in item_dict:
                        item_data = item_dict[item_id]
                        
                        # Check expansion
                        expansion_item = self.expansion_items_db.search_items(item_id=item_id)
                        item_data['expansion_name'] = "Classic"
                        if expansion_item:
                            expansion_db = ExpansionDB()
                            expansions = {exp['id']: exp['name'] for exp in expansion_db.get_all_expansions()}
                            expansion_id = expansion_item[0]['expansion_id']
                            item_data['expansion_name'] = expansions.get(expansion_id, "Classic")
                        
                        # Check if it's a quest item
                        item_data['is_quest_item'] = item_id in quest_item_ids
                        items.append(item_data)

            return sorted(items, key=lambda x: (x.get('itemtype', 0), x.get('name', '')))

    def get_items_by_expansion(self, expansion_id):
        """Get items that drop in a specific expansion"""
        expansion_items = self.expansion_items_db.get_items_by_expansion(expansion_id)
        item_ids = [item.item_id for item in expansion_items]

        if not item_ids:
            return []

        items = []
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            # Fetch basic info for all items at once
            item_query = text("SELECT id, name, itemtype, icon FROM items WHERE id IN :item_ids")
            # Limit the number of parameters to avoid issues with some DBs
            item_results = conn.execute(item_query, {"item_ids": tuple(item_ids[:500])}).fetchall()
            
            item_dict = {item['id']: dict(item._mapping) for item in item_results}
            
            quest_item_ids = get_quest_item_ids()
            expansion_db = ExpansionDB()
            expansions = {exp['id']: exp['name'] for exp in expansion_db.get_all_expansions()}
            
            for item_id in item_ids:
                if item_id in item_dict:
                    item_data = item_dict[item_id]
                    
                    # Set expansion name
                    item_data['expansion_name'] = expansions.get(expansion_id, "Unknown")
                    
                    # Check if it's a quest item
                    item_data['is_quest_item'] = item_id in quest_item_ids
                    items.append(item_data)

        return sorted(items, key=lambda x: (x.get('itemtype', 0), x.get('name', '')))

    @cache_results(ttl=1800)
    def get_npcs_by_loottable(self, loottable_id):
        import time
        logger = logging.getLogger(__name__)
        func_start = time.time()
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            npcs = []
            db_start = time.time()
            npc_query = text("SELECT id, name, FLOOR(id/1000) as zoneidnumber FROM npc_types WHERE loottable_id = :loottable_id")
            npc_rows = list(conn.execute(npc_query, {"loottable_id": loottable_id}).fetchall())
            db_time = time.time() - db_start
            zone_time = 0
            for row in npc_rows:
                zone_start = time.time()
                zone_query = text("SELECT short_name, long_name FROM zone WHERE zoneidnumber = :zoneidnumber")
                zone = conn.execute(zone_query, {"zoneidnumber": row[2]}).fetchone()
                zone_time += time.time() - zone_start
                if zone:
                    npcs.append({
                        "npc_id": row[0],
                        "npc_name": row[1],
                        "zone_short_name": zone[0],
                        "zone_long_name": zone[1]
                    })
            func_end = time.time()
            logger.info(f"[PROFILE] get_npcs_by_loottable({loottable_id}): db={db_time:.4f}s, zone={zone_time:.4f}s, total={func_end-func_start:.4f}s, npcs={len(npcs)}")
            return npcs

    @cache_results(ttl=1800)
    def get_npcs_by_merchant(self, merchantid):
        """Return a list of NPCs (npc_id, npc_name, zone_short_name, zone_long_name) for a merchantid."""
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            npcs = []
            npc_query = text("SELECT id, name, FLOOR(id/1000) as zoneidnumber FROM npc_types WHERE merchant_id = :merchantid")
            for row in conn.execute(npc_query, {"merchantid": merchantid}).fetchall():
                zone_query = text("SELECT short_name, long_name FROM zone WHERE zoneidnumber = :zoneidnumber")
                zone = conn.execute(zone_query, {"zoneidnumber": row[2]}).fetchone()
                if zone:
                    npcs.append({
                        "npc_id": row[0],
                        "npc_name": row[1],
                        "zone_short_name": zone[0],
                        "zone_long_name": zone[1]
                    })
            return npcs

    @cache_results(ttl=1800)
    def get_item_npcs(self, item_id):
        import time
        logger = logging.getLogger(__name__)
        func_start = time.time()
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
            npcs = []
            seen = set()
            # --- Loot Table Path ---
            lootdrop_start = time.time()
            lootdrop_query = text("SELECT lootdrop_id FROM lootdrop_entries WHERE item_id = :item_id")
            lootdrop_ids = [row[0] for row in conn.execute(lootdrop_query, {"item_id": item_id}).fetchall()]
            lootdrop_time = time.time() - lootdrop_start
            loottable_ids = []
            loottable_time = 0
            get_npcs_loottable_time = 0
            if lootdrop_ids:
                loottable_start = time.time()
                loottable_query = text("SELECT loottable_id FROM loottable_entries WHERE lootdrop_id IN :lootdrop_ids")
                loottable_ids = [row[0] for row in conn.execute(loottable_query, {"lootdrop_ids": tuple(lootdrop_ids)}).fetchall()]
                loottable_time = time.time() - loottable_start
                get_npcs_loottable_start = time.time()
                for loottable_id in loottable_ids:
                    for npc in self.get_npcs_by_loottable(loottable_id):
                        key = (npc["npc_id"], npc["zone_short_name"])
                        if key not in seen:
                            npcs.append(npc)
                            seen.add(key)
                get_npcs_loottable_time = time.time() - get_npcs_loottable_start
            # --- Merchant Path ---
            merchant_start = time.time()
            merchant_query = text("SELECT merchantid FROM merchantlist WHERE item = :item_id")
            merchant_ids = [row[0] for row in conn.execute(merchant_query, {"item_id": item_id}).fetchall()]
            merchant_time = time.time() - merchant_start
            get_npcs_merchant_time = 0
            if merchant_ids:
                get_npcs_merchant_start = time.time()
                for merchantid in merchant_ids:
                    for npc in self.get_npcs_by_merchant(merchantid):
                        key = (npc["npc_id"], npc["zone_short_name"])
                        if key not in seen:
                            npcs.append(npc)
                            seen.add(key)
                get_npcs_merchant_time = time.time() - get_npcs_merchant_start
            func_end = time.time()
            logger.info(f"[PROFILE] get_item_npcs({item_id}): lootdrop={lootdrop_time:.4f}s, loottable={loottable_time:.4f}s, get_npcs_loottable={get_npcs_loottable_time:.4f}s, merchant={merchant_time:.4f}s, get_npcs_merchant={get_npcs_merchant_time:.4f}s, total={func_end-func_start:.4f}s, npcs={len(npcs)}")
            return npcs
