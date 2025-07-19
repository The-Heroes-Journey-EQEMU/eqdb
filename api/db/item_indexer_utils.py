from api.cache import get_redis_client
from logic import Item
from sqlalchemy.orm import Session
from api.db_manager import db_manager
from utils import Util, get_class_string
import logging

logger = logging.getLogger(__name__)

def index_item(item_id):
    """Indexes a single item into Redis."""
    client = get_redis_client()
    if not client:
        logger.error("Redis client not available. Cannot perform indexing.")
        return

    engine = db_manager.get_engine_for_table('items')
    with Session(bind=engine) as session:
        item = session.query(Item).filter(Item.id == item_id).first()
        if not item:
            return

        # Use canonical Python mappings
        class_map = {i: get_class_string(i) for i in range(1, 17)}
        slot_map = Util.get_categorized_item_slots()
        type_map = Util.get_categorized_item_types()

        # 1. Item Detail Cache (HASH)
        item_key = f"item:{item.id}"
        item_details = {k: str(v) if v is not None else "" for k, v in item.__dict__.items() if not k.startswith('_')}
        client.hset(item_key, mapping=item_details)

        # 2. Search and Filter Indexes (SET)
        if item.classes:
            for class_id, class_name in class_map.items():
                if item.classes & (1 << (class_id - 1)):
                    client.sadd(f"item_idx:class:{class_name}", item.id)
        if item.slots:
            for slot_id, slot_name in slot_map.items():
                if item.slots & slot_id:
                    client.sadd(f"item_idx:slot:{slot_name}", item.id)
        if item.itemtype in type_map:
            client.sadd(f"item_idx:type:{type_map[item.itemtype]}", item.id)
        if item.augtype > 0:
            client.sadd("item_idx:aug:true", item.id)

        # 3. Name-Based Search Index (SET)
        if item.Name:
            for word in item.Name.lower().split():
                if len(word) > 2:
                    client.sadd(f"item_word:{word}", item.id)

        # 4. Advanced Search Indexes (SET)
        # Expansion
        if hasattr(item, 'expansion_name') and item.expansion_name:
            client.sadd(f"item_idx:expansion:{item.expansion_name}", item.id)
        # Elemental damage type
        if hasattr(item, 'elemental_damage_type') and item.elemental_damage_type:
            client.sadd(f"item_idx:elemental:{item.elemental_damage_type}", item.id)
        # Bane damage type
        if hasattr(item, 'bane_damage_type') and item.bane_damage_type:
            client.sadd(f"item_idx:bane:{item.bane_damage_type}", item.id)
        # Proc
        if hasattr(item, 'proc') and item.proc:
            client.sadd("item_idx:proc:true", item.id)
        # Click
        if hasattr(item, 'click') and item.click:
            client.sadd("item_idx:click:true", item.id)
        # Pet effect
        if hasattr(item, 'pet') and item.pet:
            client.sadd("item_idx:pet:true", item.id)
        # Sympathetic effect
        if hasattr(item, 'sympathetic') and item.sympathetic:
            client.sadd("item_idx:sympathetic:true", item.id)

    # logger.info(f"Successfully indexed item {item_id}.") 