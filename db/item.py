from sqlalchemy import create_engine, text
import configparser
import os

def get_config():
    """Get configuration from configuration.ini file"""
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    return config

class ItemDB:
    def __init__(self):
        """Initialize the item database connection"""
        config = get_config()
        db_config = config['database']
        url = f"{db_config['driver']}{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        self.engine = create_engine(url)
    
    def get_item_raw_data(self, item_id=None, name=None, item_type=None):
        """Get raw item data from the database"""
        with self.engine.connect() as conn:
            if item_id:
                query = text("""
                    SELECT * FROM items 
                    WHERE id = :item_id
                """)
                result = conn.execute(query, {"item_id": item_id}).fetchone()
                if result:
                    return dict(result._mapping)
                return None
            elif name:
                query = text("""
                    SELECT * FROM items 
                    WHERE name LIKE :name
                    LIMIT 50
                """)
                results = conn.execute(query, {"name": f"%{name}%"}).fetchall()
                return [dict(row._mapping) for row in results]
            elif item_type:
                query = text("""
                    SELECT * FROM items 
                    WHERE type = :item_type
                    LIMIT 50
                """)
                results = conn.execute(query, {"item_type": item_type}).fetchall()
                return [dict(row._mapping) for row in results]
            return None 