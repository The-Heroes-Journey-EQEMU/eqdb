#!/usr/bin/env python3
"""
Test script for the GeometryGenerator class

This script demonstrates the conversion of parsed map data into 3D geometry
meshes suitable for glTF export.
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent))

from parser import MapParser
from geometry import GeometryGenerator, MeshData

def setup_logging():
    """Set up logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_geometry_generation():
    """Test the geometry generation functionality."""
    print("=== Testing Geometry Generation ===")
    print()
    
    # Initialize parser and parse overthere zone
    parser = MapParser(verbose=False)
    print("1. Parsing overthere zone...")
    
    try:
        map_data = parser.parse_zone("overthere")
        print(f"   ✓ Parsed {len(map_data.line_segments)} line segments")
        print(f"   ✓ Parsed {len(map_data.labels)} labels")
        print(f"   ✓ Parsed {len(map_data.waypoints)} waypoints")
        print(f"   ✓ Parsed {len(map_data.secondary_segments)} secondary segments")
    except Exception as e:
        print(f"   ✗ Error parsing overthere zone: {e}")
        return
    
    # Initialize geometry generator
    print("\n2. Initializing geometry generator...")
    generator = GeometryGenerator(
        line_thickness=3.0,
        scale_factor=0.1,  # Scale down for better viewing
        offset_x=0.0,
        offset_y=0.0,
        offset_z=0.0,
        verbose=True
    )
    print("   ✓ Geometry generator initialized")
    
    # Generate all geometry
    print("\n3. Generating 3D geometry...")
    meshes = generator.generate_all_geometry(map_data)
    print(f"   ✓ Generated {len(meshes)} meshes")
    
    # Analyze mesh types
    mesh_types = {}
    total_vertices = 0
    total_faces = 0
    
    for mesh in meshes:
        mesh_type = mesh.mesh_type
        if mesh_type not in mesh_types:
            mesh_types[mesh_type] = 0
        mesh_types[mesh_type] += 1
        
        total_vertices += len(mesh.vertices)
        total_faces += len(mesh.faces)
    
    print(f"   Mesh breakdown:")
    for mesh_type, count in mesh_types.items():
        print(f"     - {mesh_type}: {count} meshes")
    
    print(f"   Total vertices: {total_vertices:,}")
    print(f"   Total faces: {total_faces:,}")
    
    # Test coordinate transformation
    print("\n4. Testing coordinate transformation...")
    original_coords = (1000.0, 2000.0, 100.0)
    transformed = generator.transform_coordinates(*original_coords)
    print(f"   Original: {original_coords}")
    print(f"   Transformed: {transformed}")
    print(f"   Scale factor applied: {transformed[0] / original_coords[0]:.3f}")
    
    # Test individual mesh generation
    print("\n5. Testing individual mesh generation...")
    
    if map_data.line_segments:
        line_mesh = generator.generate_line_mesh(map_data.line_segments[0])
        if line_mesh:
            print(f"   ✓ Line mesh: {len(line_mesh.vertices)} vertices, {len(line_mesh.faces)} faces")
            print(f"     Color: {line_mesh.colors[0]}")
    
    if map_data.labels:
        label_mesh = generator.generate_label_mesh(map_data.labels[0])
        if label_mesh:
            print(f"   ✓ Label mesh: {len(label_mesh.vertices)} vertices, {len(label_mesh.faces)} faces")
            print(f"     Text: {map_data.labels[0].text}")
    
    if map_data.waypoints:
        waypoint_mesh = generator.generate_waypoint_mesh(map_data.waypoints[0])
        if waypoint_mesh:
            print(f"   ✓ Waypoint mesh: {len(waypoint_mesh.vertices)} vertices, {len(waypoint_mesh.faces)} faces")
            print(f"     Special visual: {map_data.waypoints[0].special_visual}")
    
    # Test geometry optimization
    print("\n6. Testing geometry optimization...")
    optimized_meshes = generator.optimize_geometry(meshes)
    print(f"   Original meshes: {len(meshes)}")
    print(f"   Optimized meshes: {len(optimized_meshes)}")
    
    if len(optimized_meshes) < len(meshes):
        print(f"   ✓ Optimization reduced mesh count by {len(meshes) - len(optimized_meshes)}")
    else:
        print("   - No optimization possible (all meshes are unique)")
    
    # Calculate bounding box
    print("\n7. Calculating bounding box...")
    bbox = generator.calculate_bounding_box(meshes)
    print(f"   Bounding box:")
    print(f"     X: {bbox['min_x']:.1f} to {bbox['max_x']:.1f}")
    print(f"     Y: {bbox['min_y']:.1f} to {bbox['max_y']:.1f}")
    print(f"     Z: {bbox['min_z']:.1f} to {bbox['max_z']:.1f}")
    
    # Test with different parameters
    print("\n8. Testing with different parameters...")
    
    # Test with thicker lines
    thick_generator = GeometryGenerator(
        line_thickness=10.0,
        scale_factor=0.1,
        verbose=False
    )
    thick_meshes = thick_generator.generate_all_geometry(map_data)
    print(f"   Thick lines: {len(thick_meshes)} meshes")
    
    # Test with different scale
    scaled_generator = GeometryGenerator(
        line_thickness=3.0,
        scale_factor=0.05,  # Smaller scale
        verbose=False
    )
    scaled_meshes = scaled_generator.generate_all_geometry(map_data)
    print(f"   Smaller scale: {len(scaled_meshes)} meshes")
    
    # Test with offset
    offset_generator = GeometryGenerator(
        line_thickness=3.0,
        scale_factor=0.1,
        offset_x=1000.0,
        offset_y=1000.0,
        offset_z=0.0,
        verbose=False
    )
    offset_meshes = offset_generator.generate_all_geometry(map_data)
    print(f"   With offset: {len(offset_meshes)} meshes")
    
    print("\n=== Geometry Generation Test Complete ===")

def test_mesh_data_structure():
    """Test the MeshData structure and basic operations."""
    print("\n=== Testing MeshData Structure ===")
    
    import numpy as np
    
    # Create sample mesh data
    vertices = np.array([
        [0, 0, 0],
        [1, 0, 0],
        [1, 1, 0],
        [0, 1, 0]
    ])
    
    faces = np.array([
        [0, 1, 2],
        [0, 2, 3]
    ])
    
    colors = np.array([
        [1.0, 0.0, 0.0],  # Red
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 0.0, 0.0]
    ])
    
    mesh = MeshData(
        vertices=vertices,
        faces=faces,
        colors=colors,
        name="test_mesh",
        mesh_type="test"
    )
    
    print(f"   Mesh name: {mesh.name}")
    print(f"   Mesh type: {mesh.mesh_type}")
    print(f"   Vertices: {len(mesh.vertices)}")
    print(f"   Faces: {len(mesh.faces)}")
    print(f"   Colors: {len(mesh.colors)}")
    print(f"   Vertex shape: {mesh.vertices.shape}")
    print(f"   Face shape: {mesh.faces.shape}")
    print(f"   Color shape: {mesh.colors.shape}")
    
    print("   ✓ MeshData structure test complete")

if __name__ == "__main__":
    setup_logging()
    test_geometry_generation()
    test_mesh_data_structure() 