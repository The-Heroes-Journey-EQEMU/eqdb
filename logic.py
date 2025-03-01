"""EQDB Logic File"""
import configparser
import datetime
import operator
import os
import utils

from sqlalchemy import create_engine, and_, or_, Column, Integer
from sqlalchemy.orm import Session, aliased
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
FocusSpell = aliased(SpellsNewReference)
ClickSpell = aliased(SpellsNewReference)
ProcSpell = aliased(SpellsNewReference)
WornSpell = aliased(SpellsNewReference)
BardSpell = aliased(SpellsNewReference)


def _debugger():
    data = []
    args = [Item.id.label('item_id'), Item.Name.label('item_name'), Item.heroic_int.label('item_heroic_int'),
            FocusSpell.id.label('focus_id'),
            FocusSpell.name.label('focus_name'),
            ClickSpell.id.label('click_id'),
            ClickSpell.name.label('click_name'),
            ProcSpell.id.label('proc_id'),
            ProcSpell.id.label('proc_name')]
    with Session(bind=engine) as session:
        query = session.query(*args).\
            join(FocusSpell, FocusSpell.id == Item.focuseffect, isouter=True).\
            join(ClickSpell, ClickSpell.id == Item.clickeffect, isouter=True).\
            join(ProcSpell, ProcSpell.id == Item.proceffect, isouter=True).\
            filter(Item.id.in_(session.query(Item.id + 2000000).filter(or_((Item.id == 1001), (Item.id == 26778), (Item.id == 1154), (Item.id == 7825))))).\
            group_by(Item.id)
        result = query.all()

    for entry in result:
        data.append(entry._mapping)
    return data


def _get_link_filters():
    """Helper to return the basic link filters between zone, npc, and item"""
    return [NPCTypes.loottable_id == LootTableEntries.loottable_id,
            LootTableEntries.lootdrop_id == LootDropEntries.lootdrop_id,
            LootDropEntries.item_id == Item.id]


def _get_arg_list(tooltip=False):
    """Helper to return things we want to search for."""
    arg_list = [Item.id, Item.Name, Item.hp, Item.mana, Item.endur, Item.ac, Item.damage, Item.aagi, Item.acha,
                Item.adex, Item.aint, Item.asta, Item.astr, Item.awis, Item.heroic_agi, Item.heroic_cha,
                Item.heroic_dex, Item.heroic_int, Item.heroic_sta, Item.heroic_str, Item.heroic_wis, Item.cr, Item.dr,
                Item.fr, Item.mr, Item.pr, Item.heroic_cr, Item.heroic_dr, Item.heroic_fr, Item.heroic_mr,
                Item.heroic_pr, Item.attack, Item.haste, Item.regen, Item.manaregen, Item.enduranceregen, Item.healamt,
                Item.spelldmg, Item.accuracy, Item.avoidance, Item.combateffects, Item.damageshield, Item.dotshielding,
                Item.shielding, Item.spellshield, Item.strikethrough, Item.stunresist, Item.delay, Item.proceffect,
                Item.focuseffect, Item.clickeffect, Item.banedmgamt, Item.banedmgbody, Item.banedmgrace,
                Item.banedmgraceamt, Item.elemdmgamt, Item.elemdmgtype, Item.clicklevel2, Item.proclevel2,
                Item.backstabdmg, Item.bardeffect]
    if tooltip:
        arg_list.append(Item.classes)
        arg_list.append(Item.slots)
        arg_list.append(Item.itemtype)
        arg_list.append(Item.proceffect)
        arg_list.append(Item.worneffect)
        arg_list.append(Item.augslot1type)
        arg_list.append(Item.augslot2type)
        arg_list.append(Item.augslot3type)
        arg_list.append(Item.augslot4type)
        arg_list.append(Item.augslot5type)
    else:
        arg_list.append(FocusSpell.id.label('focus_id'))
        arg_list.append(FocusSpell.name.label('focus_spell_name'))
        arg_list.append(FocusSpell.effect_base_value1.label('focus_min_val'))
        arg_list.append(FocusSpell.effect_limit_value1.label('focus_max_val'))
        arg_list.append(ClickSpell.id.label('click_id'))
        arg_list.append(ClickSpell.name.label('click_name'))
        arg_list.append(ProcSpell.id.label('proc_id'))
        arg_list.append(ProcSpell.name.label('proc_name'))
        arg_list.append(WornSpell.name.label('worn_name'))
        arg_list.append(WornSpell.effect_base_value1.label('worn_value'))
        arg_list.append(BardSpell.name.label('inst_name'))
        arg_list.append(BardSpell.effect_base_value1.label('inst_value'))

    return arg_list


def get_item_data(item_id):
    """Returns the basic data for an item, used for tooltips."""

    with Session(bind=engine) as session:
        # Get the item
        args = _get_arg_list(tooltip=True)
        query = session.query(*args).filter(Item.id == item_id)
        result = query.all()
        ret_dict = dict(result[0]._mapping)

        proc = ret_dict['proceffect']
        click = ret_dict['clickeffect']
        focus = ret_dict['focuseffect']
        worn = ret_dict['worneffect']
        inst = ret_dict['bardeffect']
        banebody = ret_dict['banedmgbody']
        banerace = ret_dict['banedmgrace']
        elemtype = ret_dict['elemdmgtype']
        aug_slot_1 = ret_dict['augslot1type']
        aug_slot_2 = ret_dict['augslot2type']
        aug_slot_3 = ret_dict['augslot3type']
        aug_slot_4 = ret_dict['augslot4type']
        aug_slot_5 = ret_dict['augslot5type']

        if worn > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == worn)
            result = query.all()
            ret_dict['worn_name'] = result[0][0]
        if proc > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == proc)
            result = query.all()
            ret_dict['proc_name'] = result[0][0]
        if click > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == click)
            result = query.all()
            ret_dict['click_name'] = utils.check_sympathetic(result[0][0])
        if focus > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == focus)
            result = query.all()
            ret_dict['focus_name'] = result[0][0]
        if inst > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == inst)
            result = query.all()
            ret_dict['inst_name'] = result[0][0]
        if banebody > 0:
            ret_dict['bane_body_name'] = utils.get_bane_dmg_body(banebody)
            ret_dict['bane_body_amount'] = ret_dict['banedmgamt']
        if banerace > 0:
            ret_dict['bane_race_name'] = utils.get_bane_dmg_race(banerace)
            ret_dict['bane_race_amount'] = ret_dict['banedmgraceamt']
        if elemtype > 0:
            ret_dict['elem_dmg_name'] = utils.get_elem_dmg_type(elemtype)
            ret_dict['elem_dmg_amount'] = ret_dict['elemdmgamt']
        if aug_slot_1 > 0:
            ret_dict['aug_slot_1'] = utils.get_aug_type(aug_slot_1)
        if aug_slot_2 > 0:
            ret_dict['aug_slot_2'] = utils.get_aug_type(aug_slot_2)
        if aug_slot_3 > 0:
            ret_dict['aug_slot_3'] = utils.get_aug_type(aug_slot_3)
        if aug_slot_4 > 0:
            ret_dict['aug_slot_4'] = utils.get_aug_type(aug_slot_4)
        if aug_slot_5 > 0:
            ret_dict['aug_slot_5'] = utils.get_aug_type(aug_slot_5)

    ret_dict['class_str'] = utils.get_class_string(ret_dict['classes'])
    ret_dict['slot_str'] = utils.get_slot_string(ret_dict['slots'])
    ret_dict['type_str'] = utils.get_type_string(ret_dict['itemtype'])
    return ret_dict


def get_era_items(kwargs):
    """Returns all base items with NPC names and IDs, as well as Tradeskill and Quest items."""
    # We need to link through to all the NPCs in all the zones of the era to get all the items they drop.
    zone_or_filters = []
    quest_item_ids = []
    special_item_ids = []
    for era in kwargs['eras']:
        zone_id_list = utils.get_era_zones(era)
        for zone_id in zone_id_list:
            zone_or_filters.append(NPCTypes.id.like(f'{zone_id}___'))
        # Now, we need to get the quest items.  These are stored in files
        with open(os.path.join(here, 'item_files', f'{era}.txt'), 'r') as fh:
            file_data = fh.read()
        quest_item_ids += file_data.split('\n')

        if era == 'Kunark':
            # Add LoY
            if os.path.exists(os.path.join(here, f'item_files/LoY.txt')):
                with open(os.path.join(here, 'item_files', f'LoY.txt'), 'r') as fh:
                    file_data = fh.read()
                quest_item_ids += file_data.split('\n')
            if os.path.exists(os.path.join(here, f'item_files/LoY_ts.txt')):
                with open(os.path.join(here, f'item_files/LoY_ts.txt'), 'r') as fh:
                    file_data = fh.read()
                special_item_ids += file_data.split('\n')

        # Certain expansions have tradeskill items at the highest level, add those
        if os.path.exists(os.path.join(here, f'item_files/{era}_ts.txt')):
            with open(os.path.join(here, f'item_files/{era}_ts.txt'), 'r') as fh:
                file_data = fh.read()
            special_item_ids += file_data.split('\n')

        if os.path.exists(os.path.join(here, f'item_files/{era}_special.txt')):
            with open(os.path.join(here, f'item_files/{era}_special.txt'), 'r') as fh:
                file_data = fh.read()
            special_item_ids += file_data.split('\n')

    filters = []
    class_or_filters = []
    weapon_or_filters = []
    aug_search = False
    no_rent = False
    # Now, add the filters that can be applied at all levels to save time.
    if 'item_name' in kwargs:
        partial = "%%%s%%" % (kwargs['item_name'])
        filters.append(Item.Name.like(partial))
    if 'g_class_1' in kwargs:
        class_value = utils.lookup_class(kwargs['g_class_1'])
        class_or_filters.append(Item.classes.op('&')(class_value) == class_value)
    if 'g_class_2' in kwargs:
        class_value = utils.lookup_class(kwargs['g_class_2'])
        class_or_filters.append(Item.classes.op('&')(class_value) == class_value)
    if 'g_class_3' in kwargs:
        class_value = utils.lookup_class(kwargs['g_class_3'])
        class_or_filters.append(Item.classes.op('&')(class_value) == class_value)
    if 'g_slot' in kwargs:
        slot_value = utils.lookup_slot(kwargs['g_slot'])
        filters.append(Item.slots.op('&')(slot_value) == slot_value)
    if 'i_type' in kwargs:
        if kwargs['i_type'] == 'Any':
            pass
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
    if 'no_rent' in kwargs:
        no_rent = True

    # Apply universal filters
    if aug_search:
        filters.append(Item.augtype > 0)

    if not no_rent:
        filters.append(Item.norent == 1)

    # Run the base query to get item IDs for the
    zone_or_params = or_(*zone_or_filters)
    link_filters = _get_link_filters()
    link_params = and_(*link_filters)
    params = and_(*filters)
    class_or_params = or_(*class_or_filters)
    weapon_or_params = or_(*weapon_or_filters)

    base_items = []
    with Session(bind=engine) as session:
        query = session.query(Item.id, NPCTypes.id.label('npc_id'), NPCTypes.name.label('npc_name')).\
            filter(zone_or_params).\
            filter(link_params).\
            filter(params).\
            filter(class_or_params).\
            filter(weapon_or_params).\
            group_by(Item.id)
        result = query.all()

    for entry in result:
        new_item = dict(entry._mapping)
        new_item['id'] = new_item['id'] + 2000000
        base_items.append(new_item)

    quest_items = []
    item_id_filters = []
    for entry in quest_item_ids:
        item_id_filters.append(Item.id == entry)
    item_id_params = or_(*item_id_filters)
    with Session(bind=engine) as session:
        query = session.query(Item.id).\
            filter(item_id_params).\
            filter(params).\
            filter(class_or_params).\
            filter(weapon_or_params).\
            group_by(Item.id)
        result = query.all()
    for entry in result:
        quest_items.append({'id': entry[0], 'npc_id': -1, 'npc_name': 'Quested'})

    special_items = []
    item_id_filters = []
    for entry in special_item_ids:
        item_id_filters.append(Item.id == entry)
    item_id_params = or_(*item_id_filters)
    with Session(bind=engine) as session:
        query = session.query(Item.id).\
            filter(item_id_params).\
            filter(params).\
            filter(class_or_params).\
            filter(weapon_or_params).\
            group_by(Item.id)
        result = query.all()
    for entry in result:
        special_items.append({'id': entry[0], 'npc_id': -2, 'npc_name': 'Tradeskills'})
    return base_items, special_items, quest_items


def create_lookup_table(base_items, tradeskill_items, quest_items):
    """Returns item id filters and an associated lookup table."""
    lookup = {}
    item_ids = []
    for entry in base_items + tradeskill_items + quest_items:
        item_ids.append(Item.id == entry['id'])
        lookup.update({entry['id']: {'npc_id': entry['npc_id'], 'npc_name': entry['npc_name']}})
    return item_ids, lookup


def get_items_with_filters(weights, ignore_zero, **kwargs):
    """Returns all items with filters provided"""
    # Get the base items, tradeskill items, and quest items that drop from the zones in the eras requested.
    base_items, tradeskill_items, quest_items = get_era_items(kwargs)

    # Create the lookup table
    item_ids, lookup_table = create_lookup_table(base_items, tradeskill_items, quest_items)

    # Set up basic database filters
    filters = []
    focus_or_filters = []

    skip_filters = ['item_name', 'g_class_1', 'g_class_2', 'g_class_3', 'g_slot', 'i_type', 'no_rent', 'sub_type',
                    'sympathetic', 'eras']
    bane_body = False
    for entry in kwargs:
        if entry in skip_filters:
            continue
        elif entry == 'proc':
            filters.append(Item.proceffect >= 1)
        elif 'proclevel2' in entry:
            filters.append(Item.proclevel2 <= kwargs['proclevel2'])
        elif entry == 'click':
            filters.append(Item.clickeffect >= 1)
        elif 'clicklevel2' in entry:
            filters.append(Item.clicklevel2 <= kwargs['clicklevel2'])
        elif 'elemdmgtype' in entry:
            filters.append(Item.elemdmgtype == kwargs['elemdmgtype'])
        elif 'banedmgbody' in entry:
            bane_body = True
            filters.append(Item.banedmgbody == kwargs['banedmgbody'])
        elif 'banedmgrace' in entry:
            bane_body = False
            filters.append(Item.banedmgrace == kwargs['banedmgrace'])
        elif 'focus_type' in entry:
            ids = utils.get_focus_values(kwargs['focus_type'], kwargs['sub_type'], engine, SpellsNewReference)
            for focus_id in ids:
                focus_or_filters.append(Item.focuseffect == focus_id)
            if kwargs['focus_type'] == 'Melee':
                for worn_id in ids:
                    focus_or_filters.append(Item.worneffect == worn_id)
            if kwargs['focus_type'] == 'Bard':
                for bard_id in ids:
                    focus_or_filters.append(Item.bardeffect == bard_id)
        else:
            filters.append(getattr(Item, entry) >= kwargs[entry])

    # Filters are set, run them!
    and_params = and_(*filters)
    focus_or_params = or_(*focus_or_filters)
    item_params = or_(*item_ids)

    arg_list = _get_arg_list()

    # BEHOLD, THE QUERY
    with Session(bind=engine) as session:
        query = session.query(*arg_list). \
            join(FocusSpell, FocusSpell.id == Item.focuseffect, isouter=True). \
            join(ClickSpell, ClickSpell.id == Item.clickeffect, isouter=True). \
            join(ProcSpell, ProcSpell.id == Item.proceffect, isouter=True). \
            join(WornSpell, WornSpell.id == Item.worneffect, isouter=True). \
            join(BardSpell, BardSpell.id == Item.bardeffect, isouter=True). \
            filter(Item.id.in_(session.query(Item.id).filter(item_params))). \
            filter(and_params). \
            filter(focus_or_params). \
            group_by(Item.id)
        all_items = query.all()

    out_items = []
    # If we don't have any items, that's it, return early.
    if not lookup_table:
        return out_items
    for entry in all_items:
        entry = utils.ReducedItem((dict(entry._mapping)))
        entry.npc_id = lookup_table[entry.id]['npc_id']
        entry.npc_name = lookup_table[entry.id]['npc_name']
        entry.focus_type = kwargs.get('focus_type')
        entry.sub_focus = kwargs.get('sub_type')

        if weights:
            entry.weight = utils.get_stat_weights(weights, entry, bane_body=bane_body)
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
        entry.zone_name = utils.lookup_zone_name(entry.npc_id)
        entry.npc_name = utils.fix_npc_name(entry.npc_name)
        out_items.append(entry)

    out_items.sort(key=operator.attrgetter('weight'), reverse=True)
    return out_items
