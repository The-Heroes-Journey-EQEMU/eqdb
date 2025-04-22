"""EQDB Logic File for Item Identify"""
import random

from sqlalchemy import and_
from sqlalchemy.orm import Session

from logic import local_engine, Contributor, IDEntry, IdentifiedItems, engine, Item, get_item_data


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
