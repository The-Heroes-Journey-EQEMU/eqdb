#!/usr/bin/env python3

"""Add weight sets tables to existing local database"""

import configparser
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

# Read configuration
here = os.path.dirname(__file__)
site_config = configparser.RawConfigParser()
ini_path = os.path.join(here, 'configuration.ini')
site_config.read_file(open(ini_path))
local_database = site_config.get('local_database', 'connection')
local_engine = create_engine(local_database)
LocalBase = declarative_base()

# Define the missing tables
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
    """Add missing tables to existing database"""
    print("Adding weight sets tables to existing local database...")
    
    # Create only the missing tables (don't recreate existing ones)
    LocalBase.metadata.create_all(local_engine)
    
    print("Weight sets tables added successfully!")
    print("Added tables: weights, weight_entry, restricts, restrict_entry, gear_list, gear_list_entry")

if __name__ == '__main__':
    main() 