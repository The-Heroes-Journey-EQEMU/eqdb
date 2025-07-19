#!/usr/bin/env python3
"""
Test script for Phase 2.6: Enhanced Label System Implementation

This script tests the enhanced label system with:
- Proper 3D text rendering and billboarding
- Label classification and visual treatment
- Material assignment by semantic layer
- Enhanced waypoint visualization
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path

# Add the converter directory to the path
sys.path.append(os.path.dirname(__file__))

from parser import MapParser, MapData, LineSegment, Label, Waypoint
from geometry import GeometryGenerator
from materials import MaterialLibrary, MaterialAssigner
from exporter import GLTFExporter
from database import MapDatabase

def create_test_data() -> MapData:
    """Create comprehensive test data with various label types."""
    
    # Create test map data
    map_data = MapData(zone_name="testzone_enhanced_labels")
    
    # Add some line segments for context
    map_data.line_segments = [
        LineSegment(0, 0, 0, 100, 0, 0, 255, 255, 255, "walls"),
        LineSegment(0, 0, 0, 0, 100, 0, 255, 255, 255, "walls"),
        LineSegment(100, 0, 0, 100, 100, 0, 255, 255, 255, "walls"),
        LineSegment(0, 100, 0, 100, 100, 0, 255, 255, 255, "walls"),
    ]
    
    # Add various types of labels
    map_data.labels = [
        # Waypoint labels
        Label(50, 50, 10, 255, 0, 0, 12, "WAYPOINT"),
        Label(25, 25, 5, 255, 0, 0, 10, "Bind Point"),
        Label(75, 75, 8, 255, 0, 0, 8, "Safe Spot"),
        
        # Zone labels
        Label(50, 0, 15, 0, 128, 255, 15, "ZONE_ENTRANCE"),
        Label(0, 50, 12, 0, 128, 255, 14, "Temple of Marr"),
        Label(100, 50, 13, 0, 128, 255, 16, "Plane of Air"),
        
        # NPC labels
        Label(25, 75, 6, 0, 255, 0, 9, "Lord Nagafen"),
        Label(75, 25, 7, 0, 255, 0, 11, "Merchant Smith"),
        Label(50, 25, 5, 0, 255, 0, 8, "Guard Captain"),
        
        # Item labels
        Label(25, 50, 4, 255, 255, 0, 7, '"Sword of Truth"'),
        Label(75, 50, 3, 255, 255, 0, 6, '"Potion of Healing"'),
        Label(50, 75, 5, 255, 255, 0, 8, '"Magic Ring"'),
        
        # General labels
        Label(10, 10, 2, 128, 128, 128, 5, "General Note"),
        Label(90, 90, 3, 128, 128, 128, 6, "Another Note"),
    ]
    
    # Add waypoints
    map_data.waypoints = [
        Waypoint(50, 50, 0, "testzone_enhanced_labels", "waypoint", True, "Main Waypoint"),
        Waypoint(25, 25, 0, "testzone_enhanced_labels", "wizard", True, "Wizard Portal"),
        Waypoint(75, 75, 0, "testzone_enhanced_labels", "druid", True, "Druid Portal"),
    ]
    
    return map_data

def test_enhanced_label_system():
    """Test the enhanced label system."""
    
    print("🧪 Testing Enhanced Label System (Phase 2.6)")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # Create test data
    print("\n📝 Creating test data with various label types...")
    map_data = create_test_data()
    
    print(f"  - Line segments: {len(map_data.line_segments)}")
    print(f"  - Labels: {len(map_data.labels)}")
    print(f"  - Waypoints: {len(map_data.waypoints)}")
    
    # Initialize components
    print("\n🔧 Initializing components...")
    geometry_generator = GeometryGenerator(verbose=True)
    material_library = MaterialLibrary()
    material_assigner = MaterialAssigner(material_library)
    exporter = GLTFExporter(verbose=True)
    
    # Generate geometry
    print("\n🎨 Generating 3D geometry...")
    meshes = geometry_generator.generate_all_geometry(map_data)
    
    print(f"  - Generated {len(meshes)} meshes")
    
    # Analyze mesh types
    mesh_types = {}
    for mesh in meshes:
        mesh_type = mesh.mesh_type
        if mesh_type not in mesh_types:
            mesh_types[mesh_type] = 0
        mesh_types[mesh_type] += 1
    
    print("  - Mesh type breakdown:")
    for mesh_type, count in mesh_types.items():
        print(f"    * {mesh_type}: {count}")
    
    # Analyze label semantic layers
    label_layers = {}
    for mesh in meshes:
        if mesh.mesh_type == "label" and mesh.semantic_layer:
            layer = mesh.semantic_layer
            if layer not in label_layers:
                label_layers[layer] = 0
            label_layers[layer] += 1
    
    print("  - Label semantic layers:")
    for layer, count in label_layers.items():
        print(f"    * {layer}: {count}")
    
    # Assign materials
    print("\n🎨 Assigning materials...")
    for mesh in meshes:
        if mesh.semantic_layer:
            material = material_assigner.assign_material_by_semantic_layer(mesh.semantic_layer)
            print(f"  - {mesh.name}: {material.name} (type: {material.material_type.value})")
    
    # Optimize geometry
    print("\n⚡ Optimizing geometry...")
    optimized_meshes = geometry_generator.optimize_geometry(meshes)
    print(f"  - Optimized from {len(meshes)} to {len(optimized_meshes)} meshes")
    
    # Calculate bounding box
    print("\n📐 Calculating bounding box...")
    bbox = geometry_generator.calculate_bounding_box(optimized_meshes)
    print(f"  - Bounding box: {bbox}")
    
    # Export to glTF
    print("\n📦 Exporting to glTF...")
    output_dir = tempfile.mkdtemp()
    gltf_path = os.path.join(output_dir, "testzone_enhanced_labels.gltf")
    
    try:
        # Export with automatic material assignment (no metadata in glTF file)
        stats = exporter.export_with_materials(
            optimized_meshes,
            material_assigner,
            gltf_path,
            map_data.zone_name
        )
        
        # Verify the file was created
        if os.path.exists(gltf_path):
            file_size = os.path.getsize(gltf_path)
            print(f"  ✅ glTF file created: {gltf_path}")
            print(f"  📊 File size: {file_size:,} bytes")
            
            # Validate glTF structure
            import json
            with open(gltf_path, 'r') as f:
                gltf_data = json.load(f)
            
            print(f"  📋 glTF structure:")
            print(f"    * Meshes: {len(gltf_data.get('meshes', []))}")
            print(f"    * Materials: {len(gltf_data.get('materials', []))}")
            print(f"    * Nodes: {len(gltf_data.get('nodes', []))}")
            print(f"    * Scenes: {len(gltf_data.get('scenes', []))}")
            
        else:
            print(f"  ❌ glTF file not created")
            return False
            
    except Exception as e:
        print(f"  ❌ Export failed: {e}")
        return False
    
    # Test database storage with comprehensive metadata
    print("\n💾 Testing database storage with comprehensive metadata...")
    db_path = os.path.join(output_dir, "test_phase2_6.db")
    database = MapDatabase(db_path)
    
    try:
        # Store parsed data metadata
        database.store_parsed_data(map_data, "Test Zone Enhanced Labels", 0)  # expansion_id 0 for Classic
        print("  ✅ Parsed data metadata stored")
        
        # Prepare comprehensive metadata for database storage
        bbox = geometry_generator.calculate_bounding_box(optimized_meshes)
        comprehensive_metadata = {
            # Geometry statistics
            'vertex_count': sum(len(mesh.vertices) for mesh in optimized_meshes),
            'triangle_count': sum(len(mesh.faces) for mesh in optimized_meshes),
            
            # Bounding box
            'min_x': bbox['min_x'],
            'min_y': bbox['min_y'], 
            'min_z': bbox['min_z'],
            'max_x': bbox['max_x'],
            'max_y': bbox['max_y'],
            'max_z': bbox['max_z'],
            
            # Layer and categorization information
            'enhanced_labels': True,
            'label_types': list(label_layers.keys()),
            'mesh_count': len(optimized_meshes),
            'semantic_layers_present': list(set(mesh.semantic_layer for mesh in optimized_meshes if mesh.semantic_layer)),
            
            # Export statistics
            'file_size': os.path.getsize(gltf_path),
            'export_stats': stats
        }
        
        # Store glTF file metadata
        database.store_gltf_file(
            zone_name=map_data.zone_name,
            gltf_file_path=gltf_path,
            metadata=comprehensive_metadata
        )
        print("  ✅ Comprehensive glTF metadata stored")
        
        # Verify waypoints are properly categorized
        print("\n🎯 Verifying waypoint and POI categorization...")
        waypoints = database.get_waypoints(map_data.zone_name)
        print(f"  - Found {len(waypoints)} waypoints in database:")
        for wp in waypoints:
            print(f"    * {wp['waypoint_type']}: ({wp['x']}, {wp['y']}, {wp['z']}) - {wp['description']}")
        
        # Query stored data
        stored_data = database.get_zone_metadata(map_data.zone_name)
        if stored_data:
            print(f"  ✅ Retrieved zone metadata:")
            print(f"    * Zone: {stored_data['zone_short_name']}")
            print(f"    * Status: {stored_data['status']}")
            print(f"    * File path: {stored_data['gltf_file_path']}")
            print(f"    * File size: {stored_data['file_size']:,} bytes")
            print(f"    * Vertices: {stored_data['vertex_count']:,}")
            print(f"    * Triangles: {stored_data['triangle_count']:,}")
        else:
            print("  ❌ Failed to retrieve zone metadata")
            
        # Verify layer categorization for visibility control
        print("\n🎨 Verifying layer categorization for visibility control...")
        print("  - Semantic layers present in geometry:")
        for mesh in optimized_meshes:
            if mesh.semantic_layer:
                print(f"    * {mesh.name}: {mesh.semantic_layer} ({mesh.mesh_type})")
        
        print("  - Layer types available for visibility control:")
        layer_types = set()
        for mesh in optimized_meshes:
            if mesh.semantic_layer:
                layer_types.add(mesh.semantic_layer)
            layer_types.add(mesh.mesh_type)
        
        for layer_type in sorted(layer_types):
            print(f"    * {layer_type}")
            
    except Exception as e:
        print(f"  ❌ Database operation failed: {e}")
        return False
    
    # Cleanup
    print(f"\n🧹 Cleaning up temporary files...")
    shutil.rmtree(output_dir)
    print("  ✅ Cleanup complete")
    
    print("\n🎉 Enhanced Label System Test Complete!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_enhanced_label_system()
    sys.exit(0 if success else 1) 