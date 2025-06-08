from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

import utils
from logic import engine, Item, LootTable, LootTableEntries, LootDrop, LootDropEntries, NPCTypes


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
            query = session.query(Item.id, Item.Name, Item.icon).filter(params).filter(or_params).limit(50)
        else:
            query = session.query(Item.id, Item.Name, Item.icon).filter(params).limit(50)
        result = query.all()

    out_data = []
    for entry in result:
        item_id = entry[0]
        excl_list = utils.get_exclusion_list('item')
        if item_id in excl_list:
            return None
        name = entry[1]
        icon = entry[2]
        if no_glamours and 'glamour' in name.lower():
            continue
        out_data.append({'item_id': item_id,
                         'name': name,
                         'icon': icon})
    return out_data


def get_item_raw_data(item_id):
    excl_list = utils.get_exclusion_list('item')
    if item_id in excl_list:
        return None

    with Session(bind=engine) as session:
        query = session.query(Item).filter(Item.id == item_id)
        result = query.one()

    ret_dict = result.__dict__
    ret_dict.pop('_sa_instance_state')
    return ret_dict


def get_loot_json(loot_id=None, npc_id=None):
    excl_list = utils.get_exclusion_list('loottable')
    if loot_id in excl_list:
        return []
    npc_excl_list = utils.get_exclusion_list('npcs')
    if npc_id in npc_excl_list:
        return []

    with Session(bind=engine) as session:
        if npc_id:
            query = session.query(NPCTypes.loottable_id).filter(NPCTypes.id == npc_id)
            result = query.one()
            if not result:
                return {}
            loot_id = result[0]

        query = session.query(LootTable).filter(LootTable.id == loot_id)
        result = query.one()
        ret_dict = result.__dict__
        ret_dict.pop('_sa_instance_state')

        query = session.query(LootTableEntries).filter(LootTableEntries.loottable_id == loot_id)
        result = query.all()

        lt_entries = []
        for entry in result:
            lt_entry = entry.__dict__
            lt_entry.pop('_sa_instance_state')

            query = session.query(LootDrop).filter(LootDrop.id == lt_entry['lootdrop_id'])
            sub_result = query.one()
            drop = sub_result.__dict__
            drop.pop('_sa_instance_state')

            query = session.query(LootDropEntries).filter(LootDropEntries.lootdrop_id == lt_entry['lootdrop_id'])
            sub_result = query.all()
            ld_entries = []
            for sub_entry in sub_result:
                ld_entry = sub_entry.__dict__
                ld_entry.pop('_sa_instance_state')
                ld_entries.append(ld_entry)
            lt_entry.update({'lootdrop_entries': ld_entries})
            lt_entry.update({'lootdrop': drop})
            lt_entries.append(lt_entry)
        ret_dict.update({'loottable_entries': lt_entries})
        return ret_dict


def get_item_json(name=None, item_id=None, i_type=None):
    excl_list = utils.get_exclusion_list('item')
    if item_id in excl_list:
        return []
    with Session(bind=engine) as session:
        if item_id:
            query = session.query(Item).filter(Item.id == item_id)
            result = query.first()
            if not result:
                return {}
            ret_dict = result.__dict__
            ret_dict.pop('_sa_instance_state')
            return ret_dict
        else:
            ret_list = []
            partial = "%%%s%%" % name
            if i_type is None:
                query = session.query(Item).filter(Item.Name.like(partial))
            elif i_type.lower() == 'base':
                query = session.query(Item).filter(Item.Name.like(partial)).filter(Item.id < 1000000)
            elif i_type.lower() == 'ench':
                query = session.query(Item).filter(Item.Name.like(partial)).\
                    filter(and_(1000000 < Item.id, Item.id < 2000000))
            elif i_type.lower() == 'legend':
                query = session.query(Item).filter(Item.Name.like(partial)).filter(Item.id > 2000000)
            else:
                query = session.query(Item).filter(Item.Name.like(partial))

            result = query.limit(50).all()
            if not result:
                return {}
            for entry in result:
                entry = entry.__dict__
                entry.pop('_sa_instance_state')
                if entry['id'] in excl_list:
                    continue
                ret_list.append(entry)
            return ret_list


def get_item_name(item_id):
    excl_list = utils.get_exclusion_list('item')
    if item_id in excl_list:
        return None
    with Session(bind=engine) as session:
        query = session.query(Item.Name).filter(Item.id == item_id)
        result = query.one()
    return result[0]
