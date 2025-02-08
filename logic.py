"""EQDB Logic File"""
import configparser
import datetime
import operator
import os
import utils

from sqlalchemy import create_engine, and_, or_, Column, Integer
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

here = os.path.dirname(__file__)
site_config = configparser.RawConfigParser()
ini_path = os.path.join(here, 'configuration.ini')
site_config.read_file(open(ini_path))

driver = site_config.get('database', 'driver')
user = site_config.get('database', 'user')
password = site_config.get('database', 'password')
database = site_config.get('database', 'database')
host = site_config.get('database', 'host')
port = site_config.get('database', 'port')

engine = create_engine(f'{driver}{user}:{password}@{host}:{port}/{database}')

Base = automap_base()


class ItemRedirection(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)


Base.prepare(autoload_with=engine)

Zone = Base.classes.zone
Item = ItemRedirection
Spawn2 = Base.classes.spawn2
SpawnEntry = Base.classes.spawnentry
NPCTypes = Base.classes.npc_types
LootTableEntries = Base.classes.loottable_entries
LootDropEntries = Base.classes.lootdrop_entries
SpellsNewReference = Base.classes.spells_new_reference


def _get_link_filters():
    """Helper to return the basic link filters between zone, npc, and item"""
    return [NPCTypes.loottable_id == LootTableEntries.loottable_id,
            LootTableEntries.lootdrop_id == LootDropEntries.lootdrop_id,
            LootDropEntries.item_id == Item.id]


def _get_arg_list(gather_base=False, get_focus_info=False, gather_e_l=False, tooltip=False):
    """Helper to return things we want to search for."""
    arg_list = [Item.id]
    if gather_base:
        arg_list.append(Item.Name)
        arg_list.append(Item.hp)
        arg_list.append(Item.mana)
        arg_list.append(Item.endur)
        arg_list.append(Item.ac)
        arg_list.append(Item.damage)
        arg_list.append(Item.aagi)
        arg_list.append(Item.acha)
        arg_list.append(Item.adex)
        arg_list.append(Item.aint)
        arg_list.append(Item.asta)
        arg_list.append(Item.astr)
        arg_list.append(Item.awis)
        arg_list.append(Item.heroic_agi)
        arg_list.append(Item.heroic_cha)
        arg_list.append(Item.heroic_dex)
        arg_list.append(Item.heroic_int)
        arg_list.append(Item.heroic_sta)
        arg_list.append(Item.heroic_str)
        arg_list.append(Item.heroic_wis)
        arg_list.append(Item.cr)
        arg_list.append(Item.dr)
        arg_list.append(Item.fr)
        arg_list.append(Item.mr)
        arg_list.append(Item.pr)
        arg_list.append(Item.heroic_cr)
        arg_list.append(Item.heroic_dr)
        arg_list.append(Item.heroic_fr)
        arg_list.append(Item.heroic_mr)
        arg_list.append(Item.heroic_pr)
        arg_list.append(Item.attack)
        arg_list.append(Item.haste)
        arg_list.append(Item.regen)
        arg_list.append(Item.manaregen)
        arg_list.append(Item.enduranceregen)
        arg_list.append(Item.healamt)
        arg_list.append(Item.spelldmg)
        arg_list.append(Item.accuracy)
        arg_list.append(Item.avoidance)
        arg_list.append(Item.combateffects)
        arg_list.append(Item.damageshield)
        arg_list.append(Item.dotshielding)
        arg_list.append(Item.shielding)
        arg_list.append(Item.spellshield)
        arg_list.append(Item.strikethrough)
        arg_list.append(Item.stunresist)
        arg_list.append(Item.delay)
        arg_list.append(Item.proceffect)
        arg_list.append(Item.focuseffect)
        arg_list.append(Item.clickeffect)
    if tooltip:
        arg_list.append(Item.classes)
        arg_list.append(Item.slots)
        arg_list.append(Item.itemtype)
        arg_list.append(Item.proceffect)
        arg_list.append(Item.focuseffect)
        arg_list.append(Item.clickeffect)
    if gather_base and not gather_e_l:
        arg_list.append(NPCTypes.name.label('npc_name'))
        arg_list.append(NPCTypes.id.label('npc_id'))
    if get_focus_info:
        arg_list.append(SpellsNewReference.name)
        arg_list.append(SpellsNewReference.effect_base_value1)
        arg_list.append(SpellsNewReference.effect_limit_value1)

    return arg_list


def _filter_file_based_items(items, gather_lego, gather_ench, gather_base, kwargs, source, zone_id):
    """Helper to filter file based items."""
    quest_skip_entries = ['base_items', 'ench_items', 'lego_items', 'sub_type', 'eras', 'proc', 'norent', 'click',
                          'sympathetic']
    filtered_quest_items = []
    for item in items:
        do_not_add = False
        if gather_lego and item.id <= 2000000:
            continue
        elif gather_ench and (item.id > 2000000 or item.id <= 1000000):
            continue
        elif gather_base and item.id >= 1000000:
            continue

        usable_by_class = False
        for entry in kwargs:
            if do_not_add:
                break
            if 'item_name' in entry:
                if kwargs['item_name'] not in item.Name:
                    do_not_add = True
            elif 'g_class_1' in entry:
                class_value = utils.lookup_class(kwargs['g_class_1'])
                if item.classes & class_value == class_value:
                    usable_by_class = True
            elif 'g_class_2' in entry:
                class_value = utils.lookup_class(kwargs['g_class_2'])
                if item.classes & class_value == class_value:
                    usable_by_class = True
            elif 'g_class_3' in entry:
                class_value = utils.lookup_class(kwargs['g_class_3'])
                if item.classes & class_value == class_value:
                    usable_by_class = True
            elif 'g_slot' in entry:
                slot_value = utils.lookup_slot(kwargs['g_slot'])
                if item.slots & slot_value != slot_value:
                    do_not_add = True
            elif 'i_type' in entry:
                if kwargs['i_type'] == 'Any':
                    continue
                elif kwargs['i_type'] == 'Augment':
                    if hasattr(item, 'augtype'):
                        if item.augtype <= 0:
                            do_not_add = True
                    else:
                        do_not_add = True
                elif kwargs['i_type'] == 'Any 1H Weapon':
                    if (item.itemtype != utils.lookup_weapon_types('One Hand Slash') and
                        item.itemtype != utils.lookup_weapon_types('One Hand Piercing') and
                        item.itemtype != utils.lookup_weapon_types('One Hand Blunt') and
                        item.itemtype != utils.lookup_weapon_types('Hand to Hand')):
                        do_not_add = True
                elif kwargs['i_type'] == 'Any 2H Weapon':
                    if (item.itemtype != utils.lookup_weapon_types('Two Hand Slash') and
                        item.itemtype != utils.lookup_weapon_types('Two Hand Piercing') and
                        item.itemtype != utils.lookup_weapon_types('Two Hand Blunt')):
                        do_not_add = True
                elif kwargs['i_type'] == 'Exclude 1H Weapon':
                    if (item.itemtype == utils.lookup_weapon_types('One Hand Slash') or
                        item.itemtype == utils.lookup_weapon_types('One Hand Piercing') or
                        item.itemtype == utils.lookup_weapon_types('One Hand Blunt') or
                        item.itemtype == utils.lookup_weapon_types('Hand to Hand')):
                        do_not_add = True
                elif kwargs['i_type'] == 'Exclude 2H Weapon':
                    if (item.itemtype == utils.lookup_weapon_types('Two Hand Slash') or
                        item.itemtype == utils.lookup_weapon_types('Two Hand Piercing') or
                        item.itemtype == utils.lookup_weapon_types('Two Hand Blunt')):
                        do_not_add = True
                else:
                    if item.itemtype != utils.lookup_weapon_types(kwargs['i_type']):
                        do_not_add = True
            elif 'proc' in entry:
                if item.proceffect < 1:
                    do_not_add = True
            elif 'click' in entry:
                if item.clickeffect < 1:
                    do_not_add = True
            elif entry in quest_skip_entries:
                continue
            elif 'focus_type' in entry:
                ids = utils.get_focus_values(kwargs['focus_type'], kwargs['sub_type'])
                valid_focus_found = False
                for focus_id in ids:
                    if item.focuseffect == focus_id:
                        valid_focus_found = True
                        break
                if not valid_focus_found:
                    do_not_add = True
            else:
                if getattr(item, entry) < kwargs[entry]:
                    do_not_add = True
        if not usable_by_class:
            do_not_add = True
        if do_not_add:
            continue
        else:
            item.npc_name = source
            item.npc_id = zone_id
            if hasattr(item, 'name'):
                item.focus_spell_name = item.name
            if hasattr(item, 'effect_base_value1'):
                item.focus_min_val = item.effect_base_value1
            if hasattr(item, 'effect_limit_value1'):
                item.focus_max_val = item.effect_limit_value1
            filtered_quest_items.append(item)
    return filtered_quest_items


def get_item_data(item_id):
    """Returns the basic data for an item, used for tooltips."""

    with Session(bind=engine) as session:
        # Get the item
        args = _get_arg_list(gather_base=True, get_focus_info=False, gather_e_l=True, tooltip=True)
        query = session.query(*args).filter(Item.id == item_id)
        result = query.all()
        ret_dict = dict(result[0]._mapping)

        proc = result[0]._mapping['proceffect']
        click = result[0]._mapping['clickeffect']
        focus = result[0]._mapping['focuseffect']

        if proc > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == proc)
            result = query.all()
            ret_dict['proc_name'] = result[0][0]
        if click > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == click)
            result = query.all()
            ret_dict['click_name'] = result[0][0]
            if 'Sympathetic Strike' in ret_dict['click_name']:
                split_name = ret_dict['click_name'].split('of Flames')
                ret_dict['click_name'] = f'{split_name[0]}{split_name[1]}'
            if 'Sympathetic Healing' in ret_dict['click_name']:
                split_name = ret_dict['click_name'].split('Burst')
                ret_dict['click_name'] = f'{split_name[0]}{split_name[1]}'
        if focus > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == focus)
            result = query.all()
            ret_dict['focus_name'] = result[0][0]

    ret_dict['Name'] = utils.fix_item_name(ret_dict['Name'], ret_dict['id'])
    ret_dict['class_str'] = utils.get_class_string(ret_dict['classes'])
    ret_dict['slot_str'] = utils.get_slot_string(ret_dict['slots'])
    ret_dict['type_str'] = utils.get_type_string(ret_dict['itemtype'])
    return ret_dict


def get_items_with_filters(weights, ignore_zero, **kwargs):
    """Returns all items with filters provided"""
    # Set up basic database filters
    filters = []
    weapon_or_filters = []
    era_or_filters = []
    focus_or_filters = []
    zone_or_filters = []
    class_or_filters = []
    link_filters = _get_link_filters()
    skip_entries = ['base_items', 'ench_items', 'lego_items', 'sub_type', 'sympathetic']
    aug_search = False
    no_rent = False
    get_focus_info = False
    quest_items = []
    special_items = []

    # Determine if we need enchanted or legendary items
    gather_base = True
    gather_ench = True
    gather_lego = True
    if 'lego_items' in kwargs:
        if kwargs['lego_items']:
            gather_base = False
            gather_ench = False
            gather_lego = True
    elif 'ench_items' in kwargs:
        if kwargs['ench_items']:
            gather_base = False
            gather_ench = True
            gather_lego = False
    elif 'base_items' in kwargs:
        if kwargs['base_items']:
            gather_base = True
            gather_ench = False
            gather_lego = False

    for entry in kwargs:
        if 'item_name' in entry:
            partial = "%%%s%%" % (kwargs['item_name'])
            filters.append(Item.Name.like(partial))
        elif 'g_class_1' in entry:
            class_value = utils.lookup_class(kwargs['g_class_1'])
            class_or_filters.append(Item.classes.op('&')(class_value) == class_value)
        elif 'g_class_2' in entry:
            class_value = utils.lookup_class(kwargs['g_class_2'])
            class_or_filters.append(Item.classes.op('&')(class_value) == class_value)
        elif 'g_class_3' in entry:
            class_value = utils.lookup_class(kwargs['g_class_3'])
            class_or_filters.append(Item.classes.op('&')(class_value) == class_value)
        elif 'g_slot' in entry:
            slot_value = utils.lookup_slot(kwargs['g_slot'])
            filters.append(Item.slots.op('&')(slot_value) == slot_value)
        elif 'eras' in entry:
            # We need to link through to all the NPCs in all the zones of the era to get all the items they drop.
            for era in kwargs['eras']:
                zone_id_list = utils.get_era_zones(era)
                for zone_id in zone_id_list:
                    zone_or_filters.append(NPCTypes.id.like(f'{zone_id}___'))
                # Now, we need to get the quest items.  These are stored in files
                with open(os.path.join(here, 'item_files', f'{era}.txt'), 'r') as fh:
                    file_data = fh.read()
                era_quest_items = file_data.split('\n')
                for item_entry in era_quest_items:
                    if not item_entry:
                        continue
                    quest_items.append(utils.FileItem(eval(item_entry)))
                # Certain expansions have tradeskill items at the highest level, add those
                if era == 'Planes':
                    with open(os.path.join(here, 'item_files/planes_special.txt'), 'r') as fh:
                        file_data = fh.read()
                    era_ts_items = file_data.split('\n')
                    for item_entry in era_ts_items:
                        if not item_entry:
                            continue
                        special_items.append(utils.FileItem(eval(item_entry)))
        elif 'i_type' in entry:
            if kwargs['i_type'] == 'Any':
                continue
            elif kwargs['i_type'] == 'Augment':
                aug_search = True
            elif kwargs['i_type'] == 'Any 1H Weapon':
                weapon_or_filters.append(Item.itemtype == utils.lookup_weapon_types('One Hand Slash'))
                weapon_or_filters.append(Item.itemtype == utils.lookup_weapon_types('One Hand Blunt'))
                weapon_or_filters.append(Item.itemtype == utils.lookup_weapon_types('One Hand Piercing'))
                weapon_or_filters.append(Item.itemtype == utils.lookup_weapon_types('Hand to Hand'))
            elif kwargs['i_type'] == 'Any 2H Weapon':
                weapon_or_filters.append(Item.itemtype == utils.lookup_weapon_types('Two Hand Slash'))
                weapon_or_filters.append(Item.itemtype == utils.lookup_weapon_types('Two Hand Blunt'))
                weapon_or_filters.append(Item.itemtype == utils.lookup_weapon_types('Two Hand Piercing'))
            elif kwargs['i_type'] == 'Exclude 1H Weapon':
                filters.append(Item.itemtype != utils.lookup_weapon_types('One Hand Slash'))
                filters.append(Item.itemtype != utils.lookup_weapon_types('One Hand Blunt'))
                filters.append(Item.itemtype != utils.lookup_weapon_types('One Hand Piercing'))
                filters.append(Item.itemtype != utils.lookup_weapon_types('Hand to Hand'))
            elif kwargs['i_type'] == 'Exclude 2H Weapon':
                filters.append(Item.itemtype != utils.lookup_weapon_types('Two Hand Slash'))
                filters.append(Item.itemtype != utils.lookup_weapon_types('Two Hand Blunt'))
                filters.append(Item.itemtype != utils.lookup_weapon_types('Two Hand Piercing'))
            else:
                filters.append(Item.itemtype == utils.lookup_weapon_types(kwargs['i_type']))
        elif 'proc' in entry:
            filters.append(Item.proceffect >= 1)
        elif 'click' in entry:
            filters.append(Item.clickeffect >= 1)
        elif entry in skip_entries:
            continue
        elif 'focus_type' in entry:
            ids = utils.get_focus_values(kwargs['focus_type'], kwargs['sub_type'])
            for focus_id in ids:
                focus_or_filters.append(Item.focuseffect == focus_id)
            get_focus_info = True
            link_filters.append(Item.focuseffect == SpellsNewReference.id)
        elif 'no_rent' in entry:
            no_rent = True

    # Apply universal filters
    if aug_search:
        filters.append(Item.augtype > 0)
    else:
        filters.append(Item.augtype <= 0)
    if not no_rent:
        filters.append(Item.norent == 1)

    # Filters are set, run them!
    and_params = and_(*filters)
    weapon_or_params = or_(*weapon_or_filters)
    era_and_params = or_(*era_or_filters)
    focus_or_params = or_(*focus_or_filters)
    zone_or_params = or_(*zone_or_filters)
    class_or_params = or_(*class_or_filters)
    link_params = and_(*link_filters)
    arg_list = _get_arg_list(True, get_focus_info)

    session = Session(bind=engine)
    query = session.query(*arg_list) \
        .filter(and_params) \
        .filter(weapon_or_params) \
        .filter(era_and_params) \
        .filter(focus_or_params) \
        .filter(zone_or_params) \
        .filter(class_or_params) \
        .filter(link_params) \
        .group_by(Item.id)
    base_items = query.all()

    # Okay, part one is done.  Now, get the legendary and enchanted items, if needed.
    if gather_base:
        all_items = []
        for entry in base_items:
            all_items.append(utils.ReducedItem(eval(str(entry._mapping))))
    else:
        item_filters = []
        lookup = {}
        for entry in base_items:
            if gather_ench:
                item_id = entry[0] + 1000000
            else:
                item_id = entry[0] + 2000000
            if get_focus_info:
                lookup.update({item_id: {'npc_name': entry[51], 'npc_id': entry[52], 'focus_name': entry[53],
                                         'focus_min': entry[54], 'focus_max': entry[55]}})
            else:
                lookup.update({item_id: {'npc_name': entry[51], 'npc_id': entry[52]}})
            item_filters.append(Item.id == item_id)

        item_params = or_(*item_filters)
        arg_list = _get_arg_list(True, False, gather_e_l=True)
        query = session.query(*arg_list).filter(item_params).group_by(Item.id)
        result = query.all()
        all_items = []

        for entry in result:
            entry = utils.ReducedItem(eval(str(entry._mapping)))
            if get_focus_info:
                entry.npc_name = lookup[entry.id]['npc_name']
                entry.npc_id = lookup[entry.id]['npc_id']
                entry.focus_spell_name = lookup[entry.id]['focus_name']
                entry.focus_min_val = lookup[entry.id]['focus_min']
                entry.focus_max_val = lookup[entry.id]['focus_max']
                all_items.append(entry)
            else:
                entry.npc_name = lookup[entry.id]['npc_name']
                entry.npc_id = lookup[entry.id]['npc_id']
                all_items.append(entry)
    session.close()

    # Now, we need to filter out quest items that don't meet filters
    all_items += _filter_file_based_items(quest_items, gather_lego, gather_ench, gather_base, kwargs, 'Quest', -1)

    # Do it again for special items
    if special_items:
        all_items += _filter_file_based_items(special_items, gather_lego, gather_ench, gather_base, kwargs,
                                              'Tradeskill', -2)

    out_items = []
    # Finally, lets get the value for the items and do some last minute cleanup
    for entry in all_items:
        check_filters = ['hp', 'mana', 'endur', 'ac', 'damage', 'aagi', 'acha', 'adex', 'aint', 'asta', 'astr',
                         'awis', 'heroic_agi', 'heroic_cha', 'heroic_dex', 'heroic_int', 'heroic_sta', 'heroic_str',
                         'heroic_wis', 'cr', 'dr', 'fr', 'mr', 'pr', 'attack', 'haste', 'regen', 'managerenge',
                         'enduranceregen', 'healmt', 'spelldmg', 'accuracy', 'avoidance', 'combateffects',
                         'damageshield', 'dotshielding', 'shielding', 'spellshield', 'strikethrough', 'stunresist']
        do_not_add = False
        for check in check_filters:
            if check in kwargs:
                if not getattr(entry, check) >= kwargs[check]:
                    do_not_add = True
                    break
        if do_not_add:
            continue

        if gather_lego and 'sympathetic' in kwargs:
            do_not_add = False
            if kwargs['sympathetic'] == 'all_strike':
                add = False
                for i in range(24356, 24366):
                    if int(entry.clickeffect) == i:
                        add = True
                        break
                if not add:
                    do_not_add = True
            elif kwargs['sympathetic'] == 'all_heal':
                add = False
                for i in range(24434, 24444):
                    if int(entry.clickeffect) == i:
                        add = True
                        break
                if not add:
                    do_not_add = True
            else:
                if int(entry.clickeffect) != int(kwargs['sympathetic']):
                    do_not_add = True
            if do_not_add:
                continue

        if get_focus_info:
            entry.focus_type = kwargs['focus_type']
            entry.sub_focus = kwargs['sub_type']

        if weights:
            entry.weight = utils.get_stat_weights(weights, entry)
            if ignore_zero and entry.weight == 0:
                continue
        else:
            entry.weight = 0

        # Add the weapon efficiency
        if entry.delay > 0:
            w_eff = '%.2f' % round(entry.damage / entry.delay, 2)
        else:
            w_eff = 0
        entry.w_eff = w_eff
        entry.Name = utils.fix_item_name(entry.Name, entry.id)
        entry.zone_name = utils.lookup_zone_name(entry.npc_id)
        entry.npc_name = utils.fix_npc_name(entry.npc_name)

        out_items.append(entry)

    out_items.sort(key=operator.attrgetter('weight'), reverse=True)
    return out_items
