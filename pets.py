"""EQDB Logic File for Pets"""
from sqlalchemy import or_
from sqlalchemy.orm import Session

import utils
from logic import SpellsNewReference, SpellsNew, engine, Pets, NPCTypes, NPCSpells, NPCSpellsEntries


def get_all_class_pets(class_id):
    spas = [SpellsNewReference.effectid1 == 33, SpellsNewReference.effectid1 == 71, SpellsNewReference.effectid1 == 106]
    spa_param = or_(*spas)
    class_name = utils.get_spell_class(class_id)
    with Session(bind=engine) as session:
        query = session.query(SpellsNewReference.id, SpellsNewReference.name,
                              SpellsNewReference.teleport_zone, SpellsNewReference.new_icon,
                              NPCTypes.race, NPCTypes.level, getattr(NPCTypes, 'class'), NPCTypes.hp, NPCTypes.AC,
                              NPCTypes.mindmg, NPCTypes.maxdmg, getattr(SpellsNewReference, f'classes{class_id}')).\
            filter(spa_param).\
            filter(getattr(SpellsNewReference, f'classes{class_id}') <= 65).\
            filter(SpellsNewReference.teleport_zone == Pets.type).\
            filter(NPCTypes.id == Pets.npcID)
        result = query.all()
    data = []
    name_check = []
    for entry in result:
        if entry[2] in name_check:
            continue
        data.append({'spell_id': entry[0],
                     'spell_name': entry[1],
                     'pet_name': entry[2],
                     'icon': entry[3],
                     'race': utils.get_bane_dmg_race(entry[4]),
                     'pet_level': entry[5],
                     'class': utils.get_spell_class(entry[6]),
                     'hp': entry[7],
                     'ac': entry[8],
                     'mindmg': entry[9],
                     'maxdmg': entry[10],
                     'level': entry[11]})
        name_check.append(entry[2])
    return data, class_name


def get_pet_data(pet_spell_name, include_base=True):
    # Get basic data
    base_data = {}
    if include_base:
        with Session(bind=engine) as session:
            query = session.query(Pets.id, Pets.type, Pets.petpower, Pets.npcID, Pets.temp).\
                filter(Pets.type == pet_spell_name)
            result = query.first()

        if not result:
            return None

        base_data = {'pet_id': result[0],
                     'pet_name': result[1],
                     'pet_power': result[2],
                     'swarm_pet': 'No' if not bool(result[4]) else 'Yes'}
        npc_id = result[3]
    else:
        with Session(bind=engine) as session:
            query = session.query(Pets.npcID).filter(Pets.type == pet_spell_name)
            result = query.first()
        npc_id = result[0]

    # Get the NPC data we care about
    with Session(bind=engine) as session:
        query = session.query(NPCTypes).filter(NPCTypes.id == npc_id)
        result = query.first()
    if not result:
        return None
    npc_data = result.__dict__
    npc_data.pop('_sa_instance_state')

    # Update certain things
    npc_data['bodytype'] = utils.get_bane_dmg_body(npc_data['bodytype'])
    npc_data['class'] = utils.get_spell_class(npc_data['class'])
    npc_data['race'] = utils.get_bane_dmg_race(npc_data['race'])

    # Convert special abilities to make sense
    spc = result.npcspecialattks
    specials = utils.translate_specials(spc)
    specials = ', '.join(specials)
    npc_data.update({'special_attacks': specials})
    if include_base:
        base_data.update({'npc': npc_data})
    else:
        return npc_data

    spells = []
    with Session(bind=engine) as session:
        # Get proc spell
        query = session.query(NPCSpells.attack_proc, SpellsNewReference.name,
                              NPCSpells.proc_chance, SpellsNewReference.new_icon).\
            filter(NPCSpells.id == npc_data['npc_spells_id']).\
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
            filter(NPCSpells.id == npc_data['npc_spells_id']).\
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
            filter(NPCSpells.id == npc_data['npc_spells_id']).\
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
            filter(NPCSpellsEntries.npc_spells_id == npc_data['npc_spells_id']).\
            filter(NPCSpellsEntries.spellid == SpellsNewReference.id)
        result = query.all()
        for entry in result:
            spells.append({'spell_type': 'cast',
                           'spell_name': entry[1],
                           'spell_id': entry[0],
                           'proc_chance': None,
                           'icon': entry[2]})

    base_data.update({'spells': spells})
    return base_data
