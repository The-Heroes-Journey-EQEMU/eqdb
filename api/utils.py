from datetime import datetime
from decimal import Decimal

def format_item_response(item_data, all_keys=None):
    """Format item data for API response"""
    if not item_data:
        return {}
    
    # Convert None to empty string and datetime to ISO format
    formatted_data = {}
    for key in all_keys or item_data.keys():
        value = item_data.get(key)
        if isinstance(value, datetime):
            formatted_data[key] = value.isoformat()
        elif isinstance(value, Decimal):
            formatted_data[key] = float(value)
        else:
            formatted_data[key] = "" if value is None else value
    
    return formatted_data

def format_npc_response(npc_data, all_keys=None):
    """Format NPC data for API response"""
    if not npc_data:
        return {}
    
    # Convert None to empty string and datetime to ISO format
    formatted_data = {}
    for key in all_keys or npc_data.keys():
        value = npc_data.get(key)
        if isinstance(value, datetime):
            formatted_data[key] = value.isoformat()
        elif isinstance(value, Decimal):
            formatted_data[key] = float(value)
        else:
            formatted_data[key] = "" if value is None else value
    
    return formatted_data

def format_spell_response(spell_data, all_keys=None):
    """Format spell data for API response"""
    if not spell_data:
        return {}
    
    # Convert None to empty string and datetime to ISO format
    formatted_data = {}
    for key in all_keys or spell_data.keys():
        value = spell_data.get(key)
        if isinstance(value, datetime):
            formatted_data[key] = value.isoformat()
        elif isinstance(value, Decimal):
            formatted_data[key] = float(value)
        else:
            formatted_data[key] = "" if value is None else value
    
    return formatted_data

def format_zone_response(zone_data, all_keys=None):
    """Format zone data for API response"""
    if not zone_data:
        return {}
    
    # Convert None to empty string and datetime to ISO format
    formatted_data = {}
    for key in all_keys or zone_data.keys():
        value = zone_data.get(key)
        if isinstance(value, datetime):
            formatted_data[key] = value.isoformat()
        elif isinstance(value, Decimal):
            formatted_data[key] = float(value)
        else:
            formatted_data[key] = "" if value is None else value
    
    return formatted_data 