import configparser
import os

from sqlalchemy import create_engine, and_, or_, Column, Integer
from sqlalchemy.orm import Session, aliased
from sqlalchemy.ext.automap import automap_base

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


def _get_link_filters():
    """Helper to return the basic link filters between zone, npc, and item"""
    return [NPCTypes.loottable_id == LootTableEntries.loottable_id,
            LootTableEntries.lootdrop_id == LootDropEntries.lootdrop_id,
            LootDropEntries.item_id == Item.id]


def main():
    # For each era, get a list of items that are found on NPCs in those expansions.
    eras = ['Classic', 'Kunark', 'Velious', 'Luclin', 'Planes', 'LoY', 'LDoN', 'GoD', 'OoW', 'DoN', 'DoDH', 'PoR',
            'TSS', 'TBS', 'SoF', 'SoD', 'UF', 'HoT', 'VoA', 'RoF']
    for era in eras:
        zone_or_filters = []
        quest_item_ids = []
        special_item_ids = []
        era_id = eras.index(era)

        zone_id_list = utils.get_era_zones(era)
        if era == 'Kunark':
            loy_id_list = utils.get_era_zones('LoY')
            zone_id_list = [item for item in zone_id_list if item not in loy_id_list]

        for zone_id in zone_id_list:
            zone_or_filters.append(NPCTypes.id.like(f'{zone_id}___'))

        # Now, we need to get the quest items.  These are stored in files
        if os.path.exists(os.path.join(here, f'item_files', f'{era}.txt')):
            with open(os.path.join(here, 'item_files', f'{era}.txt'), 'r') as fh:
                file_data = fh.read()
            quest_item_ids += file_data.split('\n')

        # Certain expansions have tradeskill items at the highest level, add those
        if os.path.exists(os.path.join(here, f'item_files/{era}_ts.txt')):
            with open(os.path.join(here, f'item_files/{era}_ts.txt'), 'r') as fh:
                file_data = fh.read()
            special_item_ids += file_data.split('\n')

        if os.path.exists(os.path.join(here, f'item_files/{era}_special.txt')):
            with open(os.path.join(here, f'item_files/{era}_special.txt'), 'r') as fh:
                file_data = fh.read()
            special_item_ids += file_data.split('\n')

        # Get the NPC drop items
        link_filters = _get_link_filters()
        link_params = and_(*link_filters)
        zone_or_params = or_(*zone_or_filters)
        with Session(bind=engine) as session:
            query = session.query(Item.id).\
                filter(zone_or_params).\
                filter(link_params).\
                group_by(Item.id)
            result = query.all()

        zone_items = [item for t in result for item in t]

        # Get the base, enchanted, and legendary ids for each item
        full_ids = zone_items + quest_item_ids + special_item_ids
        out_ids = []
        for item_id in full_ids:
            if not item_id:
                continue
            if int(item_id) > 2000000:
                out_ids.append(int(item_id) - 1000000)
                out_ids.append(int(item_id) - 2000000)
            elif 2000000 > int(item_id) > 1000000:
                out_ids.append(int(item_id) + 1000000)
                out_ids.append(int(item_id) - 1000000)
            else:
                out_ids.append(int(item_id) + 1000000)
                out_ids.append(int(item_id) + 2000000)
        era_ids = list(set(out_ids))

        # Write to the sql file:
        with open(os.path.join('C:\\temp\\', f'item_expansion.sql'), 'a') as fh:
            for entry in era_ids:
                fh.write(f'INSERT INTO `item_expansion` VALUES ({entry}, {era_id});\n')


if __name__ == '__main__':
    main()