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
from .auth import auth
from .auth_routes import auth_ns
from .middleware import optional_auth, write_auth_required, admin_required

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
    'serialized': fields.String(description='Serialized item data', example='{"stats": {"damage": "1-5"}}')
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
    'expansion_name': fields.String(description='Expansion name', example='Classic')
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
    'notes': fields.String(description='Additional notes', example='Custom server item')
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
            'type': {'description': 'Filter items by type', 'type': 'string', 'example': 'weapon'}
        },
        responses={
            200: ('Success', [item_model]),
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
        * type: Filter items by type (optional)
        
        Returns a list of items matching the criteria.
        """
        try:
            item_id = request.args.get('id', type=int)
            name = request.args.get('name')
            item_type = request.args.get('type')
            
            # Get items from database
            items = item_db.get_item_raw_data(item_id=item_id, name=name, item_type=item_type)
            
            if not items:
                v1.abort(404, "No items found")
            
            # Format response
            if isinstance(items, list):
                formatted_items = []
                for item in items:
                    formatted_item = format_item_response(item)
                    formatted_items.append(formatted_item)
                return formatted_items
            else:
                # Single item
                return format_item_response(items)
            
        except Exception as e:
            v1.abort(500, f"Error retrieving items: {str(e)}")

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

@v1.route('/zones/<string:short_name>/details')
class ZoneExtraDetailsResource(Resource):
    @optional_auth
    @v1.doc('get_zone_details_by_short_name',
        params={'short_name': {'description': 'Zone short name', 'in': 'path'}},
        responses={
            200: ('Success', 'ZoneDetails'),
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

@v1.route('/quests/zones/<expansion>')
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
            'expansion_id': {'description': 'Expansion ID', 'type': 'integer', 'in': 'path', 'example': 0}
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
        
        Get zones using the expansion_id parameter:
        * expansion_id: Expansion ID (path parameter)
        
        Returns a list of zones in the specified expansion.
        """
        try:
            # First check if expansion exists
            expansion_data = expansion_db.get_expansion_by_id(expansion_id)
            if not expansion_data:
                v1.abort(404, "Expansion not found")
            
            zones = expansion_db.get_zones_in_expansion(expansion_id)
            return {'zones': zones}
        except Exception as e:
            v1.abort(500, f"Error retrieving zones: {str(e)}")

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

def init_routes(api):
    """Initialize all routes"""
    logger.info("Initializing API routes")
    
    # Add resources to the v1 namespace
    v1.add_resource(ItemResource, '/items')
    v1.add_resource(SpellResource, '/spells')
    v1.add_resource(SpellClassesResource, '/spells/classes')
    v1.add_resource(SpellsByClassResource, '/spells/list/<string:class_names>')
    v1.add_resource(NPCResource, '/npcs')
    v1.add_resource(ZoneResource, '/zones')
    v1.add_resource(ZoneDetailResource, '/zones/<string:identifier>')
    v1.add_resource(ZoneExtraDetailsResource, '/zones/<string:short_name>/details')
    v1.add_resource(ConnectedZoneResource, '/zones/<string:short_name>/connected')
    v1.add_resource(WaypointResource, '/zones/waypoints')
    v1.add_resource(TradeskillResource, '/tradeskills')
    v1.add_resource(RecipeResource, '/recipes')
    v1.add_resource(QuestResource, '/quests')
    v1.add_resource(QuestChainResource, '/quests/chains')
    v1.add_resource(QuestItemResource, '/quests/items')
    v1.add_resource(QuestZoneResource, '/quests/zones')
    v1.add_resource(QuestExpansionResource, '/quests/expansions')
    v1.add_resource(QuestZoneByExpansionResource, '/quests/zones/<expansion>')
    v1.add_resource(ExpansionsResource, '/expansions')
    v1.add_resource(ExpansionResource, '/expansions/<int:expansion_id>')
    v1.add_resource(ExpansionSearchResource, '/expansions/search')
    v1.add_resource(ExpansionZonesResource, '/expansions/<int:expansion_id>/zones')
    v1.add_resource(ExpansionItemsResource, '/expansion-items')
    v1.add_resource(ExpansionItemsSummaryResource, '/expansion-items/summary')
    v1.add_resource(CustomItemsResource, '/expansion-items/custom')
    v1.add_resource(CustomItemResource, '/expansion-items/custom/<int:item_id>/<int:expansion_id>')
    v1.add_resource(ImportItemsResource, '/expansion-items/import')

    # Add authentication namespace
    api.add_namespace(auth_ns, path='/auth')
    
    # Create default admin user
    auth.create_default_admin()
    
    logger.info("API routes initialization complete")
