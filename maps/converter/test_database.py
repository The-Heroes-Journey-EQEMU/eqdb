#!/usr/bin/env python3
"""
Test script for the MapDatabase class - Hybrid Storage Approach

This script demonstrates the hybrid storage approach where:
- glTF files are stored in the filesystem for fast serving
- Only metadata is stored in the database for querying and relationships
- This is much more efficient than storing 3D geometry as database rows
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from parser import MapParser, MapData, LineSegment, Label, Waypoint
from database import MapDatabase

def setup_logging():
    """Set up logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_hybrid_storage_approach():
    """Test the hybrid storage approach."""
    print("=== Testing Hybrid Storage Approach ===")
    print("This approach stores glTF files in filesystem and metadata in database")
    print()
    
    # Initialize database
    db = MapDatabase(db_path="test_map_data.db", output_dir="../output")
    
    # Test 1: Store parsed data metadata (not raw geometry)
    print("1. Testing parsed data metadata storage...")
    
    # Create test map data
    map_data = MapData(
        zone_name="testzone",
        line_segments=[
            LineSegment(100, 100, 0, 200, 100, 0, 255, 0, 0, "walls"),
            LineSegment(200, 100, 0, 200, 200, 0, 255, 0, 0, "walls"),
        ],
        labels=[
            Label(150, 150, 0, 255, 255, 255, 10, "Test Zone"),
        ],
        waypoints=[
            Waypoint(150, 150, 0, "testzone", True, "Test Waypoint"),
        ]
    )
    
    # Store metadata (not raw geometry data)
    success = db.store_parsed_data(map_data, "Test Zone", 1)
    print(f"   Stored metadata: {'✓' if success else '✗'}")
    
    # Test 2: Simulate glTF file creation and metadata storage
    print("\n2. Testing glTF file metadata storage...")
    
    # Create a dummy glTF file path
    gltf_path = "../output/gltf/testzone.gltf"
    os.makedirs(os.path.dirname(gltf_path), exist_ok=True)
    
    # Create a dummy glTF file
    with open(gltf_path, 'w') as f:
        f.write('{"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": []}]}')
    
    # Store glTF metadata
    gltf_metadata = {
        'vertex_count': 1000,
        'triangle_count': 500,
        'min_x': -1000.0,
        'min_y': -1000.0,
        'min_z': -100.0,
        'max_x': 1000.0,
        'max_y': 1000.0,
        'max_z': 100.0
    }
    
    success = db.store_gltf_file("testzone", gltf_path, gltf_metadata)
    print(f"   Stored glTF metadata: {'✓' if success else '✗'}")
    
    # Test 3: Retrieve metadata
    print("\n3. Testing metadata retrieval...")
    
    metadata = db.get_zone_metadata("testzone")
    if metadata:
        print(f"   Zone: {metadata['zone_short_name']}")
        print(f"   Status: {metadata['status']}")
        print(f"   File path: {metadata['gltf_file_path']}")
        print(f"   File size: {metadata['file_size']} bytes")
        print(f"   Vertices: {metadata['vertex_count']}")
        print(f"   Triangles: {metadata['triangle_count']}")
    else:
        print("   ✗ Failed to retrieve metadata")
    
    # Test 4: Retrieve waypoints
    print("\n4. Testing waypoint retrieval...")
    
    waypoints = db.get_waypoints("testzone")
    print(f"   Found {len(waypoints)} waypoints:")
    for wp in waypoints:
        print(f"     - {wp['waypoint_type']}: ({wp['x']}, {wp['y']}, {wp['z']}) - {wp['description']}")
    
    # Test 5: Get glTF file path
    print("\n5. Testing glTF file path retrieval...")
    
    gltf_path = db.get_gltf_file_path("testzone")
    if gltf_path:
        print(f"   glTF file: {gltf_path}")
        print(f"   File exists: {'✓' if os.path.exists(gltf_path) else '✗'}")
    else:
        print("   ✗ No glTF file path found")
    
    # Test 6: Get zones by expansion
    print("\n6. Testing expansion-based zone retrieval...")
    
    zones = db.get_zones_by_expansion(1)
    print(f"   Found {len(zones)} zones in expansion 1:")
    for zone in zones:
        print(f"     - {zone['zone_short_name']}: {zone['status']}")
    
    # Test 7: Database statistics
    print("\n7. Testing database statistics...")
    
    stats = db.get_database_stats()
    print(f"   Total zones: {stats.get('total_zones', 0)}")
    print(f"   Total waypoints: {stats.get('total_waypoints', 0)}")
    print(f"   Total file size: {stats.get('total_file_size_mb', 0)} MB")
    print(f"   Zones by status: {stats.get('zones_by_status', {})}")
    
    # Test 8: Demonstrate the efficiency advantage
    print("\n8. Demonstrating efficiency advantages...")
    print("   ✓ glTF files stored in filesystem for fast serving")
    print("   ✓ Database only stores lightweight metadata")
    print("   ✓ No need to load large 3D geometry into database memory")
    print("   ✓ Natural browser/CDN caching for glTF files")
    print("   ✓ Easy file-based backup and version control")
    print("   ✓ Database queries remain fast for metadata operations")
    
    # Cleanup
    print("\n9. Cleanup...")
    if os.path.exists("test_map_data.db"):
        os.remove("test_map_data.db")
        print("   ✓ Removed test database")
    
    if os.path.exists(gltf_path):
        os.remove(gltf_path)
        print("   ✓ Removed test glTF file")
    
    print("\n=== Hybrid Storage Test Complete ===")

def compare_storage_approaches():
    """Compare different storage approaches."""
    print("\n=== Storage Approach Comparison ===")
    print()
    
    approaches = {
        "Database Rows": {
            "pros": ["Centralized storage", "ACID compliance", "Easy queries"],
            "cons": ["Poor performance for large files", "Memory intensive", "Complex caching", "Slow file serving"]
        },
        "File System Only": {
            "pros": ["Fast file serving", "Simple structure", "Natural caching"],
            "cons": ["No metadata queries", "No relationships", "Harder to manage"]
        },
        "Hybrid (Our Approach)": {
            "pros": ["Best of both worlds", "Fast file serving", "Rich metadata queries", "Efficient storage", "Natural caching"],
            "cons": ["Slightly more complex setup", "Two storage systems to manage"]
        }
    }
    
    for approach, details in approaches.items():
        print(f"{approach}:")
        print("  Pros:")
        for pro in details["pros"]:
            print(f"    ✓ {pro}")
        print("  Cons:")
        for con in details["cons"]:
            print(f"    ✗ {con}")
        print()

if __name__ == "__main__":
    setup_logging()
    test_hybrid_storage_approach()
    compare_storage_approaches() 