#!/usr/bin/env python3

import sqlite3
import sys

def create_character_tables():
    """Create character tables in the local database"""
    
    conn = sqlite3.connect('local_db.db')
    cursor = conn.cursor()
    
    try:
        # Create characters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS characters (
                cid INTEGER PRIMARY KEY AUTOINCREMENT,
                uid INTEGER NOT NULL,
                name TEXT NOT NULL,
                class1 TEXT NOT NULL,
                class2 TEXT,
                class3 TEXT,
                level INTEGER NOT NULL DEFAULT 1,
                character_set TEXT,
                inventory_blob TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (uid) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        
        # Create index on user ID for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_characters_uid 
            ON characters(uid)
        ''')
        
        # Create unique index on user + character name
        cursor.execute('''
            CREATE UNIQUE INDEX IF NOT EXISTS idx_characters_uid_name 
            ON characters(uid, name)
        ''')
        
        conn.commit()
        print("✅ Character tables created successfully")
        
        # Verify tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='characters'")
        if cursor.fetchone():
            print("✅ Characters table verified")
        else:
            print("❌ Characters table not found")
            return False
            
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("Creating character tables...")
    if create_character_tables():
        print("✅ Character tables setup complete")
        sys.exit(0)
    else:
        print("❌ Character tables setup failed")
        sys.exit(1) 