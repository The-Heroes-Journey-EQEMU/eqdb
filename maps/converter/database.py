import os
import json
import sqlite3
import logging
from typing import Dict, List, Optional
from dataclasses import asdict
from datetime import datetime

from parser import MapData, LineSegment, Label, Waypoint

class MapDatabase:
    def __init__(self, db_path: str = "map_data.db", output_dir: str = "../output"):
        self.db_path = db_path
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Zone metadata table - stores only metadata, not geometry data
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS zone_geometry_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone_short_name TEXT UNIQUE NOT NULL,
                    zone_long_name TEXT NOT NULL,
                    expansion_id INTEGER NOT NULL,
                    gltf_file_path TEXT,                    -- Path to glTF file in filesystem
                    file_size INTEGER,                       -- File size in bytes
                    vertex_count INTEGER,                    -- Total vertices in geometry
                    triangle_count INTEGER,                  -- Total triangles in geometry
                    bounding_box_min_x REAL,
                    bounding_box_min_y REAL,
                    bounding_box_min_z REAL,
                    bounding_box_max_x REAL,
                    bounding_box_max_y REAL,
                    bounding_box_max_z REAL,
                    conversion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version TEXT DEFAULT '1.0',
                    status TEXT DEFAULT 'parsed' -- 'parsed', 'converted', 'processing', 'error'
                )
            ''')
            
            # Waypoint data table - lightweight waypoint info
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS zone_waypoints (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone_short_name TEXT NOT NULL,
                    waypoint_type TEXT NOT NULL, -- 'wizard', 'druid', 'zone_entry'
                    x REAL NOT NULL,
                    y REAL NOT NULL,
                    z REAL NOT NULL,
                    heading REAL DEFAULT 0.0,
                    description TEXT,
                    special_visual BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (zone_short_name) REFERENCES zone_geometry_metadata(zone_short_name)
                )
            ''')
            
            # Parsed data cache - stores only hash and basic info, not raw geometry
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS parsed_data_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone_short_name TEXT UNIQUE NOT NULL,
                    data_hash TEXT NOT NULL,                 -- Hash of parsed data for cache invalidation
                    line_segment_count INTEGER DEFAULT 0,    -- Count of line segments
                    label_count INTEGER DEFAULT 0,           -- Count of labels
                    waypoint_count INTEGER DEFAULT 0,        -- Count of waypoints
                    parse_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (zone_short_name) REFERENCES zone_geometry_metadata(zone_short_name)
                )
            ''')
            
            # Create indexes for better query performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_zone_short_name ON zone_geometry_metadata(zone_short_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_expansion_id ON zone_geometry_metadata(expansion_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_status ON zone_geometry_metadata(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_waypoints_zone ON zone_waypoints(zone_short_name)')
            
            conn.commit()
            self.logger.info("Database initialized successfully")
    
    def store_parsed_data(self, map_data: MapData, zone_long_name: str, expansion_id: int) -> bool:
        """Store parsed map data metadata in the database (not the raw geometry)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Store zone metadata
                cursor.execute('''
                    INSERT OR REPLACE INTO zone_geometry_metadata 
                    (zone_short_name, zone_long_name, expansion_id, status, version)
                    VALUES (?, ?, ?, 'parsed', '1.0')
                ''', (map_data.zone_name, zone_long_name, expansion_id))
                
                # Store waypoints (lightweight data)
                for waypoint in map_data.waypoints:
                    cursor.execute('''
                        INSERT OR REPLACE INTO zone_waypoints 
                        (zone_short_name, waypoint_type, x, y, z, description, special_visual)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        waypoint.zone_name,
                        waypoint.waypoint_type,
                        waypoint.x,
                        waypoint.y,
                        waypoint.z,
                        waypoint.description,
                        waypoint.special_visual
                    ))
                
                # Store parsed data cache info (counts and hash, not raw data)
                data_hash = self._calculate_data_hash(map_data)
                cursor.execute('''
                    INSERT OR REPLACE INTO parsed_data_cache 
                    (zone_short_name, data_hash, line_segment_count, label_count, 
                     waypoint_count)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    map_data.zone_name,
                    data_hash,
                    len(map_data.line_segments),
                    len(map_data.labels),
                    len(map_data.waypoints)
                ))
                
                conn.commit()
                self.logger.info(f"Stored metadata for {map_data.zone_name}: "
                               f"{len(map_data.line_segments)} segments, "
                               f"{len(map_data.labels)} labels, "
                               f"{len(map_data.waypoints)} waypoints")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing parsed data for {map_data.zone_name}: {e}")
            return False
    
    def store_gltf_file(self, zone_name: str, gltf_file_path: str, metadata: Dict) -> bool:
        """Store glTF file metadata in database (file itself stays in filesystem)."""
        try:
            # Ensure the glTF file exists
            if not os.path.exists(gltf_file_path):
                self.logger.error(f"glTF file not found: {gltf_file_path}")
                return False
            
            file_size = os.path.getsize(gltf_file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE zone_geometry_metadata 
                    SET status = ?, gltf_file_path = ?, file_size = ?, 
                        vertex_count = ?, triangle_count = ?,
                        bounding_box_min_x = ?, bounding_box_min_y = ?, bounding_box_min_z = ?,
                        bounding_box_max_x = ?, bounding_box_max_y = ?, bounding_box_max_z = ?
                    WHERE zone_short_name = ?
                ''', (
                    'converted', gltf_file_path, file_size,
                    metadata.get('vertex_count'), metadata.get('triangle_count'),
                    metadata.get('min_x'), metadata.get('min_y'), metadata.get('min_z'),
                    metadata.get('max_x'), metadata.get('max_y'), metadata.get('max_z'),
                    zone_name
                ))
                
                conn.commit()
                self.logger.info(f"Stored glTF metadata for {zone_name}: {file_size} bytes")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing glTF metadata for {zone_name}: {e}")
            return False
    
    def get_zone_metadata(self, zone_name: str) -> Optional[Dict]:
        """Get zone metadata from database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM zone_geometry_metadata 
                    WHERE zone_short_name = ?
                ''', (zone_name,))
                
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting metadata for {zone_name}: {e}")
            return None
    
    def get_gltf_file_path(self, zone_name: str) -> Optional[str]:
        """Get the file path to the glTF file for a zone."""
        metadata = self.get_zone_metadata(zone_name)
        if metadata and metadata.get('gltf_file_path'):
            return metadata['gltf_file_path']
        return None
    
    def get_waypoints(self, zone_name: str) -> List[Dict]:
        """Get waypoints for a zone."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM zone_waypoints 
                    WHERE zone_short_name = ?
                    ORDER BY waypoint_type, id
                ''', (zone_name,))
                
                rows = cursor.fetchall()
                if rows:
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting waypoints for {zone_name}: {e}")
            return []
    
    def get_zones_by_expansion(self, expansion_id: int) -> List[Dict]:
        """Get all zones for a specific expansion."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT zone_short_name, zone_long_name, status, 
                           vertex_count, triangle_count, file_size
                    FROM zone_geometry_metadata 
                    WHERE expansion_id = ?
                    ORDER BY zone_short_name
                ''', (expansion_id,))
                
                rows = cursor.fetchall()
                if rows:
                    columns = [description[0] for description in cursor.description]
                    return [dict(zip(columns, row)) for row in rows]
                return []
                
        except Exception as e:
            self.logger.error(f"Error getting zones for expansion {expansion_id}: {e}")
            return []
    
    def get_conversion_status(self, zone_name: str) -> Optional[str]:
        """Get the conversion status of a zone."""
        metadata = self.get_zone_metadata(zone_name)
        return metadata.get('status') if metadata else None
    
    def update_conversion_status(self, zone_name: str, status: str, gltf_path: str = None, 
                                metadata: Dict = None):
        """Update the conversion status of a zone."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if gltf_path and metadata:
                cursor.execute('''
                    UPDATE zone_geometry_metadata 
                    SET status = ?, gltf_file_path = ?, file_size = ?, 
                        vertex_count = ?, triangle_count = ?,
                        bounding_box_min_x = ?, bounding_box_min_y = ?, bounding_box_min_z = ?,
                        bounding_box_max_x = ?, bounding_box_max_y = ?, bounding_box_max_z = ?
                    WHERE zone_short_name = ?
                ''', (
                    status, gltf_path, metadata.get('file_size'),
                    metadata.get('vertex_count'), metadata.get('triangle_count'),
                    metadata.get('min_x'), metadata.get('min_y'), metadata.get('min_z'),
                    metadata.get('max_x'), metadata.get('max_y'), metadata.get('max_z'),
                    zone_name
                ))
            else:
                cursor.execute('''
                    UPDATE zone_geometry_metadata 
                    SET status = ?
                    WHERE zone_short_name = ?
                ''', (status, zone_name))
            
            conn.commit()
            self.logger.info(f"Updated status for {zone_name}: {status}")
    
    def _calculate_data_hash(self, map_data: MapData) -> str:
        """Calculate a hash of the parsed data for cache invalidation."""
        import hashlib
        
        # Create a string representation of the data counts and basic info
        data_str = f"{len(map_data.line_segments)}:{len(map_data.labels)}:{len(map_data.waypoints)}"
        
        # Add some sample data for better hash uniqueness
        if map_data.line_segments:
            sample_segment = map_data.line_segments[0]
            data_str += f":{sample_segment.x1}:{sample_segment.y1}:{sample_segment.z1}"
        
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total zones
                cursor.execute('SELECT COUNT(*) FROM zone_geometry_metadata')
                stats['total_zones'] = cursor.fetchone()[0]
                
                # Zones by status
                cursor.execute('''
                    SELECT status, COUNT(*) 
                    FROM zone_geometry_metadata 
                    GROUP BY status
                ''')
                stats['zones_by_status'] = dict(cursor.fetchall())
                
                # Total waypoints
                cursor.execute('SELECT COUNT(*) FROM zone_waypoints')
                stats['total_waypoints'] = cursor.fetchone()[0]
                
                # Total file size
                cursor.execute('SELECT SUM(file_size) FROM zone_geometry_metadata WHERE file_size IS NOT NULL')
                total_size = cursor.fetchone()[0] or 0
                stats['total_file_size_mb'] = round(total_size / (1024 * 1024), 2)
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {} 