#!/usr/bin/env python3
"""
Phase 2 Test Script: Complete Conversion Workflow

This script demonstrates the complete Phase 2 workflow:
1. Parse Brewall map data
2. Generate 3D geometry
3. Assign materials
4. Export to glTF format
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from parser import MapParser
from geometry import GeometryGenerator
from materials import MaterialLibrary, MaterialAssigner
from exporter import GLTFExporter

def setup_logging():
    """Set up logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_complete_phase2_workflow():
    """Test the complete Phase 2 workflow."""
    print("=== Phase 2 Complete Workflow Test ===")
    print("Testing: Parse → Geometry → Materials → glTF Export")
    print()
    
    # Step 1: Parse the overthere zone
    print("1. Parsing overthere zone...")
    parser = MapParser(verbose=False)
    
    try:
        map_data = parser.parse_zone("overthere")
        print(f"   ✓ Parsed {len(map_data.line_segments)} line segments")
        print(f"   ✓ Parsed {len(map_data.labels)} labels")
        print(f"   ✓ Parsed {len(map_data.waypoints)} waypoints")
    except Exception as e:
        print(f"   ✗ Error parsing overthere zone: {e}")
        return
    
    # Step 2: Generate 3D geometry
    print("\n2. Generating 3D geometry...")
    generator = GeometryGenerator(
        line_thickness=3.0,
        scale_factor=0.1,  # Scale down for better viewing
        verbose=True
    )
    
    meshes = generator.generate_all_geometry(map_data)
    print(f"   ✓ Generated {len(meshes)} meshes")
    
    # Optimize geometry
    optimized_meshes = generator.optimize_geometry(meshes)
    print(f"   ✓ Optimized to {len(optimized_meshes)} meshes")
    
    # Calculate bounding box
    bbox = generator.calculate_bounding_box(optimized_meshes)
    print(f"   ✓ Bounding box: X({bbox['min_x']:.1f} to {bbox['max_x']:.1f}), "
          f"Y({bbox['min_y']:.1f} to {bbox['max_y']:.1f}), "
          f"Z({bbox['min_z']:.1f} to {bbox['max_z']:.1f})")
    
    # Step 3: Set up material system
    print("\n3. Setting up material system...")
    material_library = MaterialLibrary()
    material_assigner = MaterialAssigner(material_library)
    
    print(f"   ✓ Created material library with {len(material_library.get_all_materials())} materials")
    
    # Show available material types
    material_types = {}
    for material in material_library.get_all_materials():
        mat_type = material.material_type.value
        if mat_type not in material_types:
            material_types[mat_type] = 0
        material_types[mat_type] += 1
    
    print("   Available material types:")
    for mat_type, count in material_types.items():
        print(f"     - {mat_type}: {count} materials")
    
    # Step 4: Export to glTF
    print("\n4. Exporting to glTF format...")
    exporter = GLTFExporter(verbose=True)
    
    # Create output directory
    output_dir = "../output/gltf"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = f"{output_dir}/overthere.gltf"
    
    try:
        # Export with automatic material assignment
        stats = exporter.export_with_materials(
            optimized_meshes,
            material_assigner,
            output_path,
            "overthere"
        )
        
        print(f"   ✓ Exported to {output_path}")
        print(f"   ✓ File size: {stats['file_size']:,} bytes")
        print(f"   ✓ Total vertices: {stats['total_vertices']:,}")
        print(f"   ✓ Total faces: {stats['total_faces']:,}")
        print(f"   ✓ Mesh count: {stats['mesh_count']}")
        print(f"   ✓ Material count: {stats['material_count']}")
        
    except Exception as e:
        print(f"   ✗ Error exporting glTF: {e}")
        return
    
    # Step 5: Export with waypoint metadata
    print("\n5. Adding waypoint metadata...")
    
    try:
        # Create waypoint metadata
        waypoint_metadata = exporter.create_waypoint_metadata(map_data.waypoints)
        
        # Export with extras
        extras = {
            "zone_info": {
                "name": "overthere",
                "long_name": "The Overthere",
                "expansion": "Kunark"
            },
            "waypoints": waypoint_metadata,
            "conversion_info": {
                "version": "1.0",
                "generator": "EQDB Map Converter",
                "scale_factor": generator.scale_factor,
                "line_thickness": generator.line_thickness
            }
        }
        
        metadata_path = f"{output_dir}/overthere_with_metadata.gltf"
        stats_with_metadata = exporter.export_with_extras(
            optimized_meshes,
            material_assigner.library.get_all_materials(),
            metadata_path,
            "overthere",
            extras
        )
        
        print(f"   ✓ Exported with metadata to {metadata_path}")
        print(f"   ✓ Added {len(extras)} extra fields")
        print(f"   ✓ Waypoint count: {waypoint_metadata['waypoint_count']}")
        
    except Exception as e:
        print(f"   ✗ Error adding metadata: {e}")
    
    # Step 6: Validate glTF files
    print("\n6. Validating glTF files...")
    
    try:
        import json
        
        # Check basic glTF structure
        with open(output_path, 'r') as f:
            gltf_data = json.load(f)
        
        required_fields = ['asset', 'scene', 'scenes', 'nodes', 'meshes']
        for field in required_fields:
            if field in gltf_data:
                print(f"   ✓ {field}: present")
            else:
                print(f"   ✗ {field}: missing")
        
        # Check asset info
        asset = gltf_data.get('asset', {})
        print(f"   ✓ Generator: {asset.get('generator', 'unknown')}")
        print(f"   ✓ Version: {asset.get('version', 'unknown')}")
        
        # Check scene structure
        scenes = gltf_data.get('scenes', [])
        if scenes:
            scene = scenes[0]
            nodes = scene.get('nodes', [])
            print(f"   ✓ Scene nodes: {len(nodes)}")
        
        # Check mesh count
        meshes = gltf_data.get('meshes', [])
        print(f"   ✓ glTF meshes: {len(meshes)}")
        
        # Check material count
        materials = gltf_data.get('materials', [])
        print(f"   ✓ glTF materials: {len(materials)}")
        
    except Exception as e:
        print(f"   ✗ Error validating glTF: {e}")
    
    print("\n=== Phase 2 Workflow Test Complete ===")
    print(f"Generated files:")
    print(f"  - {output_path}")
    print(f"  - {metadata_path}")
    print()
    print("Next steps:")
    print("  - Test glTF files in Babylon.js viewer")
    print("  - Move to Phase 3: Proof of Concept")
    print("  - Create Babylon.js integration")

def test_material_assignment():
    """Test material assignment functionality."""
    print("\n=== Material Assignment Test ===")
    
    # Create material library and assigner
    library = MaterialLibrary()
    assigner = MaterialAssigner(library)
    
    # Test line material assignment
    print("1. Testing line material assignment...")
    
    test_colors = [
        ((255, 0, 0), "red line"),
        ((0, 255, 0), "green line"),
        ((0, 0, 255), "blue line"),
        ((128, 128, 128), "gray line")
    ]
    
    for color, description in test_colors:
        material = assigner.assign_material_to_line(color)
        print(f"   {description}: {material.name}")
    
    # Test special line types
    print("\n2. Testing special line types...")
    
    water_material = assigner.assign_material_to_line((0, 100, 200), "water")
    air_material = assigner.assign_material_to_line((200, 200, 255), "air")
    ui_material = assigner.assign_material_to_line((255, 255, 0), "ui")
    
    print(f"   Water: {water_material.name}")
    print(f"   Air: {air_material.name}")
    print(f"   UI: {ui_material.name}")
    
    # Test waypoint material assignment
    print("\n3. Testing waypoint material assignment...")
    
    wizard_material = assigner.assign_material_to_waypoint("wizard", True)
    druid_material = assigner.assign_material_to_waypoint("druid", True)
    general_material = assigner.assign_material_to_waypoint("waypoint", True)
    
    print(f"   Wizard: {wizard_material.name}")
    print(f"   Druid: {druid_material.name}")
    print(f"   General: {general_material.name}")
    
    # Test label material assignment
    print("\n4. Testing label material assignment...")
    
    small_label = assigner.assign_material_to_label((255, 255, 255), 10)
    large_label = assigner.assign_material_to_label((255, 255, 255), 20)
    
    print(f"   Small label: {small_label.name}")
    print(f"   Large label: {large_label.name}")
    
    print("   ✓ Material assignment test complete")

if __name__ == "__main__":
    setup_logging()
    test_complete_phase2_workflow()
    test_material_assignment() 