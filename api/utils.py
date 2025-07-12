from datetime import datetime
from decimal import Decimal
import os
here = os.path.dirname(os.path.abspath(__file__))

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


def parse_skill(skill_num):
    if skill_num == 0:
        return '1H Blunt'
    elif skill_num == 1:
        return '1H Slashing'
    elif skill_num == 2:
        return '2H Blunt'
    elif skill_num == 3:
        return '2H Slashing'
    elif skill_num == 4:
        return 'Abjuration'
    elif skill_num == 5:
        return 'Alteration'
    elif skill_num == 6:
        return 'Apply Poison'
    elif skill_num == 7:
        return 'Archery'
    elif skill_num == 8:
        return 'Backstab'
    elif skill_num == 9:
        return 'Bind Wounds'
    elif skill_num == 10:
        return 'Bash'
    elif skill_num == 11:
        return 'Block'
    elif skill_num == 12:
        return 'Brass Instruments'
    elif skill_num == 13:
        return 'Channeling'
    elif skill_num == 14:
        return 'Conjuration'
    elif skill_num == 15:
        return 'Defense'
    elif skill_num == 16:
        return 'Disarm'
    elif skill_num == 17:
        return 'Disarm Traps'
    elif skill_num == 18:
        return 'Divination'
    elif skill_num == 19:
        return 'Dodge'
    elif skill_num == 20:
        return 'Double Attack'
    elif skill_num == 21:
        return 'Dragon Punch'
    elif skill_num == 22:
        return 'Dual Wield'
    elif skill_num == 23:
        return 'Eagle Strike'
    elif skill_num == 24:
        return 'Evocation'
    elif skill_num == 25:
        return 'Feign Death'
    elif skill_num == 26:
        return 'Flying Kick'
    elif skill_num == 27:
        return 'Forage'
    elif skill_num == 28:
        return 'Hand to Hand'
    elif skill_num == 29:
        return 'Hide'
    elif skill_num == 30:
        return 'Kick'
    elif skill_num == 31:
        return 'Meditate'
    elif skill_num == 32:
        return 'Mend'
    elif skill_num == 33:
        return 'Offense'
    elif skill_num == 34:
        return 'Parry'
    elif skill_num == 35:
        return 'Pick Locks'
    elif skill_num == 36:
        return 'Piercing'
    elif skill_num == 37:
        return 'Riposte'
    elif skill_num == 38:
        return 'Round Kick'
    elif skill_num == 39:
        return 'Safe Fall'
    elif skill_num == 40:
        return 'Sense Heading'
    elif skill_num == 41:
        return 'Singing'
    elif skill_num == 42:
        return 'Sneak'
    elif skill_num == 43:
        return 'Specialize Abjuration'
    elif skill_num == 44:
        return 'Specialize Alteration'
    elif skill_num == 45:
        return 'Specialize Conjuration'
    elif skill_num == 46:
        return 'Specialize Divination'
    elif skill_num == 47:
        return 'Specialize Evocation'
    elif skill_num == 48:
        return 'Pick Pockets'
    elif skill_num == 49:
        return 'Stringed Instruments'
    elif skill_num == 50:
        return 'Swimming'
    elif skill_num == 51:
        return 'Throwing'
    elif skill_num == 52:
        return 'Tiger Claw'
    elif skill_num == 53:
        return 'Tracking'
    elif skill_num == 54:
        return 'Wind Instruments'
    elif skill_num == 55:
        return 'Fishing'
    elif skill_num == 56:
        return 'Poison Making'
    elif skill_num == 57:
        return 'Tinkering'
    elif skill_num == 58:
        return 'Research'
    elif skill_num == 59:
        return 'Alchemy'
    elif skill_num == 60:
        return 'Baking'
    elif skill_num == 61:
        return 'Tailoring'
    elif skill_num == 62:
        return 'Sense Traps'
    elif skill_num == 63:
        return 'Blacksmithing'
    elif skill_num == 64:
        return 'Fletching'
    elif skill_num == 65:
        return 'Brewing'
    elif skill_num == 66:
        return 'Alcohol Tolerance'
    elif skill_num == 67:
        return 'Begging'
    elif skill_num == 68:
        return 'Jewel Crafting'
    elif skill_num == 69:
        return 'Pottery'
    elif skill_num == 70:
        return 'Percussion Instruments'
    elif skill_num == 71:
        return 'Intimidate'
    elif skill_num == 72:
        return 'Berserking'
    elif skill_num == 73:
        return 'Taunt'
    elif skill_num == 74:
        return 'Frenzy'
    elif skill_num == 75:
        return 'Non-Tradeskill'
    elif skill_num == 76:
        return 'Triple Attack'
    elif skill_num == 77:
        return '2H Piercing'
    elif skill_num == 255:
        return 'none'
    else:
        return f'Unknown Skill: {skill_num}'

    
def get_exclusion_list(name):
    with open(os.path.join(here, 'Exclusion', f'{name}.txt')) as fh:
        data = fh.read()
    return data.split('\n')    

def get_elem_dmg_type(num):
    """Returns the elemental damage type."""
    if num == 1:
        return 'Magic'
    elif num == 2:
        return 'Fire'
    elif num == 3:
        return 'Cold'
    elif num == 4:
        return 'Poison'
    elif num == 5:
        return 'Disease'
    elif num == 6:
        return 'Chromatic'
    elif num == 7:
        return 'Prismatic'
    elif num == 8:
        return 'Phys'
    elif num == 9:
        return 'Corruption'
    else:
        raise Exception(f'Unknown elemental type: {num}')


