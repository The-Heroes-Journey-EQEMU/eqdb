#!/usr/bin/env python3
"""
Test script for the MapParser to see what it produces.
This will parse the overthere zone and show the output structure.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from parser import MapParser

def test_parser():
    """Test the parser with the overthere zone."""
    print("=== Testing MapParser with 'overthere' zone ===\n")
    
    # Initialize parser
    parser = MapParser(verbose=True)
    
    # Parse the overthere zone
    zone_name = "overthere"
    map_data = parser.parse_zone(zone_name)
    
    # Display results
    print(f"Zone: {map_data.zone_name}")
    print(f"Line segments: {len(map_data.line_segments)}")
    print(f"Labels: {len(map_data.labels)}")
    print(f"Secondary segments: {len(map_data.secondary_segments)}")
    print(f"Waypoints: {len(map_data.waypoints)}")
    
    # Show first few examples of each type
    if map_data.line_segments:
        print(f"\n=== First 3 Line Segments ===")
        for i, segment in enumerate(map_data.line_segments[:3]):
            print(f"  {i+1}. ({segment.x1:.1f}, {segment.y1:.1f}, {segment.z1:.1f}) -> "
                  f"({segment.x2:.1f}, {segment.y2:.1f}, {segment.z2:.1f}) "
                  f"RGB({segment.r}, {segment.g}, {segment.b})")
    
    if map_data.labels:
        print(f"\n=== First 3 Labels ===")
        for i, label in enumerate(map_data.labels[:3]):
            print(f"  {i+1}. ({label.x:.1f}, {label.y:.1f}, {label.z:.1f}) "
                  f"RGB({label.r}, {label.g}, {label.b}) "
                  f"Size: {label.size} Text: '{label.text}'")
    
    if map_data.secondary_segments:
        print(f"\n=== First 3 Secondary Segments ===")
        for i, segment in enumerate(map_data.secondary_segments[:3]):
            print(f"  {i+1}. ({segment.x1:.1f}, {segment.y1:.1f}, {segment.z1:.1f}) -> "
                  f"({segment.x2:.1f}, {segment.y2:.1f}, {segment.z2:.1f}) "
                  f"RGB({segment.r}, {segment.g}, {segment.b})")
    
    if map_data.waypoints:
        print(f"\n=== Waypoints ===")
        for i, waypoint in enumerate(map_data.waypoints):
            print(f"  {i+1}. ({waypoint.x:.1f}, {waypoint.y:.1f}, {waypoint.z:.1f}) "
                  f"Type: {waypoint.waypoint_type} "
                  f"Description: {waypoint.description}")
    
    # Show coordinate ranges
    print(f"\n=== Coordinate Analysis ===")
    all_coords = []
    for segment in map_data.line_segments:
        all_coords.extend([segment.x1, segment.y1, segment.z1, segment.x2, segment.y2, segment.z2])
    for label in map_data.labels:
        all_coords.extend([label.x, label.y, label.z])
    for waypoint in map_data.waypoints:
        all_coords.extend([waypoint.x, waypoint.y, waypoint.z])
    
    if all_coords:
        min_x, min_y, min_z = min(all_coords[::3]), min(all_coords[1::3]), min(all_coords[2::3])
        max_x, max_y, max_z = max(all_coords[::3]), max(all_coords[1::3]), max(all_coords[2::3])
        print(f"  X range: {min_x:.1f} to {max_x:.1f} (span: {max_x - min_x:.1f})")
        print(f"  Y range: {min_y:.1f} to {max_y:.1f} (span: {max_y - min_y:.1f})")
        print(f"  Z range: {min_z:.1f} to {max_z:.1f} (span: {max_z - min_z:.1f})")
    
    # Show color analysis
    print(f"\n=== Color Analysis ===")
    colors = set()
    for segment in map_data.line_segments:
        colors.add((segment.r, segment.g, segment.b))
    for label in map_data.labels:
        colors.add((label.r, label.g, label.b))
    
    print(f"  Unique colors found: {len(colors)}")
    print(f"  Sample colors: {list(colors)[:5]}")
    
    return map_data

if __name__ == "__main__":
    test_parser() 