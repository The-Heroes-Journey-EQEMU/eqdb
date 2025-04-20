"""EQDB Logic File"""
import configparser
import datetime
import operator
import os
import random

import utils

from sqlalchemy import create_engine, and_, or_, Column, Integer
from sqlalchemy.orm import Session, aliased
from sqlalchemy.ext.automap import automap_base

here = os.path.dirname(__file__)
site_config = configparser.RawConfigParser()
ini_path = os.path.join(here, 'configuration.ini')
site_config.read_file(open(ini_path))
expansion = site_config.getint('thj', 'expansion')

driver = site_config.get('database', 'driver')
user = site_config.get('database', 'user')
password = site_config.get('database', 'password')
database = site_config.get('database', 'database')
host = site_config.get('database', 'host')
port = site_config.get('database', 'port')

engine = create_engine(f'{driver}{user}:{password}@{host}:{port}/{database}')
local_database = site_config.get('local_database', 'connection')
local_engine = create_engine(local_database)

Base = automap_base()
LocalBase = automap_base()


class ItemRedirection(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)


Base.prepare(autoload_with=engine)
LocalBase.prepare(autoload_with=local_engine)

Zone = Base.classes.zone
ZonePoints = Base.classes.zone_points
Item = ItemRedirection
Spawn2 = Base.classes.spawn2
SpawnEntry = Base.classes.spawnentry
SpawnGroup = Base.classes.spawngroup
NPCTypes = Base.classes.npc_types
NPCSpells = Base.classes.npc_spells
NPCSpellsEntries = Base.classes.npc_spells_entries
MerchantList = Base.classes.merchantlist
LootTableEntries = Base.classes.loottable_entries
LootDropEntries = Base.classes.lootdrop_entries
LootDrop = Base.classes.lootdrop
SpellsNewReference = Base.classes.spells_new_reference
SpellsNew = Base.classes.spells_new
FocusSpell = aliased(SpellsNewReference)
FocusSpellNew = aliased(SpellsNew)
ClickSpell = aliased(SpellsNewReference)
ClickSpellNew = aliased(SpellsNew)
ProcSpell = aliased(SpellsNewReference)
ProcSpellNew = aliased(SpellsNew)
WornSpell = aliased(SpellsNewReference)
WornSpellNew = aliased(SpellsNew)
BardSpell = aliased(SpellsNewReference)
BardSpellNew = aliased(SpellsNew)
Forage = Base.classes.forage
GroundSpawns = Base.classes.ground_spawns
TradeskillRecipe = Base.classes.tradeskill_recipe
TradeskillRecipeEntries = Base.classes.tradeskill_recipe_entries


IdentifiedItems = LocalBase.classes.identified_items
IDEntry = LocalBase.classes.id_entry
Contributor = LocalBase.classes.contributor

# Important that this goes here
import spell


def _debugger():
    return spell.get_spell_data(6561, engine)


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
                Item.backstabdmg, Item.bardeffect, Item.worneffect, Item.procrate, Item.lore, Item.bagtype,
                Item.bagslots, Item.bagwr, Item.bagsize, Item.skillmodvalue, Item.skillmodmax, Item.skillmodtype]
    if tooltip:
        arg_list.append(Item.classes)
        arg_list.append(Item.slots)
        arg_list.append(Item.itemtype)
        arg_list.append(Item.proceffect)
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
        arg_list.append(WornSpell.id.label('worn_id'))
        arg_list.append(WornSpell.name.label('worn_name'))
        arg_list.append(WornSpell.effect_base_value1.label('worn_value'))
        arg_list.append(BardSpell.id.label('inst_id'))
        arg_list.append(BardSpell.name.label('inst_name'))
        arg_list.append(BardSpell.effect_base_value1.label('inst_value'))

    return arg_list


def get_leaderboard():
    """Gets the data identification leaderboard"""
    # Get all contributors
    with Session(bind=local_engine) as session:
        query = session.query(Contributor)
        result = query.all()

    contributors = []
    for entry in result:
        entry = entry.__dict__
        contributor = {'contributor': entry['name'], 'contributed': entry['contributed']}
        with Session(bind=local_engine) as session:
            query = session.query(IDEntry).filter(IDEntry.cid == entry['id'])
            result = query.all()
        contributor.update({'identifications': len(result)})
        contributors.append(contributor)

    return contributors


def get_tradeskills(name=None, trivial=None, tradeskill=None):
    filters = []
    if name:
        partial = "%%%s%%" % name
        filters.append(TradeskillRecipe.name.like(partial))
    if trivial:
        filters.append(TradeskillRecipe.trivial <= int(trivial))
    if tradeskill:
        filters.append(TradeskillRecipe.tradeskill == tradeskill)

    params = and_(*filters)
    with Session(bind=engine) as session:
        query = session.query(TradeskillRecipe.id, TradeskillRecipe.name, TradeskillRecipe.trivial).filter(params)
        result = query.all()

    out_data = []
    for entry in result:
        out_data.append({'ts_id': entry[0],
                         'ts_name': entry[1],
                         'trivial': entry[2]})
    return out_data


def get_tradeskill_detail(ts_id):
    # Get the tradeskill base details
    base_data = {}
    with Session(bind=engine) as session:
        args = [TradeskillRecipe.name, TradeskillRecipe.tradeskill, TradeskillRecipe.skillneeded,
                TradeskillRecipe.trivial, TradeskillRecipe.nofail, TradeskillRecipe.replace_container,
                TradeskillRecipe.must_learn, TradeskillRecipe.enabled, TradeskillRecipe.min_expansion]
        query = session.query(*args).filter(TradeskillRecipe.id == ts_id)
        result = query.one()

    base_data.update({'name': result[0],
                      'skill': utils.parse_skill(result[1]),
                      'required': result[2],
                      'trivial': result[3],
                      'no_fail': result[4],
                      'replace_container': result[5],
                      'must_learn': result[6],
                      'enabled': result[7],
                      'min_expansion': result[8],
                      'expansion': expansion})

    # Get the items involved in making the recipe
    with Session(bind=engine) as session:
        args = [TradeskillRecipeEntries.item_id, Item.Name, TradeskillRecipeEntries.successcount,
                TradeskillRecipeEntries.failcount, TradeskillRecipeEntries.componentcount]
        query = session.query(*args).filter(TradeskillRecipeEntries.recipe_id == ts_id).\
            filter(TradeskillRecipeEntries.iscontainer <= 0).\
            filter(TradeskillRecipeEntries.item_id == Item.id)
        result = query.all()

    components = []
    success = []
    fail = []
    for entry in result:
        item_id = entry[0]
        item_name = entry[1]
        successcount = entry[2]
        failcount = entry[3]
        componentcount = entry[4]

        if successcount > 0:
            success.append({'item_id': item_id,
                            'item_name': item_name,
                            'count': successcount})
        if failcount > 0:
            fail.append({'item_id': item_id,
                         'item_name': item_name,
                         'count': failcount})
        if componentcount > 0:
            components.append({'item_id': item_id,
                               'item_name': item_name,
                               'count': componentcount})
    base_data.update({'components': components,
                      'success': success,
                      'fail': fail})

    # Get the containers
    containers = []
    with Session(bind=engine) as session:
        query = session.query(TradeskillRecipeEntries.item_id, TradeskillRecipeEntries.iscontainer).\
            filter(TradeskillRecipeEntries.recipe_id == ts_id).\
            filter(TradeskillRecipeEntries.iscontainer >= 1)
        result = query.all()

    for entry in result:
        try:
            containers.append({'container_type': utils.get_object_type(entry[0])})
        except NotImplementedError:
            with Session(bind=engine) as session:
                query = session.query(Item.Name).filter(Item.id == entry[0])
                sub_result = query.one()
            containers.append({'container_type': sub_result[0]})
    base_data.update({'containers': containers})

    return base_data


def get_npc_raw_data(npc_id):
    with Session(bind=engine) as session:
        query = session.query(NPCTypes).filter(NPCTypes.id == npc_id)
        result = query.one()

    ret_dict = result.__dict__
    ret_dict.pop('_sa_instance_state')
    return ret_dict


def get_npc_detail(npc_id):
    # Get basic npc details:
    with Session(bind=engine) as session:
        query = session.query(NPCTypes).filter(NPCTypes.id == npc_id)
        result = query.one()
    base_data = result.__dict__
    base_data.pop('_sa_instance_state')

    # Update certain things
    base_data['bodytype'] = utils.get_bane_dmg_body(base_data['bodytype'])
    base_data['name'] = utils.fix_npc_name(base_data['name'])
    base_data['class'] = utils.get_class_string(base_data['class'])
    base_data['race'] = utils.get_bane_dmg_race(base_data['race'])

    # Convert special abilities to make sense
    specials = []
    spc = result.npcspecialattks
    if 'E' in spc:
        specials.append('Enrages')
    if 'F' in spc:
        specials.append('Flurries')
    if 'R' in spc:
        specials.append('Rampages')
    if 'r' in spc:
        specials.append('Wild Rampages')
    if 'S' in spc:
        specials.append('Summons')
    if 'T' in spc:
        specials.append('Triple Attacks')
    if 'Q' in spc:
        specials.append('Quad Attacks')
    if 'b' in spc:
        specials.append('Bane Attacks')
    if 'm' in spc:
        specials.append('Magical Attacks')
    if 'U' in spc:
        specials.append('Immune to Slow')
    if 'C' in spc:
        specials.append('Immune to Charm')
    if 'N' in spc:
        specials.append('Immune to Stuns')
    if 'I' in spc:
        specials.append('Immune to Snare')
    if 'D' in spc:
        specials.append('Immune to Slow')
    if 'K' in spc:
        specials.append('Immune to Dispel Magic')
    if 'A' in spc:
        specials.append('Immune to Melee')
    if 'B' in spc:
        specials.append('Immune to Magic')
    if 'f' in spc:
        specials.append('Will not flee')
    if 'O' in spc:
        specials.append('Immune to non-bane Melee')
    if 'W' in spc:
        specials.append('Immune to non-magical Melee')
    if 'G' in spc:
        specials.append('Cannot be agroed')
    if 'g' in spc:
        specials.append('Belly Caster')
    if 'd' in spc:
        specials.append('Ignores Feign Death')
    if 'Y' in spc:
        specials.append('Has a Ranged Attack')
    if 'L' in spc:
        specials.append('Dual Wields')
    if 't' in spc:
        specials.append('Focused Hate')
    if 'n' in spc:
        specials.append('Does not buff/heal friends')
    if 'p' in spc:
        specials.append('Immune to Pacify')
    if 'J' in spc:
        specials.append('Leashed to combat area')
    if 'j' in spc:
        specials.append('Thetered to combat area')
    if 'o' in spc:
        specials.append('Destructible Object')
    if 'Z' in spc:
        specials.append('Immune to player damage')
    if 'i' in spc:
        specials.append('Immune to Taunt')
    if 'e' in spc:
        specials.append('Will always flee')
    if 'h' in spc:
        specials.append('Flee at low percent health')
    base_data.update({'special_attacks': specials})

    # Get the spells this NPC uses
    spells = []
    loot_lists = {}
    spawn_groups = []
    merch = []
    with Session(bind=engine) as session:
        # If this is a merchant, get it's merchant items
        query = session.query(MerchantList.item, Item.Name, MerchantList.min_expansion).\
            filter(MerchantList.merchantid == npc_id).\
            filter(MerchantList.item == Item.id)
        result = query.all()
        for entry in result:
            if int(entry[2]) > expansion:
                continue
            merch.append({'item_id': entry[0],
                          'item_name': entry[1]})
        base_data['merch'] = merch

        # Get proc spell
        query = session.query(NPCSpells.attack_proc, SpellsNewReference.name, NPCSpells.proc_chance).\
            filter(NPCSpells.id == base_data['npc_spells_id']).\
            filter(NPCSpells.attack_proc == SpellsNewReference.id)
        result = query.first()
        if result:
            spells.append({'spell_type': 'proc',
                           'spell_name': result[1],
                           'spell_id': result[0],
                           'proc_chance': result[2]})
        # Get defensive proc spell
        query = session.query(NPCSpells.defensive_proc, SpellsNewReference.name, NPCSpells.dproc_chance).\
            filter(NPCSpells.id == base_data['npc_spells_id']).\
            filter(NPCSpells.defensive_proc == SpellsNewReference.id)
        result = query.first()
        if result:
            spells.append({'spell_type': 'defensive',
                           'spell_name': result[1],
                           'spell_id': result[0],
                           'proc_chance': result[2]})
        # Get ranged proc spell
        query = session.query(NPCSpells.range_proc, SpellsNewReference.name, NPCSpells.rproc_chance).\
            filter(NPCSpells.id == base_data['npc_spells_id']).\
            filter(NPCSpells.range_proc == SpellsNewReference.id)
        result = query.first()
        if result:
            spells.append({'spell_type': 'ranged',
                           'spell_name': result[1],
                           'spell_id': result[0],
                           'proc_chance': result[2]})

        # Get all cast spells
        query = session.query(NPCSpellsEntries.spellid, SpellsNewReference.name).\
            filter(NPCSpellsEntries.npc_spells_id == base_data['npc_spells_id']).\
            filter(NPCSpellsEntries.spellid == SpellsNewReference.id)
        result = query.all()
        for entry in result:
            spells.append({'spell_type': 'cast',
                           'spell_name': entry[1],
                           'spell_id': entry[0],
                           'proc_chance': None})

        # Get the loot lists
        query = session.query(LootTableEntries).\
            filter(LootTableEntries.loottable_id == base_data['loottable_id'])
        result = query.all()
        for entry in result:
            # Get the name
            query = session.query(LootDrop.name).filter(LootDrop.id == entry.lootdrop_id)
            sub_result = query.one()
            loot_list_name = sub_result[0]

            # Get the items
            query = session.query(LootDropEntries.item_id, Item.Name, LootDropEntries.chance).\
                filter(LootDropEntries.lootdrop_id == entry.lootdrop_id).filter(LootDropEntries.item_id == Item.id)
            sub_result = query.all()

            items = []
            for sub_entry in sub_result:
                item = {'item_id': sub_entry[0],
                        'item_name': sub_entry[1],
                        'probability': sub_entry[2]}
                items.append(item)
            loot_lists.update({entry.lootdrop_id: {'name': loot_list_name,
                                                   'items': items,
                                                   'multiplier': entry.multiplier,
                                                   'droplimit': entry.droplimit,
                                                   'mindrop': entry.mindrop,
                                                   'probability': entry.probability}})

        # Get spawn point(s)
        args = [Spawn2.x, Spawn2.y, Spawn2.z, Spawn2.respawntime, SpawnGroup.name, SpawnGroup.id]
        query = session.query(*args).filter(SpawnEntry.npcID == npc_id).\
            filter(SpawnEntry.spawngroupID == Spawn2.spawngroupID).\
            filter(SpawnEntry.spawngroupID == SpawnGroup.id)
        result = query.all()

        for entry in result:
            # Get the other entries on the spawn
            spawn_npcs = []
            query = session.query(SpawnEntry.npcID, NPCTypes.name, SpawnEntry.chance).\
                filter(SpawnEntry.spawngroupID == entry[5]).\
                filter(SpawnEntry.npcID == NPCTypes.id)
            sub_result = query.all()
            for sub_entry in sub_result:
                spawn_npcs.append({'npc_id': sub_entry[0],
                                   'npc_name': sub_entry[1],
                                   'chance': sub_entry[2]})

            spawn_groups.append({'name': entry[4],
                                 'x': int(entry[0]) * -1,
                                 'y': int(entry[1]) * -1,
                                 'z': entry[2],
                                 'respawn': entry[3],
                                 'spawn_npcs': spawn_npcs})

        base_data['spawn_groups'] = spawn_groups
        # Translate the spawn ID into a zone id, then get that name
        zone_id = int(npc_id / 1000)
        if zone_id != 0:
            query = session.query(Zone.long_name, Zone.expansion, Zone.short_name).filter(Zone.zoneidnumber == zone_id)
            result = query.first()
        else:
            result = ['Unknown', 0, 'Unknown']
        base_data['zone_name'] = result[0]
        base_data['zone_id'] = zone_id
        base_data['expansion'] = utils.get_era_name(result[1])
        short_name = result[2]
        base_data['loot_lists'] = loot_lists
        base_data['spells'] = spells
    # Get the mapping
    base_data['mapping'] = utils.get_map_data(short_name)
    return base_data


def get_zone_detail(zone_id):
    # Get some zone details
    with Session(bind=engine) as session:
        args = [Zone.expansion, Zone.short_name, Zone.long_name, Zone.safe_x, Zone.safe_y, Zone.canbind, Zone.canlevitate,
                Zone.castoutdoor]
        query = session.query(*args).filter(Zone.zoneidnumber == zone_id)
        result = query.first()

    base_data = {'expansion': utils.get_era_name(result[0]),
                 'short_name': result[1],
                 'long_name': result[2],
                 'safe_x': int(result[3]),
                 'safe_y': int(result[4]),
                 'can_bind': result[5],
                 'can_lev': result[6],
                 'outdoor': result[7]}

    # Get all the zones this zone connects to
    with Session(bind=engine) as session:
        query = session.query(ZonePoints.target_zone_id).distinct().filter(ZonePoints.zone == base_data['short_name'])
        result = query.all()

        if result:
            target_zone_ids = []
            for entry in result:
                target_zone_ids.append(Zone.zoneidnumber == entry[0])

            target_zone_params = or_(*target_zone_ids)
            query = session.query(Zone.zoneidnumber, Zone.long_name, Zone.expansion).filter(target_zone_params)
            result = query.all()
        else:
            result = []

    linked_zone_data = {}
    for entry in result:
        if int(entry[2]) > expansion:
            continue
        linked_zone_data.update({entry[0]: entry[1]})
    base_data.update({'linked_zones': linked_zone_data})

    # Get all the items that drop in this zone.
    known_ids = []
    link_filters = _get_link_filters()
    link_params = and_(*link_filters)
    with Session(bind=engine) as session:
        query = session.query(Item.id, Item.Name).filter(NPCTypes.id.like(f'{zone_id}___')).filter(link_params)
        result = query.all()
    out_items = []
    for entry in result:
        if entry[0] not in known_ids:
            known_ids.append(entry[0])
            out_items.append({'item_id': entry[0],
                              'item_name': entry[1]})
    base_data.update({'dropped_items': out_items})

    # Parse the map files and add them to the returned data.
    short_name = base_data['short_name']
    base_data.update({'mapping': utils.get_map_data(short_name)})

    # Get all the NPCs for this zone
    spawn_groups = {}
    with Session(bind=engine) as session:
        query = session.query(Spawn2.x, Spawn2.y, Spawn2.z, Spawn2.respawntime, SpawnGroup.name, NPCTypes.name, NPCTypes.id, SpawnEntry.chance).\
            filter(Spawn2.spawngroupID == SpawnGroup.id).\
            filter(SpawnEntry.spawngroupID == Spawn2.spawngroupID).\
            filter(Spawn2.zone == short_name). \
            filter(SpawnEntry.npcID == NPCTypes.id).\
            order_by(Spawn2.spawngroupID)
        result = query.all()
        for entry in result:
            x = entry[0]
            y = entry[1]
            z = entry[2]
            respawn = entry[3]
            name = entry[4]
            npc_name = entry[5]
            npc_id = entry[6]
            chance = entry[7]
            if name in spawn_groups:
                npc_list = spawn_groups[name]['npcs']
            else:
                npc_list = []
            if {'npc_name': npc_name, 'npc_id': npc_id, 'chance': chance} not in npc_list:
                npc_list.append({'npc_name': npc_name,
                                 'npc_id': npc_id,
                                 'chance': chance})
            spawn_groups.update({name: {'x': x,
                                        'y': y,
                                        'z': z,
                                        'respawn': respawn,
                                        'npcs': npc_list}})
    base_data['spawn_groups'] = spawn_groups

    return base_data


def get_zone_listing():
    era_list = {'Classic': 0, 'Ruins of Kunark': 1, 'Legacy of Ykesha': 5, 'Scars of Velious': 2, 'Shadows of Luclin': 3,
                'Planes of Power': 4, 'Lost Dungeons of Norrath': 6, 'Gates of Discord': 7}
    out_list = {}
    exclusion_list = ['cshome', 'hateplane', 'powar', 'soldungc', 'qvicb']
    # Massaging
    massage_list = {'nedaria': 7, 'bazaar': 3}
    add_to_later = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}, 5: {}, 6: {}, 7: {}}
    for era in era_list:
        with Session(bind=engine) as session:
            query = session.query(Zone.zoneidnumber, Zone.short_name, Zone.long_name, Zone.zone_exp_multiplier). \
                filter(Zone.expansion == era_list[era])
            result = query.all()
        era_zones = {}
        for entry in result:
            id_num = entry[0]
            short_name = entry[1]
            long_name = entry[2]
            zem = entry[3]
            if short_name in exclusion_list:
                continue
            if short_name in massage_list.keys() and massage_list[short_name] != era_list[era]:
                add_to_later.update({massage_list[short_name]: {long_name: {'id': id_num,
                                                                            'short_name': short_name,
                                                                            'zem': zem}}})
                continue

            era_zones.update({long_name: {'id': id_num,
                                          'short_name': short_name,
                                          'zem': zem}})
        for entry in add_to_later[era_list[era]]:
            era_zones.update({entry: add_to_later[era_list[era]][entry]})
        out_list.update({era: era_zones})
    return out_list


def get_zone_long_name(zone_short_name):
    with Session(bind=engine) as session:
        query = session.query(Zone.zoneidnumber, Zone.long_name).filter(Zone.short_name == zone_short_name)
        result = query.one()
    return result[0], result[1]


def get_item_raw_data(item_id):
    with Session(bind=engine) as session:
        query = session.query(Item).filter(Item.id == item_id)
        result = query.one()

    ret_dict = result.__dict__
    ret_dict.pop('_sa_instance_state')
    return ret_dict


def get_npcs(npc_name):
    npc_name = npc_name.replace(' ', '_')
    partial = "%%%s%%" % npc_name
    with Session(bind=engine) as session:
        query = session.query(NPCTypes.id, NPCTypes.name).\
            filter(NPCTypes.name.like(partial)).limit(50)
        result = query.all()

    out_data = []
    for entry in result:
        npc_id = entry[0]
        npc_name = entry[1]
        zone_id = int(npc_id/1000)
        with Session(bind=engine) as session:
            query = session.query(Zone.long_name, Zone.expansion).filter(Zone.zoneidnumber == zone_id)
            sub_result = query.first()

        if int(sub_result[1]) > expansion:
            continue

        if not sub_result:
            sub_result = ['Unknown']
        out_data.append({'npc_id': npc_id,
                         'name': utils.fix_npc_name(npc_name),
                         'zone': sub_result[0]})
    return out_data


def get_spell_raw_data(spell_id):
    with Session(bind=engine) as session:
        query = session.query(SpellsNewReference).filter(SpellsNewReference.id == spell_id)
        result = query.first()

    if not result:
        with Session(bind=engine) as session:
            query = session.query(SpellsNew).filter(SpellsNew.id == spell_id)
            result = query.first()

    ret_dict = result.__dict__
    ret_dict.pop('_sa_instance_state')
    return ret_dict


def get_spells(spell_name):
    partial = "%%%s%%" % spell_name
    with Session(bind=engine) as session:
        query = session.query(SpellsNewReference.id, SpellsNewReference.name).\
            filter(SpellsNewReference.name.like(partial)).limit(50)
        result = query.all()

    with Session(bind=engine) as session:
        query = session.query(SpellsNew.id, SpellsNew.name).filter(SpellsNew.name.like(partial)).limit(50)
        result2 = query.all()

    out_data = []
    for entry in result + result2:
        spell_id = entry[0]
        name = entry[1]
        out_data.append({'spell_id': spell_id,
                         'name': name})
    return out_data


def get_fast_item(item_name, tradeskill=None, equippable=None, itype='Base', no_glamours=False, only_aug=False):
    filters = []
    or_filters = []
    if len(item_name) > 0:
        partial = "%%%s%%" % item_name
        filters.append(Item.Name.like(partial))
    if tradeskill:
        filters.append(Item.tradeskills == 1)
        equippable = None
        itype = 'Base'
        no_glamours = True
        only_aug = False
    if equippable:
        or_filters = [Item.itemtype == 0, Item.itemtype == 1, Item.itemtype == 2, Item.itemtype == 3,
                      Item.itemtype == 4, Item.itemtype == 5, Item.itemtype == 7, Item.itemtype == 8,
                      Item.itemtype == 10, Item.itemtype == 19, Item.itemtype == 23, Item.itemtype == 24,
                      Item.itemtype == 25, Item.itemtype == 26, Item.itemtype == 27, Item.itemtype == 29,
                      Item.itemtype == 35, Item.itemtype == 54, Item.itemtype == 52]
    if itype == 'Base':
        filters.append(Item.id < 1000000)
    if itype == 'Enchanted':
        filters.append(Item.id > 1000000)
        filters.append(Item.id < 2000000)
    if itype == 'Legendary':
        filters.append(Item.id > 2000000)
    if only_aug:
        filters.append(Item.augtype > 0)

    params = and_(*filters)
    with Session(bind=engine) as session:
        if or_filters:
            or_params = or_(*or_filters)
            query = session.query(Item.id, Item.Name).filter(params).filter(or_params).limit(50)
        else:
            query = session.query(Item.id, Item.Name).filter(params).limit(50)
        result = query.all()

    out_data = []
    for entry in result:
        item_id = entry[0]
        name = entry[1]
        if no_glamours and 'glamour' in name.lower():
            continue
        out_data.append({'item_id': item_id,
                         'name': name})
    return out_data


def get_spell_data(spell_id):
    spell_data, slots = spell.get_spell_data(spell_id, engine)

    procs = []
    clicks = []
    focus = []
    worn = []
    bard = []

    with Session(bind=engine) as session:
        # Find all the items that have this as a proc
        query = session.query(Item.id, Item.Name).filter(Item.proceffect == spell_id)
        result = query.all()
        for entry in result:
            item_id = entry[0]
            item_name = entry[1]
            procs.append({'item_id': item_id,
                          'item_name': item_name})

        # Find all the items that have this as a click effect
        query = session.query(Item.id, Item.Name).filter(Item.clickeffect == spell_id)
        result = query.all()
        for entry in result:
            item_id = entry[0]
            item_name = entry[1]
            clicks.append({'item_id': item_id,
                          'item_name': item_name})

        # Find all the items that have this as a focus effect
        query = session.query(Item.id, Item.Name).filter(Item.focuseffect == spell_id)
        result = query.all()
        for entry in result:
            item_id = entry[0]
            item_name = entry[1]
            focus.append({'item_id': item_id,
                          'item_name': item_name})

        # Find all the items that have this as a worn effect
        query = session.query(Item.id, Item.Name).filter(Item.worneffect == spell_id)
        result = query.all()
        for entry in result:
            item_id = entry[0]
            item_name = entry[1]
            worn.append({'item_id': item_id,
                          'item_name': item_name})

        # Find all the items that have this as a bard effect
        query = session.query(Item.id, Item.Name).filter(Item.bardeffect == spell_id)
        result = query.all()
        for entry in result:
            item_id = entry[0]
            item_name = entry[1]
            bard.append({'item_id': item_id,
                          'item_name': item_name})

    spell_data.update({'procs': procs,
                       'clicks': clicks,
                       'focus': focus,
                       'worn': worn,
                       'bard': bard})

    return spell_data, slots


def get_spell_tooltip(spell_id):
    return spell.get_spell_data(spell_id, engine, basic_data=False)


def add_item_identification(data, user=None):
    """Adds an item identification to the database, and does the necessary followup."""
    item_id = data.get('item_id')
    expansion = data.get('expansion')
    source = data.get('source')
    zone_id = data.get('zone_id')

    if user:
        user_id = user.id
        user_name = user.name
    else:
        user_id = -1
        user_name = 'Anonymous'

    # Does this user already exist in the local db
    with Session(bind=local_engine) as session:
        query = session.query(Contributor).filter(Contributor.id == user_id)
        result = query.all()

    if not result:
        # Add the contributor
        with Session(bind=local_engine) as session:
            new_contrib = Contributor(name=user_name,
                                      id=user_id,
                                      contributed=1)
            session.add(new_contrib)
            session.commit()
            contrib = {'name': user_name, 'id': user_id, 'contributed': 1}
    else:
        contrib = result[0].__dict__

    # Does this item have existing identifications
    with Session(bind=local_engine) as session:
        args = [IDEntry.expansion, IDEntry.source, IDEntry.item_id, Contributor.contributed, Contributor.id]
        query = session.query(*args).filter(IDEntry.item_id == item_id).filter(IDEntry.cid == Contributor.id)
        result = query.all()

    existing_entries = result

    # Create the data matrix
    idents = [{'expansion': expansion, 'source': source, 'zone': zone_id}]
    ident_amt = [contrib.get('contributed')]
    for entry in result:
        entry = entry._mapping
        test_key = {'expansion': entry.get('expansion'), 'source': entry.get('source'), 'zone': entry.get('zone_id')}
        if test_key in idents:
            idx = idents.index(test_key)
            new_val = ident_amt[idx] + entry.get('contributed')
            ident_amt[idx] = new_val
        else:
            idents.append(test_key)
            ident_amt.append(entry.get('contributed'))

    # Check if we now have an identification:
    identification = None
    for entry in ident_amt:
        if entry >= 100:
            idx = ident_amt.index(entry)
            identification = idents[idx]
            break

    if identification is not None:
        # Update all the contributors contributions
        with Session(bind=local_engine) as session:
            for entry in existing_entries:
                if entry.id == -1:
                    continue
                obj = session.query(Contributor).filter(Contributor.id == entry.get('id'))
                obj.update({'contributed': entry.get('contributed') + 1})
                session.commit()
            if user_id != -1:
                obj = session.query(Contributor).filter(Contributor.id == user_id)
                obj.update({'contributed': contrib.get('contributed') + 1})
                session.commit()
                contrib['contributed'] += 1

        # Add this item to identified items.
        with Session(bind=local_engine) as session:
            new_item = IdentifiedItems(item_id=item_id,
                                       expansion=identification.get('expansion'),
                                       source=identification.get('source'),
                                       zone_id=identification.get('zone_id'))
            session.add(new_item)
            session.commit()

        # Remove the item from existing identifications
        with Session(bind=local_engine) as session:
            for entry in existing_entries:
                obj = IDEntry.query.filter_by(item_id == entry.get('item_id'))
                session.delete(obj)
                session.commit()

        # Report back
        ret_dict = {'item_id': item_id,
                    'result': True,
                    'expansion': expansion,
                    'source': source}
    else:
        # Add this to Idents
        with Session(bind=local_engine) as session:
            new_entry = IDEntry(item_id=item_id,
                                cid=contrib.get('id'),
                                expansion=expansion,
                                source=source,
                                zone_id=zone_id)
            session.add(new_entry)
            session.commit()
        ret_dict = {'item_id': item_id,
                    'result': False,
                    'expansion': None,
                    'source': None}
    if user:
        # Get the number of identifications the user has submitted
        with Session(bind=local_engine) as session:
            query = session.query(IDEntry.item_id).filter(IDEntry.cid == user.id)
            result = query.all()

        ret_dict.update({'user_contrib': contrib.get('contributed'),
                         'user_identify': len(result)})
    return ret_dict


def get_unidentified_item(user=None):
    """Returns an unidentified item."""
    if user:
        pick_new = False
        chooser = random.randint(1, 10)
        if chooser == 10:
            pick_new = True
        if not pick_new:
            # Get a partially identified item that the user hasn't weighed in on
            with Session(bind=local_engine) as session:
                query = session.query(IDEntry.item_id).filter(IDEntry.cid == user.id)
                result = query.all()
            exclude_ids = []
            for entry in result:
                exclude_ids.append(IDEntry.item_id != entry[0])
            exclude_params = and_(*exclude_ids)

            with Session(bind=local_engine) as session:
                query = session.query(IDEntry.item_id).filter(exclude_params)
                result = query.all()
            if result:
                choice = random.choice(result)
                return get_item_data(choice[0])

    # Get all the identified items IDs from the local db.
    with Session(bind=local_engine) as session:
        query = session.query(IdentifiedItems.item_id)
        result = query.all()
    ided_items = [item for t in result for item in t]

    # Anything from 1000 to 1000000 is a potentially valid item ID.
    pos_items = list(range(1000, 1000000))

    unid = list(set(pos_items) - set(ided_items))

    while True:
        check_id = random.choice(unid)
        # See if this item ID exists on THJ
        with Session(bind=engine) as session:
            query = session.query(Item.id).filter(Item.id == check_id)
            result = query.all()
        if not result:
            continue
        # We have a valid ID!  Return it!
        return get_item_data(result[0][0])


def get_item_data(item_id, full=False):
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
        skill_mod = ret_dict['skillmodtype']

        if worn > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == worn)
            result = query.all()
            if not result:
                query = session.query(SpellsNew.name).filter(SpellsNew.id == worn)
                result = query.all()
            ret_dict['worn_name'] = result[0][0]
        if proc > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == proc)
            result = query.all()
            if not result:
                query = session.query(SpellsNew.name).filter(SpellsNew.id == proc)
                result = query.all()
            ret_dict['proc_name'] = result[0][0]
        if click > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == click)
            result = query.all()
            if not result:
                query = session.query(SpellsNew.name).filter(SpellsNew.id == click)
                result = query.all()
            ret_dict['click_name'] = utils.check_sympathetic(result[0][0])
        if focus > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == focus)
            result = query.all()
            if not result:
                query = session.query(SpellsNew.name).filter(SpellsNew.id == focus)
                result = query.all()
            ret_dict['focus_name'] = result[0][0]
        if inst > 0:
            query = session.query(SpellsNewReference.name).filter(SpellsNewReference.id == inst)
            result = query.all()
            if not result:
                query = session.query(SpellsNew.name).filter(SpellsNew.id == inst)
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
        if skill_mod > 0:
            ret_dict['skillmodname'] = utils.parse_skill(int(skill_mod))

    ret_dict['class_str'] = utils.get_class_string(ret_dict['classes'])
    ret_dict['slot_str'] = utils.get_slot_string(ret_dict['slots'])
    ret_dict['type_str'] = utils.get_type_string(ret_dict['itemtype'])
    ret_dict['thj_enabled'] = False
    item_id = int(item_id)
    if item_id < 1000000:
        # See if Enchanted and Legendary exist
        with Session(bind=engine) as session:
            ench = item_id + 1000000
            lego = item_id + 2000000
            query = session.query(Item.id).filter(or_(Item.id == ench, Item.id == lego))
            result = query.all()
            if len(result) == 2:
                ret_dict['thj_enabled'] = True
    elif item_id > 1000000:
        ret_dict['thj_enabled'] = True
    if full:
        # Get mobs that drop this as loot
        droppers = []
        if item_id > 2000000:
            item_id = item_id - 2000000
        elif 2000000 > item_id > 1000000:
            item_id = item_id - 1000000
        with Session(bind=engine) as session:
            query = session.query(NPCTypes.id, NPCTypes.name).filter(LootDropEntries.item_id == item_id).\
                filter(LootDropEntries.lootdrop_id == LootTableEntries.lootdrop_id).\
                filter(LootTableEntries.loottable_id == NPCTypes.loottable_id)
            result = query.all()
            for entry in result:
                query = session.query(Zone.long_name).filter(Zone.zoneidnumber == int(entry[0]/1000))
                sub_result = query.one()

                if {'npc_id': entry[0], 'npc_name': utils.fix_npc_name(entry[1]), 'zone_name': sub_result[0]} in droppers:
                    continue
                droppers.append({'npc_id': entry[0],
                                 'npc_name': utils.fix_npc_name(entry[1]),
                                 'zone_name': sub_result[0]})
        ret_dict['droppers'] = droppers

        # Get vendors that sell this
        vendors = []
        with Session(bind=engine) as session:
            query = session.query(NPCTypes.id, NPCTypes.name).filter(MerchantList.item == item_id).\
                filter(MerchantList.merchantid == NPCTypes.id)
            result = query.all()
        for entry in result:
            vendors.append({'npc_id': entry[0],
                            'npc_name': utils.fix_npc_name(entry[1])})
        ret_dict['vendors'] = vendors

        # Get where this is foraged from
        foraged = []
        with Session(bind=engine) as session:
            query = session.query(Zone.zoneidnumber, Zone.long_name, Zone.expansion, Forage.chance).\
                filter(Forage.Itemid == item_id).\
                filter(Zone.zoneidnumber == Forage.zoneid)
            result = query.all()
        for entry in result:
            if int(entry[2]) > expansion:
                continue
            foraged.append({'zone_id': entry[0],
                            'zone_name': entry[1],
                            'chance': entry[3]})
        ret_dict['foraged'] = foraged

        # Get where this is a ground spawn
        ground = []
        with Session(bind=engine) as session:
            query = session.query(Zone.zoneidnumber, Zone.long_name, Zone.expansion,
                                  GroundSpawns.min_x, GroundSpawns.min_y, GroundSpawns.respawn_timer).\
                filter(GroundSpawns.zoneid == Zone.zoneidnumber).\
                filter(GroundSpawns.item == item_id)
            result = query.all()
        for entry in result:
            if int(entry[2]) > expansion:
                continue
            ground.append({'zone_id': entry[0],
                           'zone_name': entry[1],
                           'x': entry[3],
                           'y': entry[4],
                           'respawn': entry[5]})
        ret_dict['ground'] = ground

        # Get where this is made by tradeskills
        ts_result = []
        with Session(bind=engine) as session:
            query = session.query(TradeskillRecipeEntries.recipe_id, TradeskillRecipe.name).\
                filter(TradeskillRecipe.id == TradeskillRecipeEntries.recipe_id).\
                filter(TradeskillRecipeEntries.item_id == item_id). \
                filter(TradeskillRecipeEntries.successcount >= 1)
            result = query.all()

        for entry in result:
            ts_result.append({'ts_id': entry[0],
                              'ts_name': entry[1]})
        ret_dict['ts_result'] = ts_result

        # Get where this item is used in tradeskills
        ts_component = []
        with Session(bind=engine) as session:
            query = session.query(TradeskillRecipeEntries.recipe_id, TradeskillRecipe.name).\
                filter(TradeskillRecipe.id == TradeskillRecipeEntries.recipe_id).\
                filter(TradeskillRecipeEntries.item_id == item_id). \
                filter(TradeskillRecipeEntries.componentcount >= 1)
            result = query.all()

        for entry in result:
            ts_component.append({'ts_id': entry[0],
                              'ts_name': entry[1]})
        ret_dict['ts_component'] = ts_component

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
    if 'pet_search' in kwargs:
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
                    'sympathetic', 'eras', 'w_eff', 'pet_search']
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
        elif 'delay' in entry:
            filters.append(Item.delay <= kwargs['delay'])
        elif 'procrate' in entry:
            filters.append(Item.procrate >= int(kwargs[entry]))
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
    show_worn = False
    show_inst = False
    show_focus = False
    for entry in all_items:
        entry = utils.ReducedItem((dict(entry._mapping)))
        entry.npc_id = lookup_table[entry.id]['npc_id']
        entry.npc_name = lookup_table[entry.id]['npc_name']
        entry.focus_type = kwargs.get('focus_type')
        entry.sub_focus = kwargs.get('sub_type')
        if entry.focuseffect > 0:
            show_focus = True
        if entry.worneffect > 0:
            show_worn = True
        if entry.bardeffect > 0:
            show_inst = True

        if 'pet_search' in kwargs:
            pet_search = True
        else:
            pet_search = False

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
    return out_items, show_focus, show_worn, show_inst
