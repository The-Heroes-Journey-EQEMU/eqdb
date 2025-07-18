import logging
import json
import time
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.cache import get_redis_client
from logic import Item, DbStr, engine
from sqlalchemy.orm import Session
from api.db_manager import db_manager
from utils import Util, get_class_string
from api.db.zone import ZoneDB
from api.db.item import ItemDB
from api.db.npc import NPCDB
from sqlalchemy import text
from api.db.item_indexer_utils import index_item
import redis
import configparser
from api.cache import init_cache
from api.db.expansion import ExpansionDB
from utils import get_exclusion_list


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read Redis config
config = configparser.ConfigParser()
config.read(os.path.join(os.path.dirname(__file__), '..', 'configuration.ini'))
redis_config = config['redis']
redis_host = redis_config.get('host', '127.0.0.1')
redis_port = redis_config.getint('port', 6379)
redis_db = redis_config.getint('db', 0)

# Initialize Redis client and cache
client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)
init_cache(client)


def index_all_items():
    """
    Cache warming: For each zone, loop through all spawns, then all NPCs, then all items for each NPC, and index each item in Redis.
    Also builds itemZoneNpc:{item_id} lookup tables for fast enrichment.
    Only includes zones in allowed expansions and not in the exclusion list.
    """
    logger.info("Starting cache warming by spawns...")
    start_time = time.time()
    zone_db = ZoneDB()
    item_db = ItemDB()
    npc_db = NPCDB()
    expansion_db = ExpansionDB()
    exclusion_list = set(get_exclusion_list('zone'))
    allowed_expansions = set(exp['id'] for exp in expansion_db.get_enabled_expansions())

    # Get all zone short names and their expansions
    engine = db_manager.get_engine_for_table('zone')
    with engine.connect() as conn:
        zones = conn.execute(text("SELECT short_name, expansion FROM zone")).fetchall()
        zone_info = [(row[0], row[1]) for row in zones]

    total_items_indexed = set()
    processed_npcs = set()  # Track NPCs already processed
    item_zone_npc = {}  # item_id -> set of (zone_shortname, npc_id)
    for short_name, expansion_id in zone_info:
        if short_name in exclusion_list or expansion_id not in allowed_expansions:
            continue
        logger.info(f"Processing zone: {short_name}")
        spawns = zone_db.get_zone_spawns_by_short_name(short_name)
        for spawn in spawns:
            for npc in spawn.get('npcs', []):
                npc_id = npc.get('npc_id')
                if not npc_id or npc_id in processed_npcs:
                    continue
                processed_npcs.add(npc_id)
                # Get all items for this NPC (loot + merchant)
                engine_items = db_manager.get_engine_for_table('items')
                with engine_items.connect() as conn_items:
                    # Loot table
                    lootdrop_query = text("SELECT lootdrop_id FROM loottable_entries WHERE loottable_id = (SELECT loottable_id FROM npc_types WHERE id = :npc_id)")
                    lootdrop_ids = [row[0] for row in conn_items.execute(lootdrop_query, {"npc_id": npc_id}).fetchall()]
                    item_ids = set()
                    if lootdrop_ids:
                        lootdrop_entries_query = text("SELECT item_id FROM lootdrop_entries WHERE lootdrop_id IN :lootdrop_ids AND chance > 0")
                        item_id_results = conn_items.execute(lootdrop_entries_query, {"lootdrop_ids": tuple(lootdrop_ids)}).fetchall()
                        item_ids.update(row[0] for row in item_id_results)
                    # Merchant list
                    merchant_query = text("SELECT merchant_id FROM npc_types WHERE id = :npc_id")
                    merchant_ids = [row[0] for row in conn_items.execute(merchant_query, {"npc_id": npc_id}).fetchall() if row[0]]
                    if merchant_ids:
                        merchantlist_query = text("SELECT item FROM merchantlist WHERE merchantid IN :merchant_ids")
                        merchant_item_results = conn_items.execute(merchantlist_query, {"merchant_ids": tuple(merchant_ids)}).fetchall()
                        item_ids.update(row[0] for row in merchant_item_results)
                for item_id in item_ids:
                    if item_id not in total_items_indexed:
                        index_item(item_id)
                        total_items_indexed.add(item_id)
                    # Add to itemZoneNpc
                    if item_id not in item_zone_npc:
                        item_zone_npc[item_id] = set()
                    item_zone_npc[item_id].add((short_name, npc_id))
        logger.info(f"Finished zone: {short_name}")
    # Write itemZoneNpc to Redis
    for item_id, zone_npc_set in item_zone_npc.items():
        key = f"itemZoneNpc:{item_id}"
        value = json.dumps(list(zone_npc_set))
        client.set(key, value)
    end_time = time.time()
    logger.info(f"Cache warming completed in {end_time - start_time:.2f} seconds. Indexed {len(total_items_indexed)} unique items. Built itemZoneNpc for {len(item_zone_npc)} items.")

def search_items_from_redis(params):
    """
    Searches for items using the Redis indexes.
    `params` is a dictionary of search parameters.
    """
    client = get_redis_client()
    if not client:
        logger.error("Redis client not available. Cannot perform search.")
        return []

    # Start with a set of all item IDs if no other criteria is provided
    # This would be slow, so we should require at least one filter
    if not params:
        return []

    # Collect all the sets to intersect
    sets_to_intersect = []

    if 'class' in params:
        sets_to_intersect.append(f"item_idx:class:{params['class']}")
    if 'slot' in params:
        sets_to_intersect.append(f"item_idx:slot:{params['slot']}")
    if 'type' in params:
        sets_to_intersect.append(f"item_idx:type:{params['type']}")
    if 'aug' in params:
        sets_to_intersect.append("item_idx:aug:true")
    
    if 'name' in params:
        name_sets = [f"item_word:{word}" for word in params['name'].lower().split() if len(word) > 2]
        if name_sets:
            # Intersect the name sets first
            name_result_key = f"tmp:name_search:{params['name']}"
            client.sinterstore(name_result_key, name_sets)
            client.expire(name_result_key, 60) # Expire temporary key
            sets_to_intersect.append(name_result_key)

    if 'expansion' in params:
        sets_to_intersect.append(f"item_idx:expansion:{params['expansion']}")
    if 'elemental_damage_type' in params:
        sets_to_intersect.append(f"item_idx:elemental:{params['elemental_damage_type']}")
    if 'bane_damage_type' in params:
        sets_to_intersect.append(f"item_idx:bane:{params['bane_damage_type']}")
    if 'proc' in params and params['proc'] == 'True':
        sets_to_intersect.append("item_idx:proc:true")
    if 'click' in params and params['click'] == 'True':
        sets_to_intersect.append("item_idx:click:true")
    if 'pet_search' in params and params['pet_search']:
        sets_to_intersect.append("item_idx:pet:true")
    if 'sympathetic' in params and params['sympathetic'] != 'None':
        sets_to_intersect.append("item_idx:sympathetic:true")

    if not sets_to_intersect:
        return []

    # Perform the intersection
    result_key = f"tmp:search_result:{json.dumps(params, sort_keys=True)}"
    client.sinterstore(result_key, sets_to_intersect)
    client.expire(result_key, 60) # Expire temporary key

    item_ids = [int(item_id) for item_id in client.smembers(result_key)]

    # Fetch full item details from the HASH cache
    items = []
    for item_id in item_ids:
        item_details = client.hgetall(f"item:{item_id}")
        if item_details:
            def decode_if_bytes(val):
                return val.decode('utf-8') if isinstance(val, bytes) else val
            items.append({decode_if_bytes(k): decode_if_bytes(v) for k, v in item_details.items()})
    
    return items

if __name__ == "__main__":
    index_all_items()
