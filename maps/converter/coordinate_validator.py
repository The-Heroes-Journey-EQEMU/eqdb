#!/usr/bin/env python3
"""
Coordinate System Validator for Map Conversion

This module handles coordinate system validation, consistency checks,
and coordinate system differences between Brewall and Babylon.js.
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass
from enum import Enum

from parser import MapData, LineSegment, Label, Waypoint

class CoordinateSystem(Enum):
    """Different coordinate systems used in the project."""
    BREWALL = "brewall"      # Original Brewall format
    BABYLON_JS = "babylon"   # Babylon.js 3D coordinate system
    NORMALIZED = "normalized" # Normalized for optimal viewing

@dataclass
class CoordinateRange:
    """Defines valid coordinate ranges for different systems."""
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    min_z: float
    max_z: float
    
    def contains(self, x: float, y: float, z: float) -> bool:
        """Check if coordinates are within this range."""
        return (self.min_x <= x <= self.max_x and
                self.min_y <= y <= self.max_y and
                self.min_z <= z <= self.max_z)
    
    def get_center(self) -> Tuple[float, float, float]:
        """Get the center point of this range."""
        return (
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2,
            (self.min_z + self.max_z) / 2
        )
    
    def get_size(self) -> Tuple[float, float, float]:
        """Get the size of this range."""
        return (
            self.max_x - self.min_x,
            self.max_y - self.min_y,
            self.max_z - self.min_z
        )

@dataclass
class CoordinateValidationResult:
    """Result of coordinate validation."""
    is_valid: bool
    issues: List[str]
    coordinate_range: Optional[CoordinateRange] = None
    outliers: List[Tuple[float, float, float]] = None
    recommendations: List[str] = None

class CoordinateValidator:
    """Validates and analyzes coordinate systems for map data."""
    
    # Known coordinate ranges for different game expansions
    BREWALL_COORDINATE_RANGES = {
        "classic": CoordinateRange(-3000, 3000, -3000, 3000, -1000, 1000),
        "kunark": CoordinateRange(-4000, 4000, -4000, 4000, -1500, 1500),
        "velious": CoordinateRange(-5000, 5000, -5000, 5000, -2000, 2000),
        "luclin": CoordinateRange(-6000, 6000, -6000, 6000, -2500, 2500),
        "pop": CoordinateRange(-7000, 7000, -7000, 7000, -3000, 3000),
        "default": CoordinateRange(-10000, 10000, -10000, 10000, -5000, 5000)
    }
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the coordinate validator.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
    
    def validate_map_data(self, map_data: MapData, expansion: str = "default") -> CoordinateValidationResult:
        """
        Validate coordinate data for a complete map.
        
        Args:
            map_data: Map data to validate
            expansion: Game expansion for coordinate range validation
            
        Returns:
            Validation result with issues and recommendations
        """
        issues = []
        outliers = []
        recommendations = []
        
        # Get expected coordinate range for this expansion
        expected_range = self.BREWALL_COORDINATE_RANGES.get(expansion, self.BREWALL_COORDINATE_RANGES["default"])
        
        # Collect all coordinates
        all_coordinates = []
        
        # Validate line segments
        for segment in map_data.line_segments:
            coords = [(segment.x1, segment.y1, segment.z1), (segment.x2, segment.y2, segment.z2)]
            all_coordinates.extend(coords)
            
            # Check for zero-length segments
            if self._is_zero_length(segment):
                issues.append(f"Zero-length line segment: ({segment.x1}, {segment.y1}, {segment.z1}) to ({segment.x2}, {segment.y2}, {segment.z2})")
            
            # Check for outliers
            for x, y, z in coords:
                if not expected_range.contains(x, y, z):
                    outliers.append((x, y, z))
                    issues.append(f"Outlier coordinate in line segment: ({x}, {y}, {z})")
        
        # Validate labels
        for label in map_data.labels:
            coords = (label.x, label.y, label.z)
            all_coordinates.append(coords)
            
            if not expected_range.contains(*coords):
                outliers.append(coords)
                issues.append(f"Outlier coordinate in label '{label.text}': ({label.x}, {label.y}, {label.z})")
        
        # Validate waypoints
        for waypoint in map_data.waypoints:
            coords = (waypoint.x, waypoint.y, waypoint.z)
            all_coordinates.append(coords)
            
            if not expected_range.contains(*coords):
                outliers.append(coords)
                issues.append(f"Outlier coordinate in waypoint: ({waypoint.x}, {waypoint.y}, {waypoint.z})")
        
        # Calculate actual coordinate range
        if all_coordinates:
            coords_array = np.array(all_coordinates)
            actual_range = CoordinateRange(
                min_x=float(np.min(coords_array[:, 0])),
                max_x=float(np.max(coords_array[:, 0])),
                min_y=float(np.min(coords_array[:, 1])),
                max_y=float(np.max(coords_array[:, 1])),
                min_z=float(np.min(coords_array[:, 2])),
                max_z=float(np.max(coords_array[:, 2]))
            )
        else:
            actual_range = None
            issues.append("No coordinates found in map data")
        
        # Analyze coordinate distribution
        if actual_range:
            self._analyze_coordinate_distribution(actual_range, expected_range, recommendations)
        
        # Check for coordinate system consistency
        consistency_issues = self._check_coordinate_consistency(map_data)
        issues.extend(consistency_issues)
        
        # Generate recommendations
        if outliers:
            recommendations.append(f"Found {len(outliers)} outlier coordinates - consider coordinate system transformation")
        
        if actual_range and expected_range:
            size_diff = self._compare_ranges(actual_range, expected_range)
            if size_diff > 0.5:  # More than 50% difference
                recommendations.append(f"Coordinate range is {size_diff:.1%} different from expected - may need scaling")
        
        is_valid = len(issues) == 0
        
        return CoordinateValidationResult(
            is_valid=is_valid,
            issues=issues,
            coordinate_range=actual_range,
            outliers=outliers,
            recommendations=recommendations
        )
    
    def _is_zero_length(self, segment: LineSegment) -> bool:
        """Check if a line segment has zero length."""
        dx = segment.x2 - segment.x1
        dy = segment.y2 - segment.y1
        dz = segment.z2 - segment.z1
        length = np.sqrt(dx*dx + dy*dy + dz*dz)
        return length < 0.001  # Very small threshold
    
    def _analyze_coordinate_distribution(self, actual_range: CoordinateRange, 
                                       expected_range: CoordinateRange, 
                                       recommendations: List[str]):
        """Analyze coordinate distribution and provide recommendations."""
        actual_size = actual_range.get_size()
        expected_size = expected_range.get_size()
        
        # Check if coordinates are centered
        actual_center = actual_range.get_center()
        expected_center = expected_range.get_center()
        
        center_offset = np.sqrt(sum((a - e) ** 2 for a, e in zip(actual_center, expected_center)))
        max_expected_size = max(expected_size)
        
        if center_offset > max_expected_size * 0.1:  # More than 10% offset
            recommendations.append(f"Coordinates are offset from expected center by {center_offset:.1f} units")
        
        # Check for extreme aspect ratios
        aspect_ratios = [actual_size[i] / max(actual_size) for i in range(3)]
        if any(ratio < 0.1 for ratio in aspect_ratios):
            recommendations.append("Extreme aspect ratio detected - coordinates may be flattened")
    
    def _check_coordinate_consistency(self, map_data: MapData) -> List[str]:
        """Check for coordinate system consistency issues."""
        issues = []
        
        # Check for mixed coordinate systems (e.g., some coordinates in different units)
        all_coords = []
        
        for segment in map_data.line_segments:
            all_coords.extend([(segment.x1, segment.y1, segment.z1), (segment.x2, segment.y2, segment.z2)])
        
        for label in map_data.labels:
            all_coords.append((label.x, label.y, label.z))
        
        for waypoint in map_data.waypoints:
            all_coords.append((waypoint.x, waypoint.y, waypoint.z))
        
        if all_coords:
            coords_array = np.array(all_coords)
            
            # Check for coordinate system mixing (e.g., some coords in different scales)
            x_std = np.std(coords_array[:, 0])
            y_std = np.std(coords_array[:, 1])
            z_std = np.std(coords_array[:, 2])
            
            # If standard deviations are very different, might indicate mixed systems
            stds = [x_std, y_std, z_std]
            max_std = max(stds)
            min_std = min(stds)
            
            if max_std > 0 and min_std / max_std < 0.01:  # Very different scales
                issues.append("Possible mixed coordinate systems detected - coordinate scales vary significantly")
        
        return issues
    
    def _compare_ranges(self, actual: CoordinateRange, expected: CoordinateRange) -> float:
        """Compare two coordinate ranges and return difference percentage."""
        actual_size = actual.get_size()
        expected_size = expected.get_size()
        
        actual_max = max(actual_size)
        expected_max = max(expected_size)
        
        if expected_max == 0:
            return 1.0
        
        return abs(actual_max - expected_max) / expected_max
    
    def suggest_transformation(self, validation_result: CoordinateValidationResult, 
                             target_system: CoordinateSystem = CoordinateSystem.BABYLON_JS) -> Dict:
        """
        Suggest coordinate transformation based on validation results.
        
        Args:
            validation_result: Result from coordinate validation
            target_system: Target coordinate system
            
        Returns:
            Dictionary with transformation parameters
        """
        if not validation_result.coordinate_range:
            return {"error": "No coordinate range available"}
        
        actual_range = validation_result.coordinate_range
        center = actual_range.get_center()
        size = actual_range.get_size()
        max_size = max(size)
        
        # Calculate optimal scale factor for Babylon.js
        # Babylon.js works well with coordinates in the range of -1000 to 1000
        target_size = 2000  # -1000 to 1000 range
        scale_factor = target_size / max_size if max_size > 0 else 1.0
        
        # Calculate offset to center the geometry
        offset_x = -center[0] * scale_factor
        offset_y = -center[1] * scale_factor
        offset_z = -center[2] * scale_factor
        
        return {
            "scale_factor": scale_factor,
            "offset_x": offset_x,
            "offset_y": offset_y,
            "offset_z": offset_z,
            "target_system": target_system.value,
            "original_center": center,
            "original_size": size,
            "transformed_size": [s * scale_factor for s in size]
        }
    
    def validate_transformation(self, original_coords: List[Tuple[float, float, float]], 
                              transformed_coords: List[Tuple[float, float, float]]) -> bool:
        """
        Validate that a coordinate transformation preserves relative positions.
        
        Args:
            original_coords: Original coordinates
            transformed_coords: Transformed coordinates
            
        Returns:
            True if transformation is valid
        """
        if len(original_coords) != len(transformed_coords):
            return False
        
        if len(original_coords) < 2:
            return True  # Need at least 2 points to validate
        
        # Check that relative distances are preserved (within tolerance)
        tolerance = 0.01  # 1% tolerance
        
        for i in range(len(original_coords)):
            for j in range(i + 1, len(original_coords)):
                # Original distance
                orig_dist = np.sqrt(sum((original_coords[i][k] - original_coords[j][k]) ** 2 for k in range(3)))
                
                # Transformed distance
                trans_dist = np.sqrt(sum((transformed_coords[i][k] - transformed_coords[j][k]) ** 2 for k in range(3)))
                
                if orig_dist > 0:
                    ratio = trans_dist / orig_dist
                    if abs(ratio - 1.0) > tolerance:
                        self.logger.warning(f"Coordinate transformation may not preserve relative positions: ratio = {ratio}")
                        return False
        
        return True 