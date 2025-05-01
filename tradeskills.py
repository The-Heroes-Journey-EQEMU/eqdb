from sqlalchemy import and_
from sqlalchemy.orm import Session

import utils
from logic import TradeskillRecipe, engine, TradeskillRecipeEntries, Item, expansion


def get_tradeskill_detail(ts_id):
    # Get the tradeskill base details
    base_data = {}
    with Session(bind=engine) as session:
        args = [TradeskillRecipe.name, TradeskillRecipe.tradeskill, TradeskillRecipe.skillneeded,
                TradeskillRecipe.trivial, TradeskillRecipe.nofail, TradeskillRecipe.replace_container,
                TradeskillRecipe.must_learn, TradeskillRecipe.enabled, TradeskillRecipe.min_expansion]
        query = session.query(*args).filter(TradeskillRecipe.id == ts_id)
        result = query.first()
    if not result:
        return None

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
                TradeskillRecipeEntries.failcount, TradeskillRecipeEntries.componentcount, Item.icon]
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
        icon = entry[5]

        if successcount > 0:
            success.append({'item_id': item_id,
                            'item_name': item_name,
                            'count': successcount,
                            'icon': icon})
        if failcount > 0:
            fail.append({'item_id': item_id,
                         'item_name': item_name,
                         'count': failcount,
                         'icon': icon})
        if componentcount > 0:
            components.append({'item_id': item_id,
                               'item_name': item_name,
                               'count': componentcount,
                               'icon': icon})
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


def get_tradeskills(name=None, trivial=None, tradeskill=None, remove_no_fail=False, trivial_min=None):
    filters = [TradeskillRecipe.enabled == 1]
    if name:
        partial = "%%%s%%" % name
        filters.append(TradeskillRecipe.name.like(partial))
    if trivial:
        filters.append(TradeskillRecipe.trivial <= int(trivial))
    if trivial_min:
        filters.append(TradeskillRecipe.trivial >= int(trivial_min))
    if tradeskill:
        filters.append(TradeskillRecipe.tradeskill == tradeskill)
    if remove_no_fail:
        filters.append(TradeskillRecipe.nofail != 1)

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
