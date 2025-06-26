#!/usr/bin/env python3
"""
Script to import expansion item files into the local database.
This script reads all item files from the item_files directory and imports them
into the expansion_items table for tracking items by expansion.
"""

import os
import sys
import logging
from db.expansion_items import ExpansionItemsDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to import expansion items"""
    try:
        # Initialize database connection (using SQLite for local storage)
        db = ExpansionItemsDB('sqlite:///expansion_items.db')
        
        # Get the item_files directory path
        item_files_dir = os.path.join(os.path.dirname(__file__), 'item_files')
        
        if not os.path.exists(item_files_dir):
            logger.error(f"Item files directory not found: {item_files_dir}")
            sys.exit(1)
        
        logger.info(f"Starting import from: {item_files_dir}")
        
        # Import all item files
        total_imported = db.import_item_files(item_files_dir)
        
        logger.info(f"Import completed successfully!")
        logger.info(f"Total items imported: {total_imported}")
        
        # Show summary
        summary = db.get_expansion_summary()
        logger.info("Expansion Summary:")
        for expansion_id, counts in summary.items():
            if counts['total'] > 0:
                logger.info(f"  Expansion {expansion_id}: {counts['total']} total items "
                          f"({counts['regular']} regular, {counts['tradeskill']} tradeskill, "
                          f"{counts['special']} special, {counts['custom']} custom)")
        
    except Exception as e:
        logger.error(f"Error during import: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 