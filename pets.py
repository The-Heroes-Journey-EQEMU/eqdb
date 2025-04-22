"""EQDB Logic File for Pets"""
from sqlalchemy import or_
from sqlalchemy.orm import Session

import logic
import utils
from logic import SpellsNewReference, SpellsNew, engine, Pets, NPCTypes


def get_all_class_pets(class_id):
    spas = [SpellsNewReference.effectid1 == 33, SpellsNewReference.effectid1 == 71, SpellsNewReference.effectid1 == 106]
    spa_param = or_(*spas)
    with Session(bind=engine) as session:
        query = session.query(SpellsNewReference.id, SpellsNewReference.name, SpellsNewReference.teleport_zone).\
            filter(spa_param).\
            filter(getattr(SpellsNewReference, f'classes{class_id}') != 255)
        result = query.all()
    data = []
    for entry in result:
        data.append({'spell_id': entry[0],
                     'spell_name': entry[1],
                     'pet_name': entry[2]})
    return data


def get_pet_data(pet_spell_name):
    # Get basic data
    with Session(bind=engine) as session:
        query = session.query(Pets.id, Pets.type, Pets.petpower, Pets.npcID, Pets.temp).\
            filter(Pets.type == pet_spell_name)
        result = query.first()

    if not result:
        return None

    base_data = {'pet_id': result[0],
                 'pet_name': result[1],
                 'pet_power': result[2],
                 'swarm_pet': bool(result[4])}
    npc_id = result[3]

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
    npc_data['class'] = utils.get_class_string(npc_data['class'])
    npc_data['race'] = utils.get_bane_dmg_race(npc_data['race'])

    # Convert special abilities to make sense
    spc = result.npcspecialattks
    npc_data.update({'special_attacks': utils.translate_specials(spc)})
    base_data.update({'npc': npc_data})

    return base_data
