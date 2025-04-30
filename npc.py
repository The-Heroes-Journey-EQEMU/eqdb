from sqlalchemy.orm import Session

import utils
from logic import engine, NPCTypes, FactionList, NPCFactionEntries, MerchantList, Item, expansion, NPCSpells, \
    SpellsNewReference, NPCSpellsEntries, LootTableEntries, LootDrop, LootDropEntries, Spawn2, SpawnEntry, SpawnGroup, \
    Zone


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

        if not sub_result:
            continue

        if int(sub_result[1]) > expansion:
            continue

        if not sub_result:
            sub_result = ['Unknown']
        out_data.append({'npc_id': npc_id,
                         'name': utils.fix_npc_name(npc_name),
                         'zone': sub_result[0]})
    return out_data


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

    # Update the faction to the name
    with Session(bind=engine) as session:
        query = session.query(FactionList.name, FactionList.id).\
            filter(NPCFactionEntries.npc_faction_id == base_data['npc_faction_id']).\
            filter(FactionList.id == NPCFactionEntries.faction_id)
        sub_result = query.first()
    if sub_result:
        base_data['faction'] = {'faction_name': sub_result[0], 'faction_id': sub_result[1]}
    else:
        base_data['faction'] = {}

    # Convert special abilities to make sense
    base_data.update({'special_attacks': utils.translate_specials(result.npcspecialattks)})

    # Get the spells this NPC uses
    spells = []
    loot_lists = {}
    spawn_groups = []
    merch = []
    with Session(bind=engine) as session:
        # If this is a merchant, get it's merchant items
        query = session.query(MerchantList.item, Item.Name, MerchantList.min_expansion, Item.icon).\
            filter(MerchantList.merchantid == npc_id).\
            filter(MerchantList.item == Item.id)
        result = query.all()
        for entry in result:
            if int(entry[2]) > expansion:
                continue
            merch.append({'item_id': entry[0],
                          'item_name': entry[1],
                          'icon': entry[3]})
        base_data['merch'] = merch

        # Get proc spell
        query = session.query(NPCSpells.attack_proc, SpellsNewReference.name,
                              NPCSpells.proc_chance, SpellsNewReference.new_icon).\
            filter(NPCSpells.id == base_data['npc_spells_id']).\
            filter(NPCSpells.attack_proc == SpellsNewReference.id)
        result = query.first()
        if result:
            spells.append({'spell_type': 'proc',
                           'spell_name': result[1],
                           'spell_id': result[0],
                           'proc_chance': result[2],
                           'icon': result[3]})
        # Get defensive proc spell
        query = session.query(NPCSpells.defensive_proc, SpellsNewReference.name,
                              NPCSpells.dproc_chance, SpellsNewReference.new_icon).\
            filter(NPCSpells.id == base_data['npc_spells_id']).\
            filter(NPCSpells.defensive_proc == SpellsNewReference.id)
        result = query.first()
        if result:
            spells.append({'spell_type': 'defensive',
                           'spell_name': result[1],
                           'spell_id': result[0],
                           'proc_chance': result[2],
                           'icon': result[3]})
        # Get ranged proc spell
        query = session.query(NPCSpells.range_proc, SpellsNewReference.name,
                              NPCSpells.rproc_chance, SpellsNewReference.new_icon).\
            filter(NPCSpells.id == base_data['npc_spells_id']).\
            filter(NPCSpells.range_proc == SpellsNewReference.id)
        result = query.first()
        if result:
            spells.append({'spell_type': 'ranged',
                           'spell_name': result[1],
                           'spell_id': result[0],
                           'proc_chance': result[2],
                           'icon': result[3]})

        # Get all cast spells
        query = session.query(NPCSpellsEntries.spellid, SpellsNewReference.name, SpellsNewReference.new_icon).\
            filter(NPCSpellsEntries.npc_spells_id == base_data['npc_spells_id']).\
            filter(NPCSpellsEntries.spellid == SpellsNewReference.id)
        result = query.all()
        for entry in result:
            spells.append({'spell_type': 'cast',
                           'spell_name': entry[1],
                           'spell_id': entry[0],
                           'proc_chance': None,
                           'icon': entry[2]})

        # Get the loot lists
        query = session.query(LootTableEntries).\
            filter(LootTableEntries.loottable_id == base_data['loottable_id'])
        result = query.all()
        for entry in result:
            # Get the name
            query = session.query(LootDrop.name).filter(LootDrop.id == entry.lootdrop_id)
            sub_result = query.first()
            if not sub_result:
                continue
            loot_list_name = sub_result[0]

            # Get the items
            query = session.query(LootDropEntries.item_id, Item.Name, LootDropEntries.chance, Item.icon).\
                filter(LootDropEntries.lootdrop_id == entry.lootdrop_id).filter(LootDropEntries.item_id == Item.id)
            sub_result = query.all()

            items = []
            for sub_entry in sub_result:
                item = {'item_id': sub_entry[0],
                        'item_name': sub_entry[1],
                        'probability': sub_entry[2],
                        'icon': sub_entry[3]}
                items.append(item)
            loot_lists.update({entry.lootdrop_id: {'name': loot_list_name,
                                                   'items': items,
                                                   'multiplier': entry.multiplier,
                                                   'droplimit': entry.droplimit,
                                                   'mindrop': entry.mindrop,
                                                   'probability': entry.probability}})

        # Get spawn point(s)
        args = [Spawn2.x, Spawn2.y, Spawn2.z, Spawn2.respawntime, SpawnGroup.name, SpawnGroup.id, Spawn2.id]
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
                                 'spawn_npcs': spawn_npcs,
                                 'group_id': entry[5],
                                 'spawn_id': entry[6]})

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


def get_npc_raw_data(npc_id):
    with Session(bind=engine) as session:
        query = session.query(NPCTypes).filter(NPCTypes.id == npc_id)
        result = query.one()

    ret_dict = result.__dict__
    ret_dict.pop('_sa_instance_state')
    return ret_dict
