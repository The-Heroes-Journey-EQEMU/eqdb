import logging
from flask import request, jsonify
from flask_restx import Resource, fields
from sqlalchemy import text
from datetime import datetime
from api import v1
from api.db.item import ItemDB
from api.db.spell import SpellDB
from api.db.npc import NPCDB
from api.db.zone import ZoneDB
from api.db.tradeskill import TradeskillDB
from api.db.quest import QuestDB
from api.db.expansion import ExpansionDB
from api.db.expansion_items import ExpansionItemsDB
from api.redis_item_indexer import index_all_items, search_items_from_redis
from api.db.item_indexer_utils import index_item
from .auth import auth
from .auth_routes import auth_ns
from .middleware import optional_auth, write_auth_required, admin_required
from .cache import clear_cache
from .models import create_models
from utils import get_type_string, get_slot_string, Util, get_all_skills, get_class_string
import time
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize database connections
item_db = ItemDB()
spell_db = SpellDB()
npc_db = NPCDB()
zone_db = ZoneDB()
tradeskill_db = TradeskillDB()
quest_db = QuestDB()
expansion_db = ExpansionDB()
expansion_items_db = ExpansionItemsDB('sqlite:///expansion_items.db')

# Define error response models
error_model = v1.model('Error', {
    'message': fields.String(description='Error message', example='Item not found')
})

# Define response models with examples
item_model = v1.model('Item', {
    'id': fields.Integer(description='Item ID', example=12345),
    'name': fields.String(description='Item name', example='Fine Steel Dagger'),
    'type': fields.String(description='Item type', example='Weapon'),
    'serialized': fields.String(description='Serialized item data', example='{"stats": {"damage": "1-5"}}'),
    'expansion_name': fields.String(description='Expansion name', example='Classic'),
    'itemtype_name': fields.String(description='Human-readable item type', example='2H Slashing'),
    'slot_names': fields.String(description='Human-readable slot names (space-separated)', example='Primary Secondary'),
})

spell_model = v1.model('Spell', {
    'id': fields.Integer(description='Spell ID', example=12345),
    'name': fields.String(description='Spell name', example='Minor Healing'),
    'class': fields.String(description='Spell class', example='Cleric'),
    'level': fields.Integer(description='Spell level', example=1)
})

npc_model = v1.model('NPC', {
    'id': fields.Integer(description='NPC ID', example=12345),
    'name': fields.String(description='NPC name', example='Guard'),
    'zone': fields.String(description='Zone name', example='North Qeynos'),
    'level': fields.Integer(description='NPC level', example=5)
})

zone_model = v1.model('Zone', {
    'short_name': fields.String(description='Zone short name', example='qeynos'),
    'long_name': fields.String(description='Zone full name', example='North Qeynos'),
    'expansion_id': fields.Integer(description='Expansion ID', example=0),
    'expansion_name': fields.String(description='Expansion name', example='Classic'),
    'min_level': fields.Integer(description='Minimum level for the zone', example=1),
    'max_level': fields.Integer(description='Maximum level for the zone', example=25)
})

connected_zone_model = v1.model('ConnectedZone', {
    'target_zone_id': fields.Integer(description='Connected zone ID', example=2),
    'short_name': fields.String(description='Connected zone short name', example='qeynos2'),
    'long_name': fields.String(description='Connected zone long name', example='South Qeynos')
})

tradeskill_model = v1.model('Tradeskill', {
    'id': fields.Integer(description='Tradeskill ID', example=59),
    'name': fields.String(description='Tradeskill name', example='Alchemy'),
    'skill': fields.String(description='Required skill', example='Alchemy'),
    'recipe_count': fields.Integer(description='Number of recipes in this tradeskill', example=150)
})

# Define component item model
component_item_model = v1.model('ComponentItem', {
    'item_id': fields.Integer(description='Item ID', example=12345),
    'item_name': fields.String(description='Item name', example='Fine Steel'),
    'count': fields.Integer(description='Quantity needed', example=2)
})

recipe_model = v1.model('Recipe', {
    'id': fields.Integer(description='Recipe ID', example=12345),
    'name': fields.String(description='Recipe name', example='Fine Steel Dagger'),
    'tradeskill': fields.Integer(description='Tradeskill skill number', example=63),
    'tradeskill_name': fields.String(description='Tradeskill name', example='Blacksmithing'),
    'skillneeded': fields.Integer(description='Required skill level', example=100),
    'trivial': fields.Integer(description='Trivial skill level', example=150),
    'nofail': fields.Integer(description='No fail flag', example=0),
    'replace_container': fields.Integer(description='Replace container flag', example=0),
    'must_learn': fields.Integer(description='Must learn flag', example=0),
    'enabled': fields.Integer(description='Enabled flag', example=1),
    'min_expansion': fields.Integer(description='Minimum expansion required', example=0),
    'components': fields.List(fields.Nested(component_item_model), description='Items needed for the combine'),
    'success_items': fields.List(fields.Nested(component_item_model), description='Items produced on success'),
    'fail_items': fields.List(fields.Nested(component_item_model), description='Items produced on failure')
})

expansion_model = v1.model('Expansion', {
    'id': fields.Integer(description='Expansion ID', example=0),
    'name': fields.String(description='Expansion name', example='Classic'),
    'short_name': fields.String(description='Expansion short name', example='classic'),
    'release_date': fields.String(description='Expansion release date', example='1999-03-16'),
    'description': fields.String(description='Expansion description', example='Original EverQuest release')
})

quest_model = v1.model('Quest', {
    'npc_id': fields.Integer(description='NPC ID', example=12345),
    'npc_name': fields.String(description='NPC name', example='Guard Captain'),
    'quest_name': fields.String(description='Quest name', example='Quest from Guard Captain'),
    'level': fields.Integer(description='NPC level', example=10),
    'zone_name': fields.String(description='Zone short name', example='qeynos'),
    'zone_long_name': fields.String(description='Zone full name', example='North Qeynos'),
    'zone_expansion': fields.Integer(description='Zone expansion number', example=0),
    'item_id': fields.Integer(description='Quest item ID', example=12345),
    'item_name': fields.String(description='Quest item name', example='Fine Steel Dagger'),
    'itemtype': fields.Integer(description='Item type', example=1),
    'classes': fields.Integer(description='Classes that can use this item', example=65535),
    'slots': fields.Integer(description='Equipment slots', example=0),
    'is_quest_item': fields.Boolean(description='Whether this is a quest item', example=True),
    'expansion': fields.String(description='Expansion this quest item is from', example='Classic')
})

expansions_list_model = v1.model('ExpansionsList', {
    'expansions': fields.List(fields.Nested(expansion_model), description='List of available expansions')
})

zones_by_expansion_model = v1.model('ZonesByExpansion', {
    'expansion_name': fields.Raw(description='Zones grouped by expansion')
})

zones_in_expansion_model = v1.model('ZonesInExpansion', {
    'zones': fields.List(fields.Nested(zone_model), description='List of zones in expansion')
})

expansion_item_model = v1.model('ExpansionItem', {
    'id': fields.Integer(description='Database ID', example=1),
    'item_id': fields.Integer(description='Item ID', example=12345),
    'expansion_id': fields.Integer(description='Expansion ID', example=0),
    'item_type': fields.String(description='Item type', example='regular', enum=['regular', 'tradeskill', 'special', 'custom']),
    'is_custom': fields.Boolean(description='Whether this is a custom item', example=False),
    'added_date': fields.DateTime(description='Date added to database', example='2024-01-01T00:00:00'),
    'notes': fields.String(description='Additional notes', example='Custom server item'),
    'item_name': fields.String(description='Item Name'),
    'icon': fields.Integer(description='Item Icon ID')
})

expansion_items_list_model = v1.model('ExpansionItemsList', {
    'items': fields.List(fields.Nested(expansion_item_model), description='List of expansion items')
})

expansion_summary_model = v1.model('ExpansionSummary', {
    'expansion_id': fields.Integer(description='Expansion ID', example=0),
    'regular': fields.Integer(description='Number of regular items', example=100),
    'tradeskill': fields.Integer(description='Number of tradeskill items', example=50),
    'special': fields.Integer(description='Number of special items', example=10),
    'custom': fields.Integer(description='Number of custom items', example=5),
    'total': fields.Integer(description='Total number of items', example=165)
})

expansion_summary_list_model = v1.model('ExpansionSummaryList', {
    'summaries': fields.List(fields.Nested(expansion_summary_model), description='List of expansion summaries')
})

success_message_model = v1.model('SuccessMessage', {
    'message': fields.String(description='Success message', example='Custom item removed successfully')
})

import_result_model = v1.model('ImportResult', {
    'message': fields.String(description='Import result message', example='Import completed successfully'),
    'total_imported': fields.Integer(description='Number of items imported', example=3319)
})

# Weight Set models
weight_model = v1.model('Weight', {
    'stat': fields.String(description='Stat name', example='hp'),
    'value': fields.Float(description='Weight value', example=1.5)
})

weight_set_model = v1.model('WeightSet', {
    'id': fields.Integer(description='Weight set ID', example=1),
    'name': fields.String(description='Weight set name', example='Tank Weights'),
    'description': fields.String(description='Weight set description', example='Weights optimized for tanking'),
    'weights': fields.List(fields.Nested(weight_model), description='List of stat weights'),
    'created_at': fields.String(description='Creation date'),
    'updated_at': fields.String(description='Last update date')
})

weight_set_create_model = v1.model('WeightSetCreate', {
    'name': fields.String(required=True, description='Weight set name', example='Tank Weights'),
    'description': fields.String(description='Weight set description', example='Weights optimized for tanking'),
    'weights': fields.List(fields.Nested(weight_model), required=True, description='List of stat weights')
})

weight_set_update_model = v1.model('WeightSetUpdate', {
    'name': fields.String(description='Weight set name', example='Tank Weights'),
    'description': fields.String(description='Weight set description', example='Weights optimized for tanking'),
    'weights': fields.List(fields.Nested(weight_model), description='List of stat weights')
})

weight_sets_list_model = v1.model('WeightSetsList', {
    'weight_sets': fields.List(fields.Nested(weight_set_model), description='List of user weight sets')
})



def format_date(date_val):
    """Format date to match production API format, robust to type and value."""
    if not date_val:
        return None
    if isinstance(date_val, datetime):
        return date_val.strftime('%a, %d %b %Y %H:%M:%S GMT')
    if isinstance(date_val, str):
        # Try ISO format first
        try:
            dt = datetime.fromisoformat(date_val.replace('Z', '+00:00'))
            return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
        except Exception:
            pass
        # Try parsing common formats
        for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%a, %d %b %Y %H:%M:%S GMT'):
            try:
                dt = datetime.strptime(date_val, fmt)
                return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
            except Exception:
                continue
    return None

def format_item_response(item_data):
    """Format item data to match production API format."""
    # Convert datetime fields to ISO strings
    for key, value in item_data.items():
        if isinstance(value, (datetime,)):
            item_data[key] = value.isoformat()
    # Convert empty strings to None
    for key, value in item_data.items():
        if value == "":
            item_data[key] = None
    # Ensure all fields that are None are converted to empty strings
    for key, value in item_data.items():
        if value is None:
            item_data[key] = ""
    # Ensure serialized is None if it's an empty string
    if item_data.get('serialized') == "":
        item_data['serialized'] = None
    return item_data

def format_spell_response(spell_data, all_keys=None):
    """Format spell data to match production API format."""
    # Convert datetime fields to ISO strings
    for key, value in spell_data.items():
        if isinstance(value, (datetime,)):
            spell_data[key] = value.isoformat()
    # Convert empty strings to None
    for key, value in spell_data.items():
        if value == "":
            spell_data[key] = None
    # Ensure all fields that are None are converted to empty strings
    for key, value in spell_data.items():
        if value is None:
            spell_data[key] = ""
    # Ensure all expected keys are present
    if all_keys:
        for key in all_keys:
            if key not in spell_data:
                spell_data[key] = ""
    return spell_data

def format_npc_response(npc_data, all_keys=None):
    """Format NPC data to match production API format."""
    # Convert datetime fields to ISO strings
    for key, value in npc_data.items():
        if isinstance(value, (datetime,)):
            npc_data[key] = value.isoformat()
    # Convert empty strings to None
    for key, value in npc_data.items():
        if value == "":
            npc_data[key] = None
    # Ensure all fields that are None are converted to empty strings
    for key, value in npc_data.items():
        if value is None:
            npc_data[key] = ""
    # Ensure all expected keys are present
    if all_keys:
        for key in all_keys:
            if key not in npc_data:
                npc_data[key] = ""
    return npc_data

def format_zone_response(zone_data, all_keys=None):
    """Format zone data to match production API format."""
    # Convert datetime fields to ISO strings
    for key, value in zone_data.items():
        if isinstance(value, (datetime,)):
            zone_data[key] = value.isoformat()
    # Convert empty strings to None
    for key, value in zone_data.items():
        if value == "":
            zone_data[key] = None
    # Ensure all fields that are None are converted to empty strings
    for key, value in zone_data.items():
        if value is None:
            zone_data[key] = ""
    # Ensure all expected keys are present
    if all_keys:
        for key in all_keys:
            if key not in zone_data:
                zone_data[key] = ""
    return zone_data

# Define all resource classes
@v1.route('/items')
class ItemResource(Resource):
    @optional_auth
    @v1.doc('get_items',
        params={
            'id': {'description': 'Search items by item ID', 'type': 'integer', 'example': 12345},
            'name': {'description': 'Search items by partial name (50 results maximum)', 'type': 'string', 'example': 'dagger'},
            'item_type': {'description': 'Filter items by type', 'type': 'string', 'enum': list(Util.get_categorized_item_types().values()), 'example': 'Weapon'},
            'tradeskill_only': {'description': 'Filter for tradeskill items', 'type': 'boolean', 'example': False},
            'equippable_only': {'description': 'Filter for equippable items', 'type': 'boolean', 'example': False},
            'exclude_glamours': {'description': 'Exclude glamour items', 'type': 'boolean', 'example': False},
            'only_augments': {'description': 'Filter for augmentations only', 'type': 'boolean', 'example': False},
            'item_slot': {'description': 'Filter by item slot', 'type': 'string', 'enum': list(Util.get_categorized_item_slots().values()), 'example': 'Primary'},
            'itemtype_name': {
                'description': 'Filter by human-readable item type',
                'type': 'string',
                'enum': list(Util.get_categorized_item_types().values()),
                'example': '2H Slashing'
            },
            'slot_names': {
                'description': 'Filter by human-readable slot name',
                'type': 'string',
                'enum': list(Util.get_categorized_item_slots().values()),
                'example': 'Primary'
            },
            'itemclass_name': {
                'description': 'Filter by item class (only Weapon or Armor are supported)',
                'type': 'string',
                'enum': ['Weapon', 'Armor'],
                'example': 'Weapon'
            },
            'stat_filters': {'description': 'Array of stat filter objects: {stat: string, value: int}', 'type': 'array', 'items': {'type': 'object', 'properties': {'stat': {'type': 'string'}, 'value': {'type': 'integer'}}}, 'example': [{'stat': 'hp', 'value': 50}]},
            'stat_weights': {'description': 'Array of stat weight objects: {stat: string, weight: float}', 'type': 'array', 'items': {'type': 'object', 'properties': {'stat': {'type': 'string'}, 'weight': {'type': 'number'}}}, 'example': [{'stat': 'damage', 'weight': 1.5}]},
            'exclude_expansions': {'description': 'Array of expansion names to exclude', 'type': 'array', 'items': {'type': 'string'}, 'example': ['Kunark', 'Velious']},
            'elemental_damage_type': {'description': 'Weapon elemental damage type', 'type': 'string', 'enum': ['Magic', 'Fire', 'Cold', 'Poison', 'Disease', 'Chromatic', 'Prismatic', 'Phys', 'Corruption'], 'example': 'Fire'},
            'bane_damage_type': {'description': 'Weapon bane damage type', 'type': 'string', 'enum': ['body_14', 'race_217', 'race_236'], 'example': 'body_14'},
            'proc': {'description': 'Weapons with proc: None (include), True (only)', 'type': 'string', 'enum': ['None', 'True'], 'example': 'None'},
            'click': {'description': 'Items with click effect: None (include), True (only)', 'type': 'string', 'enum': ['None', 'True'], 'example': 'None'},
            'proc_level': {'description': 'Required level to proc', 'type': 'integer', 'example': 0},
            'click_level': {'description': 'Required level to click', 'type': 'integer', 'example': 0},
            'skillmodtype': {'description': 'Skill mod type', 'type': 'string', 'enum': [entry for skill in get_all_skills() for entry in skill.values()], 'example': 'Abjuration'},
            'expansion': {'description': 'Expansion name', 'type': 'string', 'enum': [], 'example': 'Classic'},
            'pet_search': {'description': 'Search for pet items', 'type': 'boolean', 'example': False},
            'show_full_detail': {'description': 'Show item detail table', 'type': 'boolean', 'example': False},
            'show_weight_detail': {'description': 'Show only weight details (requires one weight)', 'type': 'boolean', 'example': False},
            'ignore_zero': {'description': 'Include zero weight items (requires one weight)', 'type': 'boolean', 'example': False},
            'sympathetic': {'description': 'Sympathetic effect filter', 'type': 'string', 'enum': ['None', 'all_strike', '24356', '24357', '24358', '24359', '24360', '24361', '24362', '24363', '24364', '24365', 'all_heal', '24434', '24435', '24436', '24437', '24438', '24439', '24440', '24441', '24442', '24443'], 'example': 'None'},
            'page': {
                'description': 'Page number for pagination (starts at 1)',
                'type': 'integer',
                'example': 1
            },
            'page_size': {
                'description': 'Number of items per page (default 50, max 200)',
                'type': 'integer',
                'example': 50
            }
        },
        responses={
            200: ('Success', fields.Raw(description='Paginated item search results with total, page, page_size, and pages. Each item includes all stats, effects, icons, and nested spell/effect info needed for the results table.')),
            400: ('Invalid parameters', error_model),
            404: ('Item not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get items
        
        Get items using the following parameters:
        * id: Search items by item ID (optional)
        * name: Search items by partial name (optional, 50 results maximum)
        * item_type: Filter items by type (optional)
        
        Returns a list of items matching the criteria.
        """
        try:
            item_id = request.args.get('id', type=int)
            item_type_map = item_db.get_item_types()

            if item_id:
                items = item_db.get_item_details(item_id)
            else:
                name = request.args.get('name')
                item_type = request.args.get('item_type')
                tradeskill_only = request.args.get('tradeskill_only', type=lambda v: v.lower() == 'true')
                equippable_only = request.args.get('equippable_only', type=lambda v: v.lower() == 'true')
                exclude_glamours = request.args.get('exclude_glamours', type=lambda v: v.lower() == 'true')
                only_augments = request.args.get('only_augments', type=lambda v: v.lower() == 'true')
                item_slot = request.args.get('item_slot')
                itemtype_name = request.args.get('itemtype_name')
                slot_names = request.args.get('slot_names')
                itemclass_name = request.args.get('itemclass_name')
                page = request.args.get('page', default=1, type=int)
                page_size = request.args.get('page_size', default=50, type=int)

                result = item_db.search_items(
                    name=name, 
                    item_type=item_type,
                    tradeskill_only=tradeskill_only,
                    equippable_only=equippable_only,
                    exclude_glamours=exclude_glamours,
                    only_augments=only_augments,
                    item_slot=item_slot,
                    itemtype_name=itemtype_name,
                    slot_names=slot_names,
                    itemclass_name=itemclass_name,
                    page=page,
                    page_size=page_size
                )
                items = result['results']
                total = result['total']
                page = result['page']
                page_size = result['page_size']
                pages = result['pages']
            
            if not items:
                return {'message': 'No items found', 'total': total, 'page': page, 'page_size': page_size, 'pages': pages}, 404
            
            # Format response
            if isinstance(items, list):
                formatted_items = []
                for item in items:
                    new_item = dict(item)
                    item_type_id = new_item.get('itemtype')
                    # Use Util mapping for type
                    type_map = Util.get_categorized_item_types()
                    if item_type_id is not None:
                        new_item['type'] = type_map.get(item_type_id, get_type_string(item_type_id))
                        if 'itemtype' in new_item:
                            del new_item['itemtype']
                    else:
                        new_item['type'] = 'Unknown'
                    formatted_items.append(format_item_response(new_item))
                return {
                    'results': formatted_items,
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'pages': pages
                }
            else:
                # Single item
                item = items
                item_type_id = item.get('itemtype')
                if item_type_id is not None:
                    item['type'] = type_map.get(item_type_id, get_type_string(item_type_id))
                    if 'itemtype' in item:
                        del item['itemtype']
                else:
                    item['type'] = 'Unknown'
                return format_item_response(item)
            
        except Exception as e:
            v1.abort(500, f"Error retrieving items: {str(e)}")

@v1.route('/items/types')
class ItemTypesResource(Resource):
    @optional_auth
    @v1.doc('get_item_types',
        responses={
            200: ('Success', fields.Raw(description='A dictionary of item types, mapping type ID to type name')),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get all item types"""
        try:
            return item_db.get_item_types()
        except Exception as e:
            v1.abort(500, f"Error retrieving item types: {str(e)}")

@v1.route('/items/slots')
class ItemSlotsResource(Resource):
    @optional_auth
    @v1.doc('get_item_slots',
        responses={
            200: ('Success', fields.Raw(description='A dictionary of item slots, mapping slot bitmask to slot name')),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get all item slots"""
        try:
            return item_db.get_item_slots()
        except Exception as e:
            v1.abort(500, f"Error retrieving item slots: {str(e)}")

@v1.route('/items/details/<int:item_id>')
class ItemDetailsResource(Resource):
    @optional_auth
    @v1.doc('get_item_details',
        params={
            'item_id': {'description': 'Item ID to get exhaustive details for', 'type': 'integer', 'in': 'path', 'example': 12345}
        },
        responses={
            200: ('Success', fields.Raw(description='Exhaustive item details including both enriched and raw data, NPCs, spells, effects, and all available information')),
            404: ('Item not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self, item_id):
        """Get exhaustive details for a single item by ID
        
        Returns comprehensive item information including:
        * All raw database fields
        * Enriched human-readable fields (type names, slot names, etc.)
        * NPCs that drop this item
        * Associated spells and effects
        * Expansion information
        * Quest item status
        * All available metadata
        
        This endpoint provides the most complete item information available.
        """
        try:
            # Get basic item details
            item_details = item_db.get_item_details(item_id)
            if not item_details:
                v1.abort(404, f"Item with ID {item_id} not found")
                return
            
            # Get NPCs that drop this item
            npcs = item_db.get_item_npcs(item_id)
            
            # Get associated spells if any
            spells = []
            if item_details.get('clicktype') > 0:
                spell_details = spell_db.get_spell_raw_data(spell_id=item_details['clicktype'])
                if spell_details:
                    spells.append({
                        'type': 'click_effect',
                        'spell_id': item_details['clicktype'],
                        'spell_data': format_spell_response(spell_details)
                    })
            
            if item_details.get('worneffect') > 0:
                spell_details = spell_db.get_spell_raw_data(spell_id=item_details['worneffect'])
                if spell_details:
                    spells.append({
                        'type': 'worn_effect',
                        'spell_id': item_details['worneffect'],
                        'spell_data': format_spell_response(spell_details)
                    })
            
            if item_details.get('focuseffect') > 0:
                spell_details = spell_db.get_spell_raw_data(spell_id=item_details['focuseffect'])
                if spell_details:
                    spells.append({
                        'type': 'focus_effect',
                        'spell_id': item_details['focuseffect'],
                        'spell_data': format_spell_response(spell_details)
                    })
            
            if item_details.get('bardeffect') > 0:
                spell_details = spell_db.get_spell_raw_data(spell_id=item_details['bardeffect'])
                if spell_details:
                    spells.append({
                        'type': 'bard_effect',
                        'spell_id': item_details['bardeffect'],
                        'spell_data': format_spell_response(spell_details)
                    })
            
            if item_details.get('proceffect') > 0:
                spell_details = spell_db.get_spell_raw_data(spell_id=item_details['proceffect'])
                if spell_details:
                    spells.append({
                        'type': 'proc_effect',
                        'spell_id': item_details['proceffect'],
                        'spell_data': format_spell_response(spell_details)
                    })
            
            # Build comprehensive response
            response = {
                'item_id': item_id,
                'raw_data': item_details,  # All raw database fields
                'enriched_data': {
                    'id': item_details.get('id'),
                    'name': item_details.get('name'),
                    'type': item_details.get('itemtype_name'),
                    'slot_names': item_details.get('slot_names'),
                    'expansion_name': item_details.get('expansion_name'),
                    'is_quest_item': item_details.get('is_quest_item', False),
                    'itemclass_name': self._get_item_class_name(item_details.get('itemtype')),
                    'human_readable': {
                        'type': item_details.get('itemtype_name'),
                        'slots': item_details.get('slot_names'),
                        'expansion': item_details.get('expansion_name'),
                        'classes': self._get_class_names(item_details.get('classes')),
                        'races': self._get_race_names(item_details.get('races')),
                        'deity': self._get_deity_name(item_details.get('deity')),
                        'material': self._get_material_name(item_details.get('material')),
                        'color': self._get_color_name(item_details.get('color')),
                        'size': self._get_size_name(item_details.get('size'))
                    }
                },
                'npcs': npcs,  # NPCs that drop this item
                'spells': spells,  # Associated spells and effects
                'metadata': {
                    'last_updated': format_date(datetime.now()),
                    'data_sources': ['items', 'npcs', 'spells', 'expansions'],
                    'enriched_fields': ['type', 'slots', 'expansion', 'classes', 'races', 'deity', 'material', 'color', 'size']
                }
            }
            
            return response
            
        except Exception as e:
            v1.abort(500, f"Error retrieving item details: {str(e)}")
    
    def _get_item_class_name(self, itemtype):
        """Get item class name (Weapon/Armor) based on itemtype"""
        if not itemtype:
            return None
        
        weapon_types = list(Util.get_categorized_item_types('weapon').keys())
        armor_types = list(Util.get_categorized_item_types('armor').keys())
        
        if itemtype in weapon_types:
            return 'Weapon'
        elif itemtype in armor_types:
            return 'Armor'
        return None
    
    def _get_class_names(self, classes_bitmask):
        """Convert classes bitmask to list of class names"""
        if not classes_bitmask:
            return []
        
        class_names = []
        for i in range(1, 17):
            if classes_bitmask & (1 << (i - 1)):
                class_names.append(get_class_string(i))
        return class_names
    
    def _get_race_names(self, races_bitmask):
        """Convert races bitmask to list of race names"""
        if not races_bitmask:
            return []
        
        # Basic race mapping - could be expanded
        race_map = {
            1: 'Human', 2: 'Barbarian', 4: 'Erudite', 8: 'Wood Elf',
            16: 'High Elf', 32: 'Dark Elf', 64: 'Half Elf', 128: 'Dwarf',
            256: 'Troll', 512: 'Ogre', 1024: 'Halfling', 2048: 'Gnome',
            4096: 'Iksar', 8192: 'Vah Shir', 16384: 'Froglok'
        }
        
        race_names = []
        for race_id, race_name in race_map.items():
            if races_bitmask & race_id:
                race_names.append(race_name)
        return race_names
    
    def _get_deity_name(self, deity_id):
        """Get deity name by ID"""
        if not deity_id:
            return None
        
        # Basic deity mapping - could be expanded
        deity_map = {
            1: 'Agnostic', 2: 'Bertoxxulous', 3: 'Brell Serilis', 4: 'Cazic-Thule',
            5: 'Erollisi Marr', 6: 'Bristlebane', 7: 'Innoruuk', 8: 'Karana',
            9: 'Mithaniel Marr', 10: 'Prexus', 11: 'Quellious', 12: 'Rallos Zek',
            13: 'Rodcet Nife', 14: 'Solusek Ro', 15: 'The Tribunal', 16: 'Tunare',
            17: 'Veeshan'
        }
        return deity_map.get(deity_id, f'Unknown Deity {deity_id}')
    
    def _get_material_name(self, material_id):
        """Get material name by ID"""
        if not material_id:
            return None
        
        # Basic material mapping - could be expanded
        material_map = {
            0: 'Cloth', 1: 'Leather', 2: 'Chain', 3: 'Plate',
            4: 'Velious', 5: 'Velious', 6: 'Velious', 7: 'Velious',
            8: 'Velious', 9: 'Velious', 10: 'Velious', 11: 'Velious',
            12: 'Velious', 13: 'Velious', 14: 'Velious', 15: 'Velious'
        }
        return material_map.get(material_id, f'Unknown Material {material_id}')
    
    def _get_color_name(self, color_id):
        """Get color name by ID"""
        if not color_id:
            return None
        
        # Basic color mapping - could be expanded
        color_map = {
            0: 'None', 1: 'Red', 2: 'Blue', 3: 'Green', 4: 'Yellow',
            5: 'Purple', 6: 'Orange', 7: 'White', 8: 'Black'
        }
        return color_map.get(color_id, f'Unknown Color {color_id}')
    
    def _get_size_name(self, size_id):
        """Get size name by ID"""
        if not size_id:
            return None
        
        size_map = {
            0: 'Tiny', 1: 'Small', 2: 'Medium', 3: 'Large', 4: 'Giant'
        }
        return size_map.get(size_id, f'Unknown Size {size_id}')

@v1.route('/items/reindex')
class ItemReindexResource(Resource):
    @write_auth_required
    @v1.doc('reindex_items',
        responses={
            200: ('Success', success_message_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def post(self):
        """Re-index all items into Redis"""
        try:
            index_all_items()
            return {'message': 'Item re-indexing started successfully.'}
        except Exception as e:
            v1.abort(500, f"Error starting item re-indexing: {str(e)}")

@v1.route('/spells')
class SpellResource(Resource):
    @optional_auth
    @v1.doc('get_spells',
        params={
            'id': {'description': 'Search spells by spell ID', 'type': 'integer', 'example': 12345},
            'name': {'description': 'Search spells by partial name (50 results maximum)', 'type': 'string', 'example': 'heal'}
        },
        responses={
            200: ('Success', [spell_model]),
            400: ('Invalid parameters', error_model),
            404: ('Spell not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get spells
        
        Get spells using the following parameters:
        * id: Search spells by spell ID (optional)
        * name: Search spells by partial name (optional, 50 results maximum)
        
        Returns a list of spells matching the criteria.
        """
        try:
            spell_id = request.args.get('id', type=int)
            name = request.args.get('name')
        
            # Get spells from database
            spells = spell_db.get_spell_raw_data(spell_id=spell_id, spell_name=name)
            
            if not spells:
                v1.abort(404, "No spells found")
            
            # Format response
            if isinstance(spells, list):
                formatted_spells = []
                for spell in spells:
                    formatted_spell = format_spell_response(spell)
                    formatted_spells.append(formatted_spell)
                return formatted_spells
            else:
                # Single spell
                return format_spell_response(spells)
            
        except Exception as e:
            v1.abort(500, f"Error retrieving spells: {str(e)}")

_SPELL_CLASS_NAME_MAP = {
    "bard": "Bard", "beastlord": "Beastlord", "berserker": "Berserker", "cleric": "Cleric",
    "druid": "Druid", "enchanter": "Enchanter", "magician": "Magician", "monk": "Monk",
    "necromancer": "Necromancer", "paladin": "Paladin", "ranger": "Ranger", "rogue": "Rogue",
    "shadowknight": "Shadow Knight", "shaman": "Shaman", "warrior": "Warrior", "wizard": "Wizard"
}

@v1.route('/spells/classes')
class SpellClassesResource(Resource):
    @optional_auth
    @v1.doc('get_spell_classes',
        responses={
            200: ('Success', fields.List(fields.String, description='List of spellcasting classes')),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get a list of all spellcasting classes"""
        return sorted(list(_SPELL_CLASS_NAME_MAP.values()))

@v1.route('/spells/list/<string:class_names>')
class SpellsByClassResource(Resource):
    @optional_auth
    @v1.doc('get_spells_by_class',
        params={
            'class_names': {'description': 'Comma-separated list of class names', 'type': 'string', 'in': 'path', 'example': 'cleric,druid'}
        },
        responses={
            200: ('Success', fields.Raw(description='Spells grouped by class and level')),
            404: ('Class not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self, class_names):
        """Get all spells for specific classes, grouped by level"""
        min_level = request.args.get('min_level', default=1, type=int)
        max_level = request.args.get('max_level', default=65, type=int)
        
        class_list = [name.strip() for name in class_names.split(',')]
        
        all_spells_data = {}
        
        try:
            for class_name in class_list:
                # normalizing by removing halflings... actually hyphens
                normalized_name = class_name.replace('-', '').lower()
                proper_name = _SPELL_CLASS_NAME_MAP.get(normalized_name)

                if not proper_name:
                    logger.warning(f"Could not find proper name for class: {class_name}")
                    continue

                data = spell_db.get_spells_by_class_api(proper_name, min_level, max_level)
                if data and not data.get('error'):
                    all_spells_data[class_name] = data
            
            if not all_spells_data:
                v1.abort(404, f"No spells found for classes {class_names}")
                
            return all_spells_data
        except Exception as e:
            v1.abort(500, f"Error retrieving spells for classes {class_names}: {str(e)}")

@v1.route('/npcs')
class NPCResource(Resource):
    @optional_auth
    @v1.doc('get_npcs',
        params={
            'id': {'description': 'Search NPCs by NPC ID', 'type': 'integer', 'example': 12345},
            'name': {'description': 'Search NPCs by partial name (50 results maximum)', 'type': 'string', 'example': 'guard'},
            'zone': {'description': 'Filter NPCs by zone shortname', 'type': 'string', 'example': 'qeynos'}
        },
        responses={
            200: ('Success', [npc_model]),
            400: ('Invalid parameters', error_model),
            404: ('NPC not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get NPCs
        
        Get NPCs using the following parameters:
        * id: Search NPCs by NPC ID (optional)
        * name: Search NPCs by partial name (optional, 50 results maximum)
        * zone: Filter NPCs by zone shortname (optional)
        
        Returns a list of NPCs matching the criteria.
        """
        try:
            npc_id = request.args.get('id', type=int)
            name = request.args.get('name')
            zone = request.args.get('zone')
        
            # Get NPCs from database
            npcs = npc_db.get_npc_raw_data(npc_id=npc_id, name=name, zone=zone)
            
            if not npcs:
                v1.abort(404, "No NPCs found")
            
            # Format response
            if isinstance(npcs, list):
                formatted_npcs = []
                for npc in npcs:
                    formatted_npc = format_npc_response(npc)
                    formatted_npcs.append(formatted_npc)
                return formatted_npcs
            else:
                # Single NPC
                return format_npc_response(npcs)
            
        except Exception as e:
            v1.abort(500, f"Error retrieving NPCs: {str(e)}")

@v1.route('/zones/waypoints')
class WaypointResource(Resource):
    @optional_auth
    @v1.doc('get_zones_with_waypoints',
        responses={
            200: ('Success', [zone_model]),
            404: ('No zones with waypoints found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get zones with waypoints
        
        Returns a list of zones that have waypoints.
        """
        try:
            zones = zone_db.waypoint_listing()
            
            if not zones:
                v1.abort(404, "No zones with waypoints found")
            
            return zones
            
        except Exception as e:
            v1.abort(500, f"Error retrieving zones with waypoints: {str(e)}")

@v1.route('/zones/<string:identifier>')
class ZoneDetailResource(Resource):
    @optional_auth
    @v1.doc('get_zone_by_identifier',
        params={'identifier': {'description': 'Zone ID or short name', 'in': 'path'}},
        responses={
            200: ('Success', zone_model),
            404: ('Zone not found', error_model)
        }
    )
    def get(self, identifier):
        """Get a single zone by its ID or short name"""
        zone = zone_db.get_zone_by_identifier(identifier)
        if not zone:
            v1.abort(404, "Zone not found")
        return format_zone_response(zone)

zone_details_model = v1.model('ZoneDetails', {
    'zoneidnumber': fields.Integer(description='Zone ID Number'),
    'expansion': fields.String(description='Expansion Name'),
    'short_name': fields.String(description='Zone Short Name'),
    'canbind': fields.Integer(description='Can Bind'),
    'canlevitate': fields.Integer(description='Can Levitate'),
    'castoutdoor': fields.Integer(description='Can Cast Outdoor Spells'),
    'zone_exp_multiplier': fields.Float(description='Zone Experience Multiplier'),
    'safe_x': fields.Float(description='Safe X Coordinate'),
    'safe_y': fields.Float(description='Safe Y Coordinate'),
    'safe_z': fields.Float(description='Safe Z Coordinate'),
    'zone_level_range': fields.String(description='Zone Level Range'),
    'waypoint_x': fields.Float(description='Waypoint X Coordinate'),
    'waypoint_y': fields.Float(description='Waypoint Y Coordinate'),
    'waypoint_z': fields.Float(description='Waypoint Z Coordinate'),
    'newbie_zone': fields.Boolean(description='Is Newbie Zone')
})

@v1.route('/zones/<string:short_name>/details')
class ZoneExtraDetailsResource(Resource):
    @optional_auth
    @v1.doc('get_zone_details_by_short_name',
        params={'short_name': {'description': 'Zone short name', 'in': 'path'}},
        responses={
            200: ('Success', zone_details_model),
            404: ('Zone not found', error_model)
        }
    )
    def get(self, short_name):
        """Get extended details for a single zone by its short name"""
        zone_details = zone_db.get_zone_details_by_short_name(short_name)
        if not zone_details:
            v1.abort(404, "Zone details not found")
        return zone_details

@v1.route('/zones/<string:short_name>/connected')
class ConnectedZoneResource(Resource):
    @optional_auth
    @v1.doc('get_connected_zones',
        params={'short_name': {'description': 'Zone short name', 'in': 'path'}},
        responses={
            200: ('Success', [connected_zone_model]),
            404: ('Zone not found', error_model)
        }
    )
    def get(self, short_name):
        """Get all connected zones for a given zone short name"""
        connected_zones = zone_db.get_connected_zones(short_name)
        if not connected_zones:
            v1.abort(404, "No connected zones found for this zone")
        return connected_zones

@v1.route('/zones/<string:short_name>/npcs')
class ZoneNPCsResource(Resource):
    @optional_auth
    @v1.doc('get_zone_npcs',
        params={'short_name': {'description': 'Zone short name', 'in': 'path'}},
        responses={
            200: ('Success', [npc_model]),
            404: ('Zone not found or no NPCs found', error_model)
        }
    )
    def get(self, short_name):
        """Get all NPCs for a given zone short name"""
        try:
            npcs = npc_db.get_npcs_by_zone(short_name)
            if not npcs:
                v1.abort(404, "No NPCs found for this zone")
            
            # Format response
            formatted_npcs = []
            for npc in npcs:
                formatted_npc = format_npc_response(npc)
                formatted_npcs.append(formatted_npc)
            return formatted_npcs
        except Exception as e:
            v1.abort(500, f"Error retrieving NPCs for zone {short_name}: {str(e)}")

@v1.route('/zones/<string:short_name>/items')
class ZoneItemsResource(Resource):
    @optional_auth
    @v1.doc('get_zone_items',
        params={'short_name': {'description': 'Zone short name', 'in': 'path'}},
        responses={
            200: ('Success', [item_model]),
            404: ('Zone not found or no items found', error_model)
        }
    )
    def get(self, short_name):
        """Get all items that drop in a given zone"""
        items = item_db.get_items_by_zone(short_name)
        if not items:
            v1.abort(404, "No items found for this zone")
        
        # Format response
        formatted_items = []
        for item in items:
            formatted_item = format_item_response(item)
            formatted_items.append(formatted_item)
        return formatted_items

npc_spawn_model = v1.model('NPCSpawn', {
    'npc_name': fields.String(description='NPC Name'),
    'npc_id': fields.Integer(description='NPC ID'),
    'npc_level': fields.Integer(description='NPC Level'),
    'npc_race': fields.String(description='NPC Race'),
    'npc_hp': fields.Integer(description='NPC HP'),
    'chance': fields.Integer(description='Spawn Chance'),
    'spawn2_id': fields.Integer(description='Spawn2 ID')
})

zone_spawn_model = v1.model('ZoneSpawn', {
    'x': fields.Float(description='X Coordinate'),
    'y': fields.Float(description='Y Coordinate'),
    'z': fields.Float(description='Z Coordinate'),
    'respawn': fields.Integer(description='Respawn Time'),
    'spawngroup_name': fields.String(description='Spawngroup Name'),
    'npcs': fields.List(fields.Nested(npc_spawn_model), description='List of NPCs in this spawn group')
})

@v1.route('/zones/<string:short_name>/spawns')
class ZoneSpawnsResource(Resource):
    @optional_auth
    @v1.doc('get_zone_spawns',
        params={'short_name': {'description': 'Zone short name', 'in': 'path'}},
        responses={
            200: ('Success', [zone_spawn_model]),
            404: ('Zone not found or no spawns found', error_model)
        }
    )
    def get(self, short_name):
        """Get all spawns for a given zone short name"""
        try:
            spawns = zone_db.get_zone_spawns_by_short_name(short_name)
            if not spawns:
                v1.abort(404, "No spawns found for this zone")
            return spawns
        except Exception as e:
            v1.abort(500, f"Error retrieving spawns for zone {short_name}: {str(e)}")

@v1.route('/zones')
class ZoneResource(Resource):
    @optional_auth
    @v1.doc('get_zones',
        params={
            'name': {'description': 'Search zones by partial name (50 results maximum)', 'type': 'string', 'example': 'qeynos'}
        },
        responses={
            200: ('Success', [zone_model]),
            400: ('Invalid parameters', error_model),
            404: ('Zone not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get zones
        
        Get zones using the following parameters:
        * name: Search zones by partial name (optional, 50 results maximum)
        
        If no name is provided, returns all zones grouped by expansion.
        Returns a list of zones matching the criteria.
        """
        try:
            name = request.args.get('name')
        
            if name:
                # Get zones from database
                zones = zone_db.get_zone_raw_data(name=name)
                
                if not zones:
                    v1.abort(404, "No zones found")
                
                # Format response
                if isinstance(zones, list):
                    formatted_zones = []
                    for zone in zones:
                        formatted_zone = format_zone_response(zone)
                        formatted_zones.append(formatted_zone)
                    return formatted_zones
                else:
                    # Single zone
                    return format_zone_response(zones)
            else:
                # Return all zones by expansion
                zones = zone_db.get_all_zones_by_expansion()
                if not zones:
                    v1.abort(404, "No zones found")
                return zones
            
        except Exception as e:
            v1.abort(500, f"Error retrieving zones: {str(e)}")

@v1.route('/tradeskills')
class TradeskillResource(Resource):
    @optional_auth
    @v1.doc('get_tradeskills',
        params={
            'id': {'description': 'Search tradeskills by ID', 'type': 'integer', 'example': 59},
            'name': {'description': 'Search tradeskills by partial name (50 results maximum)', 'type': 'string', 'example': 'alchemy'}
        },
        responses={
            200: ('Success', [tradeskill_model]),
            400: ('Invalid parameters', error_model),
            404: ('Tradeskill not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get tradeskills
        
        Get tradeskills using the following parameters:
        * id: Search tradeskills by ID (optional)
        * name: Search tradeskills by partial name (optional, 50 results maximum)
        
        Returns a list of tradeskills matching the criteria.
        """
        try:
            tradeskill_id = request.args.get('id', type=int)
            name = request.args.get('name')
        
            # Get tradeskills from database
            tradeskills = tradeskill_db.get_tradeskill_raw_data(tradeskill_id=tradeskill_id, name=name)
            
            if not tradeskills:
                v1.abort(404, "No tradeskills found")
            
            # Format response
            if isinstance(tradeskills, list):
                return tradeskills[:50]  # Enforce 50 result limit
            else:
                return [tradeskills]
            
        except Exception as e:
            v1.abort(500, f"Error retrieving tradeskills: {str(e)}")

@v1.route('/recipes')
class RecipeResource(Resource):
    @v1.doc('get_recipes',
        params={
            'id': {'description': 'Search recipes by recipe ID', 'type': 'integer', 'example': 12345},
            'name': {'description': 'Search recipes by partial name (50 results maximum)', 'type': 'string', 'example': 'dagger'},
            'tradeskill': {'description': 'Filter recipes by tradeskill type', 'type': 'string', 'enum': ['Alchemy', 'Baking', 'Tailoring', 'Blacksmithing', 'Fletching', 'Brewing', 'Jewel Crafting', 'Pottery', 'Research', 'Poison Making', 'Tinkering'], 'example': 'Blacksmithing'}
        },
        responses={
            200: ('Success', [recipe_model]),
            400: ('Invalid parameters', error_model),
            404: ('Recipe not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Search for recipes by ID, name, or tradeskill type
        
        Search for recipes using various parameters:
        * id: Exact recipe ID match
        * name: Partial name match (case-insensitive)
        * tradeskill: Filter by tradeskill type (dropdown selection)
        
        Returns a list of recipes matching the criteria, limited to 50 results.
        """
        recipe_id = request.args.get('id')
        name = request.args.get('name')
        tradeskill_type = request.args.get('tradeskill')
        
        if recipe_id:
            data = tradeskill_db.get_recipe_raw_data(recipe_id=recipe_id)
            if not data:
                v1.abort(404, "Recipe not found")
            return data
        elif name:
            data = tradeskill_db.get_recipe_raw_data(name=name)
            if not data:
                v1.abort(404, "Recipe not found")
            return data[:50]  # Enforce 50 result limit
        elif tradeskill_type:
            data = tradeskill_db.get_recipe_raw_data(tradeskill=tradeskill_type)
            if not data:
                v1.abort(404, "No recipes found for this tradeskill")
            return data[:50]  # Enforce 50 result limit
        else:
            v1.abort(400, "No parameters provided")

@v1.route('/quests')
class QuestResource(Resource):
    @v1.doc('get_quests',
        params={
            'name': {'description': 'Search quests by partial name (50 results maximum)', 'type': 'string', 'example': 'guard'},
            'npc_name': {'description': 'Search quests by NPC name (50 results maximum)', 'type': 'string', 'example': 'captain'},
            'item_id': {'description': 'Search quests by quest item ID', 'type': 'integer', 'example': 12345},
            'item_name': {'description': 'Search quests by quest item name (50 results maximum)', 'type': 'string', 'example': 'dagger'},
            'min_level': {'description': 'Minimum NPC level filter', 'type': 'integer', 'example': 1},
            'max_level': {'description': 'Maximum NPC level filter', 'type': 'integer', 'example': 50},
            'zone': {'description': 'Filter by zone short name', 'type': 'string', 'example': 'qeynos'},
            'expansion': {'description': 'Filter by expansion number', 'type': 'integer', 'example': 0}
        },
        responses={
            200: ('Success', [quest_model]),
            400: ('Invalid parameters', error_model),
            404: ('Quest not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Search for quests by name, NPC name, or item name/ID with filtering
        
        Search for quests using various parameters:
        * name: Partial quest name match (case-insensitive)
        * npc_name: Search by NPC name (case-insensitive)
        * item_id: Search by quest item ID
        * item_name: Search by quest item name (case-insensitive)
        * min_level: Minimum NPC level filter
        * max_level: Maximum NPC level filter
        * zone: Filter by zone short name
        * expansion: Filter by expansion number
        
        Returns a list of quests matching the criteria, limited to 50 results.
        """
        name = request.args.get('name')
        npc_name = request.args.get('npc_name')
        item_id = request.args.get('item_id')
        item_name = request.args.get('item_name')
        min_level = request.args.get('min_level', type=int)
        max_level = request.args.get('max_level', type=int)
        zone = request.args.get('zone')
        expansion = request.args.get('expansion', type=int)
        
        if name:
            data = quest_db.get_quest_raw_data(name=name, min_level=min_level, max_level=max_level, 
                                          zone=zone, expansion=expansion)
            if not data:
                v1.abort(404, "Quest not found")
            return data[:50]  # Enforce 50 result limit
        elif npc_name:
            data = quest_db.get_quest_raw_data(npc_name=npc_name, min_level=min_level, max_level=max_level,
                                          zone=zone, expansion=expansion)
            if not data:
                v1.abort(404, "No quests found for this NPC")
            return data[:50]  # Enforce 50 result limit
        elif item_id:
            data = quest_db.get_quest_raw_data(item_id=item_id)
            if not data:
                v1.abort(404, "No quests found for this item")
            return data[:50]  # Enforce 50 result limit
        elif item_name:
            data = quest_db.get_quest_raw_data(item_name=item_name)
            if not data:
                v1.abort(404, "No quests found for this item")
            return data[:50]  # Enforce 50 result limit
        else:
            v1.abort(400, "No parameters provided")

@v1.route('/quests/chains')
class QuestChainResource(Resource):
    @v1.doc('get_quest_chains',
        params={
            'npc_id': {'description': 'Get quest chain from specific NPC', 'type': 'integer', 'example': 12345},
            'faction_id': {'description': 'Get quest chain from specific faction', 'type': 'integer', 'example': 100}
        },
        responses={
            200: ('Success', [quest_model]),
            400: ('Invalid parameters', error_model),
            404: ('Quest chain not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get quest chains by NPC ID or faction ID
        
        Get quest chains using various parameters:
        * npc_id: Get all quests from a specific NPC
        * faction_id: Get all quests from a specific faction
        
        Returns a list of quests in the chain, limited to 50 results.
        """
        npc_id = request.args.get('npc_id')
        faction_id = request.args.get('faction_id')
        
        if npc_id:
            data = quest_db.get_quest_chains(npc_id=npc_id)
            if not data:
                v1.abort(404, "No quest chain found for this NPC")
            return data[:50]  # Enforce 50 result limit
        elif faction_id:
            data = quest_db.get_quest_chains(faction_id=faction_id)
            if not data:
                v1.abort(404, "No quest chain found for this faction")
            return data[:50]  # Enforce 50 result limit
        else:
            v1.abort(400, "No parameters provided")

@v1.route('/quests/items')
class QuestItemResource(Resource):
    @v1.doc('get_quest_items',
        params={
            'expansion': {'description': 'Get quest items by expansion', 'type': 'string', 'enum': ['classic', 'kunark', 'velious', 'luclin', 'planes', 'god', 'oow', 'don', 'ldon', 'loy'], 'example': 'classic'}
        },
        responses={
            200: ('Success', [quest_model]),
            400: ('Invalid parameters', error_model),
            404: ('Quest items not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get quest items by expansion
        
        Get quest items using the expansion parameter:
        * expansion: Filter by expansion (classic, kunark, velious, luclin, planes, god, oow, don, ldon, loy)
        
        Returns a list of quest items from the specified expansion, limited to 50 results.
        """
        expansion = request.args.get('expansion')
        
        if expansion:
            data = quest_db.get_quest_items_by_expansion(expansion=expansion)
            if not data:
                v1.abort(404, "No quest items found for this expansion")
            return data[:50]  # Enforce 50 result limit
        else:
            v1.abort(400, "No parameters provided")

@v1.route('/quests/zones')
class QuestZoneResource(Resource):
    @v1.doc('get_quest_zones',
        responses={
            200: ('Success', zones_by_expansion_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get zones grouped by expansion for two-tiered selector
        
        Returns a hierarchical structure of expansions and their zones for filtering.
        """
        try:
            zones_by_expansion = expansion_db.get_zones_by_expansion()
            return zones_by_expansion
        except Exception as e:
            v1.abort(500, f"Error retrieving zones: {str(e)}")

@v1.route('/quests/expansions')
class QuestExpansionResource(Resource):
    @v1.doc('get_quest_expansions',
        responses={
            200: ('Success', expansions_list_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get list of available expansions
        
        Returns a list of all available expansions for filtering.
        """
        try:
            expansions = expansion_db.get_all_expansions()
            return {'expansions': expansions}
        except Exception as e:
            v1.abort(500, f"Error retrieving expansions: {str(e)}")

@v1.route('/quests/zones/<int:expansion>')
class QuestZoneByExpansionResource(Resource):
    @v1.doc('get_quest_zones_by_expansion',
        params={
            'expansion': {'description': 'Expansion number', 'type': 'integer', 'in': 'path', 'example': 0}
        },
        responses={
            200: ('Success', zones_in_expansion_model),
            404: ('Expansion not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self, expansion):
        """Get zones for a specific expansion
        
        Get zones using the expansion parameter:
        * expansion: Expansion number (path parameter)
        
        Returns a list of zones in the specified expansion.
        """
        try:
            zones = expansion_db.get_zones_in_expansion(expansion)
            if not zones:
                v1.abort(404, "No zones found for this expansion")
            return {'zones': zones}
        except Exception as e:
            v1.abort(500, f"Error retrieving zones: {str(e)}")

@v1.route('/expansions')
class ExpansionsResource(Resource):
    @v1.doc('get_expansions',
        responses={
            200: ('Success', expansions_list_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get all expansions
        
        Returns a list of all available expansions with their details.
        """
        try:
            expansions = expansion_db.get_all_expansions()
            return {'expansions': expansions}
        except Exception as e:
            v1.abort(500, f"Error retrieving expansions: {str(e)}")

@v1.route('/expansions/<int:expansion_id>')
class ExpansionResource(Resource):
    @v1.doc('get_expansion',
        params={
            'expansion_id': {'description': 'Expansion ID', 'type': 'integer', 'in': 'path', 'example': 0}
        },
        responses={
            200: ('Success', expansion_model),
            404: ('Expansion not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self, expansion_id):
        """Get expansion details by ID
        
        Get expansion details using the expansion_id parameter:
        * expansion_id: Expansion ID (path parameter)
        
        Returns detailed information about the specified expansion.
        """
        try:
            expansion_data = expansion_db.get_expansion_by_id(expansion_id)
            if not expansion_data:
                v1.abort(404, "Expansion not found")
            return expansion_data
        except Exception as e:
            v1.abort(500, f"Error retrieving expansion: {str(e)}")

@v1.route('/expansions/search')
class ExpansionSearchResource(Resource):
    @v1.doc('search_expansions',
        params={
            'name': {'description': 'Search expansions by name (case-insensitive)', 'type': 'string', 'example': 'classic'}
        },
        responses={
            200: ('Success', expansion_model),
            404: ('Expansion not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Search for expansion by name
        
        Search for expansion using the name parameter:
        * name: Expansion name or short name (case-insensitive)
        
        Returns detailed information about the matching expansion.
        """
        name = request.args.get('name')
        
        if not name:
            v1.abort(400, "Name parameter is required")
        
        try:
            expansion_data = expansion_db.get_expansion_by_name(name)
            if not expansion_data:
                v1.abort(404, "Expansion not found")
            return expansion_data
        except Exception as e:
            v1.abort(500, f"Error searching expansion: {str(e)}")

@v1.route('/expansions/<int:expansion_id>/zones')
class ExpansionZonesResource(Resource):
    @v1.doc('get_expansion_zones',
        params={
            'expansion_id': {'description': 'Expansion ID', 'type': 'integer', 'in': 'path', 'example': 0},
            'min_level': {'description': 'Minimum zone level', 'type': 'integer', 'in': 'query', 'example': 1},
            'max_level': {'description': 'Maximum zone level', 'type': 'integer', 'in': 'query', 'example': 65}
        },
        responses={
            200: ('Success', zones_in_expansion_model),
            404: ('Expansion not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self, expansion_id):
        """Get zones for a specific expansion
        
        Get zones using the following parameters:
        * expansion_id: Expansion ID (path parameter)
        * min_level: Minimum zone level (optional)
        * max_level: Maximum zone level (optional)
        
        Returns a list of zones in the specified expansion.
        """
        try:
            min_level = request.args.get('min_level', type=int)
            max_level = request.args.get('max_level', type=int)

            # First check if expansion exists
            expansion_data = expansion_db.get_expansion_by_id(expansion_id)
            if not expansion_data:
                v1.abort(404, "Expansion not found")
            
            zones = expansion_db.get_zones_in_expansion(expansion_id, min_level=min_level, max_level=max_level)
            return {'zones': zones}
        except Exception as e:
            v1.abort(500, f"Error retrieving zones: {str(e)}")

@v1.route('/expansions/<int:expansion_id>/items')
class ExpansionItemsByExpansionResource(Resource):
    @optional_auth
    @v1.doc('get_expansion_items_by_expansion',
        params={
            'expansion_id': {'description': 'Expansion ID', 'type': 'integer', 'in': 'path', 'example': 0}
        },
        responses={
            200: ('Success', [item_model]),
            404: ('Expansion not found or no items found', error_model)
        },
        security='apikey'
    )
    def get(self, expansion_id):
        """Get all items that drop in a given expansion"""
        try:
            items = item_db.get_items_by_expansion(expansion_id)
            if not items:
                v1.abort(404, "No items found for this expansion")
            
            # Format response
            formatted_items = []
            for item in items:
                formatted_item = format_item_response(item)
                formatted_items.append(formatted_item)
            return formatted_items
        except Exception as e:
            v1.abort(500, f"Error retrieving items for expansion {expansion_id}: {str(e)}")

@v1.route('/expansion-items')
class ExpansionItemsResource(Resource):
    @v1.doc('get_expansion_items',
        params={
            'expansion_id': {'description': 'Filter by expansion ID', 'type': 'integer', 'example': 0},
            'item_type': {'description': 'Filter by item type', 'type': 'string', 'enum': ['regular', 'tradeskill', 'special', 'custom'], 'example': 'regular'},
            'is_custom': {'description': 'Filter by custom status', 'type': 'boolean', 'example': False},
            'item_id': {'description': 'Filter by specific item ID', 'type': 'integer', 'example': 12345}
        },
        responses={
            200: ('Success', expansion_items_list_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get expansion items with filtering
        
        Get expansion items using various filter parameters:
        * expansion_id: Filter by expansion ID
        * item_type: Filter by item type (regular, tradeskill, special, custom)
        * is_custom: Filter by custom status
        * item_id: Filter by specific item ID
        
        Returns a list of expansion items matching the criteria.
        """
        try:
            expansion_id = request.args.get('expansion_id', type=int)
            item_type = request.args.get('item_type')
            is_custom = request.args.get('is_custom', type=bool)
            item_id = request.args.get('item_id', type=int)
            
            items = expansion_items_db.search_items(
                item_id=item_id,
                expansion_id=expansion_id,
                item_type=item_type,
                is_custom=is_custom
            )
            
            # The data is already in the correct format from the search_items method
            return {'items': items}
        except Exception as e:
            v1.abort(500, f"Error retrieving expansion items: {str(e)}")

@v1.route('/expansion-items/summary')
class ExpansionItemsSummaryResource(Resource):
    @v1.doc('get_expansion_items_summary',
        responses={
            200: ('Success', expansion_summary_list_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get summary of items by expansion and type
        
        Returns a summary of item counts by expansion and type.
        """
        try:
            summary = expansion_items_db.get_expansion_summary()
            
            # Convert to list format for API response
            summaries = []
            for expansion_id, counts in summary.items():
                if counts['total'] > 0:  # Only include expansions with items
                    summaries.append({
                        'expansion_id': expansion_id,
                        'regular': counts['regular'],
                        'tradeskill': counts['tradeskill'],
                        'special': counts['special'],
                        'custom': counts['custom'],
                        'total': counts['total']
                    })
            
            return {'summaries': summaries}
        except Exception as e:
            v1.abort(500, f"Error retrieving expansion items summary: {str(e)}")

@v1.route('/expansion-items/custom')
class CustomItemsResource(Resource):
    @optional_auth
    @v1.doc('get_custom_items',
        params={
            'expansion_id': {'description': 'Filter by expansion ID', 'type': 'integer', 'example': 0}
        },
        responses={
            200: ('Success', expansion_items_list_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get custom items
        
        Get custom items using the expansion_id parameter:
        * expansion_id: Filter by expansion ID (optional)
        
        Returns a list of custom items.
        """
        try:
            expansion_id = request.args.get('expansion_id', type=int)
            
            items = expansion_items_db.get_custom_items(expansion_id=expansion_id)
            
            # Convert SQLAlchemy objects to dictionaries
            items_data = []
            for item in items:
                items_data.append({
                    'id': item.id,
                    'item_id': item.item_id,
                    'expansion_id': item.expansion_id,
                    'item_type': item.item_type,
                    'is_custom': item.is_custom,
                    'added_date': item.added_date.isoformat() if item.added_date else None,
                    'notes': item.notes
                })
            
            return {'items': items_data}
        except Exception as e:
            v1.abort(500, f"Error retrieving custom items: {str(e)}")
    
    @write_auth_required
    @v1.doc('add_custom_item',
        params={
            'item_id': {'description': 'Item ID', 'type': 'integer', 'required': True, 'example': 12345},
            'expansion_id': {'description': 'Expansion ID', 'type': 'integer', 'required': True, 'example': 0},
            'item_type': {'description': 'Item type', 'type': 'string', 'enum': ['regular', 'tradeskill', 'special', 'custom'], 'example': 'custom'},
            'notes': {'description': 'Additional notes', 'type': 'string', 'example': 'Custom server item'}
        },
        responses={
            201: ('Success', expansion_item_model),
            400: ('Invalid parameters', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def post(self):
        """Add a custom item
        
        Add a custom item using the following parameters:
        * item_id: Item ID (required)
        * expansion_id: Expansion ID (required)
        * item_type: Item type (optional, defaults to 'custom')
        * notes: Additional notes (optional)
        
        Returns the created custom item.
        """
        try:
            data = request.get_json()
            
            if not data:
                v1.abort(400, "No data provided")
            
            item_id = data.get('item_id')
            expansion_id = data.get('expansion_id')
            item_type = data.get('item_type', 'custom')
            notes = data.get('notes')
            
            if item_id is None or expansion_id is None:
                v1.abort(400, "item_id and expansion_id are required")
            
            # Check if expansion exists
            expansion_data = expansion_db.get_expansion_by_id(expansion_id)
            if not expansion_data:
                v1.abort(400, "Invalid expansion_id")
            
            # Add the custom item
            custom_item = expansion_items_db.add_custom_item(
                item_id=item_id,
                expansion_id=expansion_id,
                item_type=item_type,
                notes=notes
            )
            
            return {
                'id': custom_item.id,
                'item_id': custom_item.item_id,
                'expansion_id': custom_item.expansion_id,
                'item_type': custom_item.item_type,
                'is_custom': custom_item.is_custom,
                'added_date': custom_item.added_date.isoformat() if custom_item.added_date else None,
                'notes': custom_item.notes
            }, 201
        except Exception as e:
            v1.abort(500, f"Error adding custom item: {str(e)}")

@v1.route('/expansion-items/custom/<int:item_id>/<int:expansion_id>')
class CustomItemResource(Resource):
    @write_auth_required
    @v1.doc('remove_custom_item',
        params={
            'item_id': {'description': 'Item ID', 'type': 'integer', 'in': 'path', 'example': 12345},
            'expansion_id': {'description': 'Expansion ID', 'type': 'integer', 'in': 'path', 'example': 0}
        },
        responses={
            200: ('Success', success_message_model),
            404: ('Custom item not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def delete(self, item_id, expansion_id):
        """Remove a custom item
        
        Remove a custom item using the following parameters:
        * item_id: Item ID (path parameter)
        * expansion_id: Expansion ID (path parameter)
        
        Returns success message.
        """
        try:
            success = expansion_items_db.remove_custom_item(item_id, expansion_id)
            
            if success:
                return {'message': 'Custom item removed successfully'}
            else:
                v1.abort(404, "Custom item not found")
        except Exception as e:
            v1.abort(500, f"Error removing custom item: {str(e)}")

@v1.route('/cache/clear')
class CacheClearResource(Resource):
    @write_auth_required
    @v1.doc('clear_cache',
        responses={
            200: ('Success', success_message_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def post(self):
        """Clear the Redis cache"""
        try:
            if clear_cache():
                return {'message': 'Cache cleared successfully'}
            else:
                v1.abort(500, "Could not connect to Redis")
        except Exception as e:
            v1.abort(500, f"Error clearing cache: {str(e)}")

@v1.route('/expansion-items/import')
class ImportItemsResource(Resource):
    @write_auth_required
    @v1.doc('import_item_files',
        responses={
            200: ('Success', import_result_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def post(self):
        """Import item files from the item_files directory
        
        Imports all item files from the item_files directory into the database.
        This should be run when new item files are added or updated.
        
        Returns import summary.
        """
        try:
            import os
            item_files_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'item_files')
            
            if not os.path.exists(item_files_dir):
                v1.abort(500, "Item files directory not found")
            
            total_imported = expansion_items_db.import_item_files(item_files_dir)
            
            return {
                'message': 'Import completed successfully',
                'total_imported': total_imported
            }
        except Exception as e:
            v1.abort(500, f"Error importing item files: {str(e)}")

@v1.route('/items/search')
class ItemSearchResource(Resource):
    @optional_auth
    @v1.doc('search_items_rich',
        params={
            'name': {'description': 'Partial item name', 'type': 'string', 'example': 'Short Sword'},
            'slot': {'description': 'Equipment slot', 'type': 'string', 'enum': list(Util.get_categorized_item_slots().values()), 'example': 'Primary'},
            'class': {'description': 'Playable class', 'type': 'string', 'enum': [get_class_string(i) for i in range(1, 17)], 'example': 'Warrior'},
            'item_type': {'description': 'Item type', 'type': 'string', 'enum': list(Util.get_categorized_item_types().values()), 'example': '1H Slashing'},
            'skillmodtype': {'description': 'Skill mod type', 'type': 'string', 'enum': [entry for skill in get_all_skills() for entry in skill.values()], 'example': 'Abjuration'},
            'expansion': {'description': 'Expansion name', 'type': 'string', 'enum': [], 'example': 'Classic'},
            'stat_filters': {'description': 'Array of stat filter objects: {stat: string, value: int}', 'type': 'array', 'items': {'type': 'object', 'properties': {'stat': {'type': 'string'}, 'value': {'type': 'integer'}}}, 'example': [{'stat': 'hp', 'value': 50}]},
            'stat_weights': {'description': 'Array of stat weight objects: {stat: string, weight: float}', 'type': 'array', 'items': {'type': 'object', 'properties': {'stat': {'type': 'string'}, 'weight': {'type': 'number'}}}, 'example': [{'stat': 'damage', 'weight': 1.5}]},
            'exclude_expansions': {'description': 'Array of expansion names to exclude', 'type': 'array', 'items': {'type': 'string'}, 'example': ['Kunark', 'Velious']},
            'elemental_damage_type': {'description': 'Weapon elemental damage type', 'type': 'string', 'enum': ['Magic', 'Fire', 'Cold', 'Poison', 'Disease', 'Chromatic', 'Prismatic', 'Phys', 'Corruption'], 'example': 'Fire'},
            'bane_damage_type': {'description': 'Weapon bane damage type', 'type': 'string', 'enum': ['body_14', 'race_217', 'race_236'], 'example': 'body_14'},
            'proc': {'description': 'Weapons with proc: None (include), True (only)', 'type': 'string', 'enum': ['None', 'True'], 'example': 'None'},
            'click': {'description': 'Items with click effect: None (include), True (only)', 'type': 'string', 'enum': ['None', 'True'], 'example': 'None'},
            'proc_level': {'description': 'Required level to proc', 'type': 'integer', 'example': 0},
            'click_level': {'description': 'Required level to click', 'type': 'integer', 'example': 0},
            'pet_search': {'description': 'Search for pet items', 'type': 'boolean', 'example': False},
            'show_full_detail': {'description': 'Show item detail table', 'type': 'boolean', 'example': False},
            'show_weight_detail': {'description': 'Show only weight details (requires one weight)', 'type': 'boolean', 'example': False},
            'ignore_zero': {'description': 'Include zero weight items (requires one weight)', 'type': 'boolean', 'example': False},
            'sympathetic': {'description': 'Sympathetic effect filter', 'type': 'string', 'enum': ['None', 'all_strike', '24356', '24357', '24358', '24359', '24360', '24361', '24362', '24363', '24364', '24365', 'all_heal', '24434', '24435', '24436', '24437', '24438', '24439', '24440', '24441', '24442', '24443'], 'example': 'None'},
            'page': {'description': 'Page number for pagination (starts at 1)', 'type': 'integer', 'example': 1},
            'page_size': {'description': 'Number of items per page (default 20, max 200)', 'type': 'integer', 'example': 20}
        },
        responses={
            200: ('Success', fields.Raw(description='Paginated item search results with total, page, page_size, and pages. Each item includes all stats, effects, icons, and nested spell/effect info needed for the results table.')),
            400: ('Invalid parameters', error_model),
            404: ('Item not found', error_model)
        },
        security='apikey'
    )
    def get(self):
        import time
        req_start = time.time()
        # Parse query params
        name = request.args.get('name')
        slot = request.args.get('slot')
        class_name = request.args.get('class')
        item_type = request.args.get('item_type')
        skillmodtype = request.args.get('skillmodtype')
        expansion = request.args.get('expansion')
        elemental_damage_type = request.args.get('elemental_damage_type')
        bane_damage_type = request.args.get('bane_damage_type')
        proc = request.args.get('proc')
        click = request.args.get('click')
        pet_search = request.args.get('pet_search', type=lambda v: v.lower() == 'true' if v else False)
        sympathetic = request.args.get('sympathetic')
        stat_filters = request.args.get('stat_filters')
        stat_weights = request.args.get('stat_weights')
        exclude_expansions = request.args.get('exclude_expansions')
        proc_level = request.args.get('proc_level', type=int)
        click_level = request.args.get('click_level', type=int)
        show_full_detail = request.args.get('show_full_detail', type=lambda v: v.lower() == 'true' if v else False)
        show_weight_detail = request.args.get('show_weight_detail', type=lambda v: v.lower() == 'true' if v else False)
        ignore_zero = request.args.get('ignore_zero', type=lambda v: v.lower() == 'true' if v else False)
        page = request.args.get('page', default=1, type=int)
        page_size = request.args.get('page_size', default=20, type=int)

        # Parse JSON arrays if present
        import json as _json
        if stat_filters:
            try:
                stat_filters = _json.loads(stat_filters)
            except Exception:
                stat_filters = []
        else:
            stat_filters = []
        if stat_weights:
            try:
                stat_weights = _json.loads(stat_weights)
            except Exception:
                stat_weights = []
        else:
            stat_weights = []
        if exclude_expansions:
            try:
                exclude_expansions = _json.loads(exclude_expansions)
            except Exception:
                exclude_expansions = []
        else:
            exclude_expansions = []

        # Build Redis search params
        redis_params = {}
        if name:
            redis_params['name'] = name
        if slot:
            redis_params['slot'] = slot
        if class_name:
            redis_params['class'] = class_name
        if item_type:
            redis_params['type'] = item_type
        if expansion:
            redis_params['expansion'] = expansion
        if elemental_damage_type:
            redis_params['elemental_damage_type'] = elemental_damage_type
        if bane_damage_type:
            redis_params['bane_damage_type'] = bane_damage_type
        if proc and proc == 'True':
            redis_params['proc'] = 'True'
        if click and click == 'True':
            redis_params['click'] = 'True'
        if pet_search:
            redis_params['pet_search'] = True
        if sympathetic and sympathetic != 'None':
            redis_params['sympathetic'] = sympathetic

        logger.info(f"[SEARCH] Redis params: {redis_params}")
        t0 = time.time()
        items = search_items_from_redis(redis_params)
        t1 = time.time()
        logger.info(f"[PROFILE] Redis search took {t1-t0:.4f} seconds for params: {redis_params}")
        logger.info(f"[SEARCH] Items from Redis: {len(items)}")

        # Post-process for stat_filters, stat_weights, exclude_expansions, proc_level, click_level
        filtered_items = []
        for item in items:
            # Exclude expansions
            if exclude_expansions and item.get('expansion_name') in exclude_expansions:
                continue
            # Stat filters
            stat_pass = True
            for stat_filter in stat_filters:
                stat = stat_filter.get('stat')
                value = stat_filter.get('value')
                if stat and value is not None:
                    try:
                        if int(item.get(stat, 0)) < int(value):
                            stat_pass = False
                            break
                    except Exception:
                        stat_pass = False
                        break
            if not stat_pass:
                continue
            # Proc/click level
            if proc_level and int(item.get('proc_level', 0)) < proc_level:
                continue
            if click_level and int(item.get('click_level', 0)) < click_level:
                continue
            filtered_items.append(item)

        # Stat weights (sort by weighted score if provided)
        if stat_weights:
            def weighted_score(item):
                score = 0.0
                for weight in stat_weights:
                    stat = weight.get('stat')
                    w = weight.get('weight', 1.0)
                    try:
                        score += float(item.get(stat, 0)) * float(w)
                    except Exception:
                        continue
                return score
            filtered_items.sort(key=weighted_score, reverse=True)

        total = len(filtered_items)
        # Pagination
        start = (page - 1) * page_size
        end = start + page_size
        paged_items = filtered_items[start:end]
        logger.info(f"[SEARCH] Post-processed and paginated items: {len(paged_items)} (total {total})")

        # Enrichment and result construction
        enriched = []
        enrich_start = time.time()
        required_fields = [
            'id', 'name', 'type', 'slot_names', 'expansion_name', 'is_quest_item', 'npcs',
            'serialized', 'itemtype_name'
        ]
        for item in paged_items:
            item_id = int(item['id']) if 'id' in item else None
            from api.cache import get_redis_client
            client = get_redis_client()
            zone_npc_key = f"itemZoneNpc:{item_id}" if item_id else None
            zone_npc_json = client.get(zone_npc_key) if client and zone_npc_key else None
            npcs = []
            if zone_npc_json:
                try:
                    npcs = json.loads(zone_npc_json)
                except Exception as e:
                    logger.warning(f"Failed to decode itemZoneNpc for item {item_id}: {e}")
                    npcs = []
            else:
                try:
                    npcs = item_db.get_item_npcs(item_id) if item_id else []
                    client.set(zone_npc_key, json.dumps(npcs))
                except Exception as e:
                    logger.warning(f"Failed to set itemZoneNpc for item {item_id}: {e}")
            # Build result dict with all required fields
            result = {
                'id': item_id,
                'name': item.get('name', item.get('Name', 'Unknown Item')),
                'type': item.get('type', item.get('itemtype_name', '')),
                'slot_names': item.get('slot_names', ''),
                'expansion_name': item.get('expansion_name', ''),
                'is_quest_item': item.get('is_quest_item', False),
                'npcs': npcs,
                'serialized': item.get('serialized', ''),
                'itemtype_name': item.get('itemtype_name', item.get('type', ''))
            }
            # Ensure all required fields are present
            for k in required_fields:
                if k not in result:
                    result[k] = ''
            # Add toggles for detail/weight/zero/sympathetic as needed
            if show_full_detail:
                result['full_detail'] = item
            if show_weight_detail and stat_weights:
                result['weight_score'] = weighted_score(item)
            if ignore_zero:
                result['full_detail'] = {k: v for k, v in item.items() if str(v) != '0'}
            if sympathetic and sympathetic != 'None':
                result['sympathetic'] = item.get('sympathetic', '')
            enriched.append(result)
        enrich_end = time.time()
        logger.info(f"[PROFILE] Enrichment took {enrich_end-enrich_start:.4f} seconds for {len(enriched)} items")
        req_end = time.time()
        logger.info(f"[PROFILE] Total /items/search request time: {req_end-req_start:.4f} seconds")
        return {
            'results': enriched,
            'total': total,
            'page': page,
            'page_size': page_size,
            'pages': (total + page_size - 1) // page_size
        }

def init_routes(api):
    """Initialize all routes"""
    logger.info("Initializing API routes")
    
    # Add resources to the v1 namespace
    v1.add_resource(ItemResource, '/items')
    v1.add_resource(ItemTypesResource, '/items/types')
    v1.add_resource(ItemSlotsResource, '/items/slots')
    v1.add_resource(SpellResource, '/spells')
    v1.add_resource(SpellClassesResource, '/spells/classes')
    v1.add_resource(SpellsByClassResource, '/spells/list/<string:class_names>')
    v1.add_resource(NPCResource, '/npcs')
    v1.add_resource(ZoneResource, '/zones')
    v1.add_resource(ZoneDetailResource, '/zones/<string:identifier>')
    v1.add_resource(ZoneExtraDetailsResource, '/zones/<string:short_name>/details')
    v1.add_resource(ConnectedZoneResource, '/zones/<string:short_name>/connected')
    v1.add_resource(ZoneNPCsResource, '/zones/<string:short_name>/npcs')
    v1.add_resource(ZoneItemsResource, '/zones/<string:short_name>/items')
    v1.add_resource(ZoneSpawnsResource, '/zones/<string:short_name>/spawns')
    v1.add_resource(WaypointResource, '/zones/waypoints')
    v1.add_resource(TradeskillResource, '/tradeskills')
    v1.add_resource(RecipeResource, '/recipes')
    v1.add_resource(QuestResource, '/quests')
    v1.add_resource(QuestChainResource, '/quests/chains')
    v1.add_resource(QuestItemResource, '/quests/items')
    v1.add_resource(QuestZoneResource, '/quests/zones')
    v1.add_resource(QuestExpansionResource, '/quests/expansions')
    v1.add_resource(QuestZoneByExpansionResource, '/quests/zones/<int:expansion>')
    v1.add_resource(ExpansionsResource, '/expansions')
    v1.add_resource(ExpansionResource, '/expansions/<int:expansion_id>')
    v1.add_resource(ExpansionSearchResource, '/expansions/search')
    v1.add_resource(ExpansionZonesResource, '/expansions/<int:expansion_id>/zones')
    v1.add_resource(ExpansionItemsByExpansionResource, '/expansions/<int:expansion_id>/items')
    v1.add_resource(ExpansionItemsResource, '/expansion-items')
    v1.add_resource(ExpansionItemsSummaryResource, '/expansion-items/summary')
    v1.add_resource(CustomItemsResource, '/expansion-items/custom')
    v1.add_resource(CustomItemResource, '/expansion-items/custom/<int:item_id>/<int:expansion_id>')
    v1.add_resource(ImportItemsResource, '/expansion-items/import')
    v1.add_resource(CacheClearResource, '/cache/clear')
    v1.add_resource(WeightSetsResource, '/user/weight-sets')
    v1.add_resource(WeightSetResource, '/user/weight-sets/<int:weight_set_id>')


    # Add authentication namespace
    api.add_namespace(auth_ns, path='/auth')
    
    # Create default admin user
    auth.create_default_admin()
    
    logger.info("API routes initialization complete")

# Weight Set API Endpoints
class WeightSetsResource(Resource):
    """Get all weight sets for the authenticated user"""
    
    @write_auth_required
    @v1.doc('get_weight_sets',
        responses={
            200: ('Success', weight_sets_list_model),
            401: ('Unauthorized', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get all weight sets for the authenticated user"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            # Import local functions for weight sets
            import local
            
            # Get weight sets with proper ID mapping
            user_id = user.id
            with local.Session(bind=local.local_engine) as session:
                # Get all weight sets for this user with their IDs
                weights_query = session.query(local.Weights).filter(local.Weights.uid == user_id)
                weights_result = weights_query.all()
                
                weight_sets = []
                for weight_entry in weights_result:
                    # Get the weight entries for this weight set
                    weight_entries_query = session.query(local.WeightEntry).filter(local.WeightEntry.wid == weight_entry.wid)
                    weight_entries = weight_entries_query.all()
                    
                    # Convert to API format
                    weights = []
                    for entry in weight_entries:
                        stat_name = local.utils.get_stat_name(entry.stat)
                        weights.append({
                            'stat': entry.stat,
                            'value': float(entry.value)
                        })
                    
                    weight_sets.append({
                        'id': weight_entry.wid,  # Use actual database ID
                        'name': weight_entry.name,
                        'description': f'Weight set: {weight_entry.name}',
                        'weights': weights,
                        'created_at': datetime.now().isoformat(),  # TODO: Add created_at to Weights table
                        'updated_at': datetime.now().isoformat()   # TODO: Add updated_at to Weights table
                    })
            
            return {'weight_sets': weight_sets}
            
        except Exception as e:
            logger.error(f"Error getting weight sets: {e}")
            return {'message': 'Internal server error'}, 500

    @write_auth_required
    @v1.doc('create_weight_set',
        body=weight_set_update_model,
        responses={
            201: ('Success', weight_set_model),
            400: ('Invalid parameters', error_model),
            401: ('Unauthorized', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def post(self):
        """Create a new weight set"""
        logger.info("POST /user/weight-sets called")
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            logger.info(f"User dict: {user_dict}")
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            logger.info(f"Created user object with ID: {user.id}")
            
            data = request.get_json()
            logger.info(f"Request data: {data}")
            if not data:
                return {'message': 'No data provided'}, 400
            
            name = data.get('name')
            description = data.get('description', '')
            weights = data.get('weights', [])
            
            logger.info(f"Parsed data - name: {name}, description: {description}, weights: {weights}")
            
            if not name:
                return {'message': 'Name is required'}, 400
            
            if not weights:
                return {'message': 'At least one weight is required'}, 400
            
            # Convert weights to the format expected by local.add_weights_set
            filters = {}
            for weight in weights:
                stat = weight.get('stat')
                value = weight.get('value')
                if stat and value is not None:
                    filters[stat] = float(value)
            
            logger.info(f"Converted filters: {filters}")
            
            # Import local functions for weight sets
            logger.info("Importing local module...")
            import local
            logger.info("Local module imported successfully")
            
            logger.info(f"Creating weight set with name: {name}, filters: {filters}")
            weight_set_id = local.add_weights_set(user, name, filters)
            logger.info(f"Weight set created with ID: {weight_set_id}")
            
            # Return the created weight set
            created_weight_set = {
                'id': weight_set_id,
                'name': name,
                'description': description,
                'weights': weights,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            logger.info(f"Returning created weight set: {created_weight_set}")
            return created_weight_set, 201
            
        except Exception as e:
            logger.error(f"Error creating weight set: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {'message': 'Internal server error'}, 500

class WeightSetResource(Resource):
    """Get, update, or delete a specific weight set"""
    
    @write_auth_required
    @v1.doc('get_weight_set',
        params={
            'weight_set_id': {'description': 'Weight set ID', 'type': 'integer', 'in': 'path', 'example': 1}
        },
        responses={
            200: ('Success', weight_set_model),
            401: ('Unauthorized', error_model),
            404: ('Weight set not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self, weight_set_id):
        """Get a specific weight set"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            # Import local functions for weight sets
            import local
            weight_set_data = local.get_weight_set(weight_set_id, user)
            
            if not weight_set_data:
                return {'message': 'Weight set not found'}, 404
            
            # Convert the data structure to match our API model
            weights = []
            for stat_name, stat_data in weight_set_data['stats'].items():
                weights.append({
                    'stat': stat_data['stat'],
                    'value': float(stat_data['value'])
                })
            
            weight_set = {
                'id': weight_set_id,
                'name': weight_set_data['name'],
                'description': f'Weight set: {weight_set_data["name"]}',
                'weights': weights,
                'created_at': datetime.now().isoformat(),  # Placeholder
                'updated_at': datetime.now().isoformat()   # Placeholder
            }
            
            return weight_set
            
        except Exception as e:
            logger.error(f"Error getting weight set {weight_set_id}: {e}")
            return {'message': 'Internal server error'}, 500

    @write_auth_required
    @v1.doc('update_weight_set',
        params={
            'weight_set_id': {'description': 'Weight set ID', 'type': 'integer', 'in': 'path', 'example': 1}
        },
        body=weight_set_update_model,
        responses={
            200: ('Success', weight_set_model),
            400: ('Invalid parameters', error_model),
            401: ('Unauthorized', error_model),
            404: ('Weight set not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def put(self, weight_set_id):
        """Update a weight set"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400
            
            weights = data.get('weights', [])
            if not weights:
                return {'message': 'At least one weight is required'}, 400
            
            # Convert weights to the format expected by local.update_weights_set
            filters = {}
            for weight in weights:
                stat = weight.get('stat')
                value = weight.get('value')
                if stat and value is not None:
                    filters[stat] = float(value)
            
            # Import local functions for weight sets
            import local
            result = local.update_weights_set(weight_set_id, filters, user)
            
            if not result:
                return {'message': 'Weight set not found or access denied'}, 404
            
            # Return the updated weight set
            updated_weight_set = {
                'id': weight_set_id,
                'name': data.get('name', 'Updated Weight Set'),
                'description': data.get('description', ''),
                'weights': weights,
                'created_at': datetime.now().isoformat(),  # Placeholder
                'updated_at': datetime.now().isoformat()
            }
            
            return updated_weight_set
            
        except Exception as e:
            logger.error(f"Error updating weight set {weight_set_id}: {e}")
            return {'message': 'Internal server error'}, 500

    @write_auth_required
    @v1.doc('delete_weight_set',
        params={
            'weight_set_id': {'description': 'Weight set ID', 'type': 'integer', 'in': 'path', 'example': 1}
        },
        responses={
            200: ('Success', success_message_model),
            401: ('Unauthorized', error_model),
            404: ('Weight set not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def delete(self, weight_set_id):
        """Delete a weight set"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            # Import local functions for weight sets
            import local
            success = local.delete_weights_set(user, weight_set_id)
            
            if not success:
                return {'message': 'Weight set not found or access denied'}, 404
            
            return {'message': 'Weight set deleted successfully'}
            
        except Exception as e:
            logger.error(f"Error deleting weight set {weight_set_id}: {e}")
            return {'message': 'Internal server error'}, 500

# Character models
character_model = v1.model('Character', {
    'id': fields.Integer(description='Character ID', example=1),
    'name': fields.String(description='Character name', example='MyWarrior'),
    'class1': fields.String(description='Primary character class', example='Warrior'),
    'class2': fields.String(description='Secondary character class', example=''),
    'class3': fields.String(description='Tertiary character class', example=''),
    'level': fields.Integer(description='Character level', example=50),
    'character_set': fields.String(description='Character set name', example='Tank Set'),
    'inventory_blob': fields.String(description='Inventory data as JSON string'),
    'created_at': fields.DateTime(description='Creation date'),
    'updated_at': fields.DateTime(description='Last update date')
})

character_create_model = v1.model('CharacterCreate', {
    'name': fields.String(required=True, description='Character name', example='MyWarrior'),
    'class1': fields.String(required=True, description='Primary character class', example='Warrior'),
    'class2': fields.String(description='Secondary character class', example=''),
    'class3': fields.String(description='Tertiary character class', example=''),
    'level': fields.Integer(required=True, description='Character level', example=50),
    'character_set': fields.String(description='Character set name', example='Tank Set'),
    'inventory_blob': fields.String(description='Inventory data as JSON string')
})

character_update_model = v1.model('CharacterUpdate', {
    'name': fields.String(description='Character name', example='MyWarrior'),
    'class1': fields.String(description='Primary character class', example='Warrior'),
    'class2': fields.String(description='Secondary character class', example=''),
    'class3': fields.String(description='Tertiary character class', example=''),
    'level': fields.Integer(description='Character level', example=50),
    'character_set': fields.String(description='Character set name', example='Tank Set'),
    'inventory_blob': fields.String(description='Inventory data as JSON string')
})

characters_list_model = v1.model('CharactersList', {
    'characters': fields.List(fields.Nested(character_model), description='List of user characters')
})

# Character routes
@v1.route('/characters')
class CharactersResource(Resource):
    """Get all characters for the authenticated user or create a new character"""
    
    @write_auth_required
    @v1.doc('get_characters',
        responses={
            200: ('Success', characters_list_model),
            401: ('Unauthorized', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self):
        """Get all characters for the authenticated user"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            # Import local functions for characters
            import local
            characters_data = local.get_characters(user)
            
            # Convert the data structure to match our API model
            characters = []
            for char_data in characters_data:
                character = {
                    'id': char_data['id'],
                    'name': char_data['name'],
                    'class1': char_data['classes'][0] if len(char_data['classes']) > 0 else '',
                    'class2': char_data['classes'][1] if len(char_data['classes']) > 1 else '',
                    'class3': char_data['classes'][2] if len(char_data['classes']) > 2 else '',
                    'level': char_data['level'],
                    'character_set': char_data['character_set'],
                    'inventory_blob': char_data['inventory_blob'],
                    'created_at': char_data['created_at'],
                    'updated_at': char_data['updated_at']
                }
                characters.append(character)
            
            return {'characters': characters}
            
        except Exception as e:
            logger.error(f"Error getting characters: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {'message': 'Internal server error'}, 500

    @write_auth_required
    @v1.doc('create_character',
        body=character_create_model,
        responses={
            201: ('Success', character_model),
            400: ('Invalid parameters', error_model),
            401: ('Unauthorized', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def post(self):
        """Create a new character"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400
            
            name = data.get('name')
            class1 = data.get('class1')
            class2 = data.get('class2', '')
            class3 = data.get('class3', '')
            level = data.get('level')
            character_set = data.get('character_set', '')
            inventory_blob = data.get('inventory_blob', '')
            
            if not name or not class1 or level is None:
                return {'message': 'Name, class1, and level are required'}, 400
            
            # Build classes list
            classes = [class1]
            if class2:
                classes.append(class2)
            if class3:
                classes.append(class3)
            
            # Import local functions for characters
            import local
            character_data = local.add_character(user, name, classes, level, character_set, inventory_blob)
            
            # Return the created character
            created_character = {
                'id': character_data['id'],
                'name': character_data['name'],
                'class1': character_data['classes'][0] if len(character_data['classes']) > 0 else '',
                'class2': character_data['classes'][1] if len(character_data['classes']) > 1 else '',
                'class3': character_data['classes'][2] if len(character_data['classes']) > 2 else '',
                'level': character_data['level'],
                'character_set': character_data['character_set'],
                'inventory_blob': character_data['inventory_blob'],
                'created_at': character_data['created_at'],
                'updated_at': character_data['updated_at']
            }
            
            return created_character, 201
            
        except Exception as e:
            logger.error(f"Error creating character: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {'message': 'Internal server error'}, 500

@v1.route('/characters/<int:character_id>')
class CharacterResource(Resource):
    """Get, update, or delete a specific character"""
    
    @write_auth_required
    @v1.doc('get_character',
        params={
            'character_id': {'description': 'Character ID', 'type': 'integer', 'in': 'path', 'example': 1}
        },
        responses={
            200: ('Success', character_model),
            401: ('Unauthorized', error_model),
            404: ('Character not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def get(self, character_id):
        """Get a specific character"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            # Import local functions for characters
            import local
            character_data = local.get_character(character_id, user)
            
            if not character_data:
                return {'message': 'Character not found'}, 404
            
            character = {
                'id': character_id,
                'name': character_data['name'],
                'class1': character_data['classes'][0] if len(character_data['classes']) > 0 else '',
                'class2': character_data['classes'][1] if len(character_data['classes']) > 1 else '',
                'class3': character_data['classes'][2] if len(character_data['classes']) > 2 else '',
                'level': character_data['level'],
                'character_set': character_data['character_set'],
                'inventory_blob': character_data['inventory_blob'],
                'created_at': character_data['created_at'],
                'updated_at': character_data['updated_at']
            }
            
            return character
            
        except Exception as e:
            logger.error(f"Error getting character {character_id}: {e}")
            return {'message': 'Internal server error'}, 500

    @write_auth_required
    @v1.doc('update_character',
        params={
            'character_id': {'description': 'Character ID', 'type': 'integer', 'in': 'path', 'example': 1}
        },
        body=character_update_model,
        responses={
            200: ('Success', character_model),
            400: ('Invalid parameters', error_model),
            401: ('Unauthorized', error_model),
            404: ('Character not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def put(self, character_id):
        """Update a character"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            data = request.get_json()
            if not data:
                return {'message': 'No data provided'}, 400
            
            # Build classes list if classes are provided
            classes = None
            if 'class1' in data or 'class2' in data or 'class3' in data:
                class1 = data.get('class1', '')
                class2 = data.get('class2', '')
                class3 = data.get('class3', '')
                classes = [class1]
                if class2:
                    classes.append(class2)
                if class3:
                    classes.append(class3)
            
            # Import local functions for characters
            import local
            result = local.update_character(
                cid=character_id,
                user=user,
                name=data.get('name'),
                classes=classes,
                level=data.get('level'),
                character_set=data.get('character_set'),
                inventory_blob=data.get('inventory_blob')
            )
            
            if not result:
                return {'message': 'Character not found or access denied'}, 404
            
            # Return the updated character
            updated_character = {
                'id': character_id,
                'name': result['name'],
                'class1': result['classes'][0] if len(result['classes']) > 0 else '',
                'class2': result['classes'][1] if len(result['classes']) > 1 else '',
                'class3': result['classes'][2] if len(result['classes']) > 2 else '',
                'level': result['level'],
                'character_set': result['character_set'],
                'inventory_blob': result['inventory_blob'],
                'created_at': result['created_at'],
                'updated_at': result['updated_at']
            }
            
            return updated_character
            
        except Exception as e:
            logger.error(f"Error updating character {character_id}: {e}")
            return {'message': 'Internal server error'}, 500

    @write_auth_required
    @v1.doc('delete_character',
        params={
            'character_id': {'description': 'Character ID', 'type': 'integer', 'in': 'path', 'example': 1}
        },
        responses={
            200: ('Success', success_message_model),
            401: ('Unauthorized', error_model),
            404: ('Character not found', error_model),
            500: ('Server error', error_model)
        },
        security='apikey'
    )
    def delete(self, character_id):
        """Delete a character"""
        try:
            # Get user from request context (set by middleware)
            user_dict = request.current_user
            if not user_dict:
                return {'message': 'Authentication required'}, 401
            
            # Create a simple user object for local functions
            class UserObject:
                def __init__(self, user_dict):
                    self.id = user_dict['id']
            
            user = UserObject(user_dict)
            
            # Import local functions for characters
            import local
            success = local.delete_character(character_id, user)
            
            if not success:
                return {'message': 'Character not found or access denied'}, 404
            
            return {'message': 'Character deleted successfully'}
            
        except Exception as e:
            logger.error(f"Error deleting character {character_id}: {e}")
            return {'message': 'Internal server error'}, 500
