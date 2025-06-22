#!/usr/bin/env python3
"""
Test script for Coordinate System Validation (Phase 2.6+)

This script demonstrates:
- Coordinate range validation
- Outlier and zero-length detection
- Consistency checks
- Transformation suggestions for Babylon.js
"""

import logging
from parser import MapData, LineSegment, Label, Waypoint
from coordinate_validator import CoordinateValidator, CoordinateSystem
from error_handler import ErrorHandler, PerformanceMonitor, ProcessingStage

def create_sample_map_data():
    """Create sample map data with a variety of coordinates, including outliers and zero-length segments."""
    return MapData(
        zone_name="testzone_coords",
        line_segments=[
            LineSegment(0, 0, 0, 100, 0, 0, 255, 255, 255, "walls"),
            LineSegment(0, 0, 0, 0, 100, 0, 255, 255, 255, "walls"),
            LineSegment(100, 0, 0, 100, 100, 0, 255, 255, 255, "walls"),
            LineSegment(0, 100, 0, 100, 100, 0, 255, 255, 255, "walls"),
            LineSegment(0, 0, 0, 0, 0, 0, 255, 0, 0, "walls"),  # Zero-length
            LineSegment(9999, 9999, 9999, 10000, 10000, 10000, 255, 0, 0, "walls"),  # Outlier
        ],
        labels=[
            Label(50, 50, 10, 255, 255, 0, 12, "Center Label"),
            Label(-5000, -5000, -500, 0, 255, 0, 10, "Far Label"),  # Outlier
        ],
        waypoints=[
            Waypoint(50, 50, 0, "testzone_coords", "waypoint", True, "Main Waypoint"),
            Waypoint(10000, 10000, 10000, "testzone_coords", "wizard", True, "Wizard Outlier"),  # Outlier
        ]
    )

def test_coordinate_validation():
    print("=== Coordinate System Validation Test ===")
    error_handler = ErrorHandler(verbose=True)
    perf_monitor = PerformanceMonitor(verbose=True)
    from parser import MapParser
    parser = MapParser(verbose=False)
    map_data = None
    with perf_monitor.monitor_stage(ProcessingStage.PARSING):
        try:
            map_data = parser.parse_zone("overthere")
            print(f"   ✓ Parsed {len(map_data.line_segments)} line segments")
        except Exception as e:
            error_handler.handle_error(ProcessingStage.PARSING, f"Error parsing overthere: {e}", exception=e)
            print(f"   ✗ Error parsing overthere: {e}")
            return
    validator = CoordinateValidator(verbose=True)
    with perf_monitor.monitor_stage(ProcessingStage.VALIDATION):
        try:
            result = validator.validate_map_data(map_data)
            print(f"   ✓ Validation complete. Outliers: {len(result.outliers)}")
            print(f"   ✓ Coordinate range: {result.coordinate_range}")
        except Exception as e:
            error_handler.handle_error(ProcessingStage.VALIDATION, f"Error validating overthere: {e}", exception=e)
            print(f"   ✗ Error validating overthere: {e}")
            return
    print("\nError Summary:")
    print(error_handler.get_error_summary())
    print("\nPerformance Summary:")
    print(perf_monitor.get_performance_summary())

def test_zone(zone_name, expansion=None):
    print(f"\n=== Coordinate Validation for {zone_name} ===")
    error_handler = ErrorHandler(verbose=True)
    perf_monitor = PerformanceMonitor(verbose=True)
    from parser import MapParser
    parser = MapParser(verbose=False)
    map_data = None
    with perf_monitor.monitor_stage(ProcessingStage.PARSING):
        try:
            map_data = parser.parse_zone(zone_name)
            print(f"   ✓ Parsed {len(map_data.line_segments)} line segments")
        except Exception as e:
            error_handler.handle_error(ProcessingStage.PARSING, f"Error parsing {zone_name}: {e}", exception=e)
            print(f"   ✗ Error parsing {zone_name}: {e}")
            return
    validator = CoordinateValidator(verbose=True)
    with perf_monitor.monitor_stage(ProcessingStage.VALIDATION):
        try:
            result = validator.validate_map_data(map_data)
            print(f"   ✓ Validation complete. Outliers: {len(result.outliers)}")
            print(f"   ✓ Coordinate range: {result.coordinate_range}")
        except Exception as e:
            error_handler.handle_error(ProcessingStage.VALIDATION, f"Error validating {zone_name}: {e}", exception=e)
            print(f"   ✗ Error validating {zone_name}: {e}")
            return
    print("\nError Summary:")
    print(error_handler.get_error_summary())
    print("\nPerformance Summary:")
    print(perf_monitor.get_performance_summary())

if __name__ == "__main__":
    test_coordinate_validation()
    test_zone("kattacastrum", expansion="pop")
    test_zone("iceclad", expansion="velious") 