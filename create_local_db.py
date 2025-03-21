"""Creates the local sqlite3 database to hold item data"""
import configparser
import os

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, or_, and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

import utils

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
local_engine = create_engine('sqlite:///local_db.db')

Base = automap_base()
LocalBase = declarative_base()


class ItemRedirection(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)


Base.prepare(autoload_with=engine)

Zone = Base.classes.zone
Item = ItemRedirection
NPCTypes = Base.classes.npc_types
LootTableEntries = Base.classes.loottable_entries
LootDropEntries = Base.classes.lootdrop_entries
MerchantList = Base.classes.merchantlist


class IdentifiedItems(LocalBase):
    __tablename__ = 'identified_items'
    iiid = Column(Integer, primary_key=True)
    item_id = Column(Integer, unique=True)
    expansion = Column(Integer)
    source = Column(String)
    zone_id = Column(Integer)


class Contributor(LocalBase):
    __tablename__ = 'contributor'
    cid = Column(Integer, primary_key=True)
    name = Column(String)
    id = Column(Integer, unique=True)
    contributed = Column(Integer)


class IDEntry(LocalBase):
    __tablename__ = 'id_entry'
    ideid = Column(Integer, primary_key=True)
    item_id = Column(Integer)
    cid = Column(Integer)
    expansion = Column(Integer)
    source = Column(String)
    zone_id = Column(Integer)


def _get_link_filters():
    """Helper to return the basic link filters between zone, npc, and item"""
    return [NPCTypes.loottable_id == LootTableEntries.loottable_id,
            LootTableEntries.lootdrop_id == LootDropEntries.lootdrop_id,
            LootDropEntries.item_id == Item.id]


def main():
    """Main execution"""

    # Destroy the current database, if it's there
    if os.path.exists(os.path.join('.', 'local_db.db')):
        os.unlink(os.path.join('.', 'local_db.db'))

    # Create the database anew
    LocalBase.metadata.create_all(local_engine)

    # Get a new session and populate things with the base data (drop and vendor data)
    eras = {'Classic': {'name': 'Classic', 'id': 0},
            'Kunark': {'name': 'Ruins of Kunark', 'id': 1},
            'Velious': {'name': 'Scars of Velious', 'id': 2},
            'Luclin': {'name': 'Shadows of Luclin', 'id': 3},
            'Planes': {'name': 'Planes of Power', 'id': 4},
            'LoY': {'name': 'Legacy of Ykesha', 'id': 5},
            'LDoN': {'name': 'Lost Dungeons of Norrath', 'id': 6},
            'GoD': {'name': 'Gates of Discord', 'id': 7},
            'OoW': {'name': 'Omens of War', 'id': 8},
            'DoN': {'name': 'Dragons of Norrath', 'id': 9},
            'DoDH': {'name': 'Depths of Darkhollow', 'id': 10},
            'PoR': {'name': 'Prophecy of Ro', 'id': 11},
            'TSS': {'name': 'The Serpents Spine', 'id': 12},
            'TBS': {'name': 'The Buried Sea', 'id': 13},
            'SoF': {'name': 'Secrets of Faydwer', 'id': 14},
            'SoD': {'name': 'Seeds of Destruction', 'id': 15},
            'UF': {'name': 'Underfoot', 'id': 16},
            'HoT': {'name': 'House of Thule', 'id': 17},
            'VoA': {'name': 'Veil of Alaris', 'id': 18},
            'RoF': {'name': 'Rain of Fear', 'id': 19}
            }
    params = and_(*_get_link_filters())

    print('Inserting vendor items...')
    source = 'Vendor'
    for era in eras:
        era_name = eras[era]['name']
        print(f'Inserting {era_name} vendor items...')
        era_id = eras[era]['id']
        zone_id_list = utils.get_era_zones(era)
        for zone_id in zone_id_list:
            print(f'Zone id: {zone_id}')
            with Session(bind=engine) as session:
                query = session.query(MerchantList.item, NPCTypes.id, NPCTypes.name).\
                    filter(MerchantList.merchantid.like(f'{zone_id}___')).\
                    filter(MerchantList.merchantid == NPCTypes.merchant_id).\
                    group_by(MerchantList.item)
                result = query.all()
            print(f'Result: {result}')
            for entry in result:
                item_id = entry[0]
                npc_id = entry[1]
                npc_name = entry[2]

                with Session(bind=local_engine) as session:
                    # See if this item already exists
                    query = session.query(IdentifiedItems.item_id).filter(IdentifiedItems.item_id == item_id)
                    result = query.all()
                    if result:
                        continue
                    print(f'Adding {item_id} from {npc_id}:{npc_name}')
                    new_item = IdentifiedItems(item_id=item_id,
                                               expansion=era_id,
                                               source=source,
                                               zone_id=zone_id)
                    session.add(new_item)
                    session.commit()

    print('Inserting dropped items...')
    source = 'Dropped'
    for era in eras:
        era_name = eras[era]['name']
        print(f'Inserting {era_name} dropped items...')
        era_id = eras[era]['id']
        zone_id_list = utils.get_era_zones(era)
        for zone_id in zone_id_list:
            with Session(bind=engine) as session:
                query = session.query(Item.id, NPCTypes.id, Item.Name, NPCTypes.name).\
                    filter(NPCTypes.id.like(f'{zone_id}___')).\
                    filter(params).\
                    group_by(Item.id)
                result = query.all()

            for entry in result:
                item_id = entry[0]
                npc_id = entry[1]
                item_name = entry[2]
                npc_name = entry[3]
                with Session(bind=local_engine) as session:
                    # See if this item already exists
                    query = session.query(IdentifiedItems.item_id).filter(IdentifiedItems.item_id == item_id)
                    result = query.all()
                    if result:
                        continue
                    print(f'Adding {item_id}:{item_name} from {npc_id}:{npc_name}')
                    new_item = IdentifiedItems(item_id=item_id,
                                               expansion=era_id,
                                               source=source,
                                               zone_id=zone_id)
                    session.add(new_item)
                    session.commit()

    # Add all the glamour stones as classic items
    with Session(bind=engine) as session:
        query = session.query(Item.id).filter(Item.Name.like("%%Glamour-stone%%"))
        result = query.all()

    with Session(bind=local_engine) as session:
        for entry in result:
            query = session.query(IdentifiedItems.item_id).filter(IdentifiedItems.item_id == entry[0])
            result = query.all()
            if result:
                continue
            new_item = IdentifiedItems(item_id=entry[0],
                                       expansion=0,
                                       source='Quest',
                                       zone_id=151)
            session.add(new_item)
            session.commit()

    print('Job done!')


if __name__ == '__main__':
    main()
