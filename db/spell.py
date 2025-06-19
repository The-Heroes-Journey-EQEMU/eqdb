from sqlalchemy import create_engine, text
import configparser
import os

def get_config():
    """Get configuration from configuration.ini file"""
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    return config

class SpellDB:
    def __init__(self):
        """Initialize the spell database connection"""
        config = get_config()
        db_config = config['database']
        url = f"{db_config['driver']}{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(url)
    
    def get_spell_raw_data(self, spell_id=None, spell_name=None, spell_class=None):
        """Get raw spell data from the database"""
        with self.engine.connect() as conn:
            if spell_id:
                query = text("""
                    SELECT * FROM spells_new 
                    WHERE id = :spell_id
                """)
                result = conn.execute(query, {"spell_id": spell_id}).fetchone()
                if result:
                    return dict(result._mapping)
                return None
            elif spell_name:
                query = text("""
                    SELECT * FROM spells_new 
                    WHERE name LIKE :spell_name
                    LIMIT 50
                """)
                results = conn.execute(query, {"spell_name": f"%{spell_name}%"}).fetchall()
                return [dict(row._mapping) for row in results]
            elif spell_class:
                query = text("""
                    SELECT * FROM spells_new 
                    WHERE classes LIKE :spell_class
                    LIMIT 50
                """)
                results = conn.execute(query, {"spell_class": f"%{spell_class}%"}).fetchall()
                return [dict(row._mapping) for row in results]
            return None 