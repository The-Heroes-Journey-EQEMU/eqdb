from sqlalchemy import create_engine, text
import configparser
import os

def get_config():
    """Get configuration from configuration.ini file"""
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    return config

class NPCDB:
    def __init__(self):
        """Initialize the NPC database connection"""
        config = get_config()
        db_config = config['database']
        url = f"{db_config['driver']}{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(url)
    
    def get_npc_raw_data(self, npc_id=None, name=None, zone=None):
        """Get raw NPC data from the database"""
        with self.engine.connect() as conn:
            if npc_id:
                query = text("""
                    SELECT * FROM npc_types 
                    WHERE id = :npc_id
                """)
                result = conn.execute(query, {"npc_id": npc_id}).fetchone()
                if result:
                    return dict(result._mapping)
                return None
            elif name:
                query = text("""
                    SELECT * FROM npc_types 
                    WHERE name LIKE :name
                    AND (:zone IS NULL OR zone = :zone)
                    LIMIT 50
                """)
                results = conn.execute(query, {"name": f"%{name}%", "zone": zone}).fetchall()
                return [dict(row._mapping) for row in results]
            return None 