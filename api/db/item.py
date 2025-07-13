from sqlalchemy import text
from api.db_manager import db_manager

class ItemDB:
    def __init__(self):
        """Initialize the ItemDB class."""
        pass
    
    def get_item_raw_data(self, item_id=None, name=None, item_type=None):
        """Get raw item data from the database"""
        engine = db_manager.get_engine_for_table('items')
        with engine.connect() as conn:
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
