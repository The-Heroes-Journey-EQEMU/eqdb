from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from logic import engine, Item


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


def get_item_raw_data(item_id):
    with Session(bind=engine) as session:
        query = session.query(Item).filter(Item.id == item_id)
        result = query.one()

    ret_dict = result.__dict__
    ret_dict.pop('_sa_instance_state')
    return ret_dict
