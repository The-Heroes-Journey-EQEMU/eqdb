from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
Base = declarative_base()

class ExpansionItem(Base):
    __tablename__ = 'expansion_items'
    
    id = Column(Integer, primary_key=True)
    item_id = Column(Integer, nullable=False)
    expansion_id = Column(Integer, nullable=False)
    item_type = Column(String(20), nullable=False)  # 'regular', 'tradeskill', 'custom'
    is_custom = Column(Boolean, default=False)
    added_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(500))

class ExpansionItemsDB:
    def __init__(self, connection_string):
        """Initialize the expansion items database connection"""
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info("Expansion items database initialized")
    
    def import_item_files(self, item_files_dir):
        """Import all item files from the item_files directory"""
        logger.info("Starting import of item files")
        
        # Mapping of file names to expansion IDs
        expansion_mapping = {
            'Classic': 0,
            'Kunark': 1,
            'Velious': 2,
            'Luclin': 3,
            'Planes': 4,
            'LoY': 5,
            'LDoN': 6,
            'GoD': 7,
            'OoW': 8,
            'DoN': 9,
            'DoDH': 10,
            'PoR': 11,
            'TSS': 12,
            'TBS': 13,
            'SoF': 14,
            'SoD': 15,
            'UF': 16,
            'HoT': 17,
            'VoA': 18,
            'RoF': 19
        }
        
        imported_count = 0
        
        for filename in os.listdir(item_files_dir):
            if filename.endswith('.txt') and filename != 'zonelist.txt':
                # Determine expansion and type
                expansion_name = None
                item_type = 'regular'
                
                for exp_name in expansion_mapping.keys():
                    if filename.startswith(exp_name):
                        expansion_name = exp_name
                        if filename.endswith('_ts.txt'):
                            item_type = 'tradeskill'
                        elif filename.endswith('_special.txt'):
                            item_type = 'special'
                        break
                
                if expansion_name and expansion_name in expansion_mapping:
                    expansion_id = expansion_mapping[expansion_name]
                    file_path = os.path.join(item_files_dir, filename)
                    
                    try:
                        count = self.import_item_file(file_path, expansion_id, item_type)
                        imported_count += count
                        logger.info(f"Imported {count} items from {filename} (Expansion: {expansion_name}, Type: {item_type})")
                    except Exception as e:
                        logger.error(f"Error importing {filename}: {str(e)}")
        
        logger.info(f"Total items imported: {imported_count}")
        return imported_count
    
    def import_item_file(self, file_path, expansion_id, item_type):
        """Import items from a specific file"""
        count = 0
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and line.isdigit():
                    item_id = int(line)
                    
                    # Check if item already exists
                    existing = self.session.query(ExpansionItem).filter_by(
                        item_id=item_id, 
                        expansion_id=expansion_id,
                        item_type=item_type
                    ).first()
                    
                    if not existing:
                        expansion_item = ExpansionItem(
                            item_id=item_id,
                            expansion_id=expansion_id,
                            item_type=item_type,
                            is_custom=False
                        )
                        self.session.add(expansion_item)
                        count += 1
        
        self.session.commit()
        return count
    
    def get_items_by_expansion(self, expansion_id, item_type=None):
        """Get items for a specific expansion"""
        query = self.session.query(ExpansionItem).filter_by(expansion_id=expansion_id)
        
        if item_type:
            query = query.filter_by(item_type=item_type)
        
        return query.all()
    
    def get_items_by_type(self, item_type):
        """Get all items of a specific type across all expansions"""
        return self.session.query(ExpansionItem).filter_by(item_type=item_type).all()
    
    def add_custom_item(self, item_id, expansion_id, item_type='custom', notes=None):
        """Add a custom item to the expansion"""
        expansion_item = ExpansionItem(
            item_id=item_id,
            expansion_id=expansion_id,
            item_type=item_type,
            is_custom=True,
            notes=notes
        )
        self.session.add(expansion_item)
        self.session.commit()
        return expansion_item
    
    def remove_custom_item(self, item_id, expansion_id):
        """Remove a custom item"""
        item = self.session.query(ExpansionItem).filter_by(
            item_id=item_id, 
            expansion_id=expansion_id,
            is_custom=True
        ).first()
        
        if item:
            self.session.delete(item)
            self.session.commit()
            return True
        return False
    
    def get_custom_items(self, expansion_id=None):
        """Get custom items"""
        query = self.session.query(ExpansionItem).filter_by(is_custom=True)
        
        if expansion_id is not None:
            query = query.filter_by(expansion_id=expansion_id)
        
        return query.all()
    
    def get_expansion_summary(self):
        """Get summary of items by expansion and type"""
        summary = {}
        
        for expansion_id in range(20):  # 0-19 expansions
            summary[expansion_id] = {
                'regular': 0,
                'tradeskill': 0,
                'special': 0,
                'custom': 0,
                'total': 0
            }
            
            items = self.get_items_by_expansion(expansion_id)
            for item in items:
                summary[expansion_id][item.item_type] += 1
                summary[expansion_id]['total'] += 1
        
        return summary
    
    def search_items(self, item_id=None, expansion_id=None, item_type=None, is_custom=None):
        """Search for items with various filters"""
        query = self.session.query(ExpansionItem)
        
        if item_id is not None:
            query = query.filter_by(item_id=item_id)
        if expansion_id is not None:
            query = query.filter_by(expansion_id=expansion_id)
        if item_type is not None:
            query = query.filter_by(item_type=item_type)
        if is_custom is not None:
            query = query.filter_by(is_custom=is_custom)
        
        return query.all()
    
    def update_item_notes(self, item_id, expansion_id, notes):
        """Update notes for an item"""
        item = self.session.query(ExpansionItem).filter_by(
            item_id=item_id,
            expansion_id=expansion_id
        ).first()
        
        if item:
            item.notes = notes
            self.session.commit()
            return True
        return False 