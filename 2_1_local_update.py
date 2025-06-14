"""Creates the local sqlite3 database to hold item data"""
import configparser
import os

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, or_, and_
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

import utils

local_engine = create_engine('sqlite:///local_db.db')

LocalBase = declarative_base()


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


def main():
    """Main execution"""
    # Create the database anew
    LocalBase.metadata.create_all(local_engine)
    print('Job done!')


if __name__ == '__main__':
    main()
