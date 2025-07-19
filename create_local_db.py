"""Creates the local sqlite3 database to hold item data"""
import configparser
import os

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session


local_engine = create_engine('sqlite:///local_db.db')
LocalBase = declarative_base()


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


class Weights(LocalBase):
    __tablename__ = 'weights'
    wid = Column(Integer, primary_key=True)
    uid = Column(Integer)
    name = Column(String)


class WeightEntry(LocalBase):
    __tablename__ = 'weight_entry'
    weid = Column(Integer, primary_key=True)
    wid = Column(Integer)
    stat = Column(String)
    value = Column(Integer)


class Restricts(LocalBase):
    __tablename__ = 'restricts'
    rid = Column(Integer, primary_key=True)
    uid = Column(Integer)
    name = Column(String)


class RestrictEntry(LocalBase):
    __tablename__ = 'restrict_entry'
    reid = Column(Integer, primary_key=True)
    rid = Column(Integer)
    stat = Column(String)
    value = Column(Integer)


class GearList(LocalBase):
    __tablename__ = 'gear_list'
    glid = Column(Integer, primary_key=True)
    uid = Column(Integer)
    name = Column(String)
    private = Column(Integer)


class GearListEntry(LocalBase):
    __tablename__ = 'gear_list_entry'
    gleid = Column(Integer, primary_key=True)
    glid = Column(Integer)
    slot = Column(String)
    augslot = Column(String)
    item_id = Column(Integer)


class Characters(LocalBase):
    __tablename__ = 'characters'
    cid = Column(Integer, primary_key=True)
    uid = Column(Integer)
    name = Column(String)
    class1 = Column(String)
    class2 = Column(String)
    class3 = Column(String)
    level = Column(Integer)
    character_set = Column(String)
    inventory_blob = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


def main():
    """Main execution"""

    # Destroy the current database, if it's there
    if os.path.exists(os.path.join('.', 'local_db.db')):
        os.unlink(os.path.join('.', 'local_db.db'))

    # Create the database anew
    LocalBase.metadata.create_all(local_engine)

    # Create the anonymous contributor
    with Session(bind=local_engine) as session:
        anon_contrib = Contributor(name='Anonymous',
                                   id=-1,
                                   contributed=1)
        session.add(anon_contrib)
        session.commit()
    print('Job done!')


if __name__ == '__main__':
    main()
