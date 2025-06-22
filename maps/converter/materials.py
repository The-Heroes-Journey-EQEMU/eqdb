#!/usr/bin/env python3
"""
Material System for Map Conversion

This module handles material definitions and assignment for different
map elements including lines, labels, waypoints, and special effects.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class MaterialType(Enum):
    """Types of materials used in the map."""
    LINE = "line"
    LABEL = "label"
    WAYPOINT = "waypoint"
    WATER = "water"
    AIR = "air"
    TERRAIN = "terrain"
    UI = "ui"

@dataclass
class Material:
    """Material definition for 3D rendering."""
    name: str
    material_type: MaterialType
    base_color: Tuple[float, float, float, float]  # RGBA
    metallic_factor: float = 0.0
    roughness_factor: float = 0.8
    alpha_mode: str = "OPAQUE"  # OPAQUE, MASK, BLEND
    alpha_cutoff: float = 0.5
    double_sided: bool = True
    emissive_factor: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    
    def to_dict(self) -> Dict:
        """Convert material to dictionary for glTF export."""
        return {
            "name": self.name,
            "pbrMetallicRoughness": {
                "baseColorFactor": list(self.base_color),
                "metallicFactor": self.metallic_factor,
                "roughnessFactor": self.roughness_factor
            },
            "alphaMode": self.alpha_mode,
            "alphaCutoff": self.alpha_cutoff,
            "doubleSided": self.double_sided,
            "emissiveFactor": list(self.emissive_factor)
        }

class MaterialLibrary:
    """Library of predefined materials for map elements."""
    
    def __init__(self):
        """Initialize the material library with predefined materials."""
        self.materials = {}
        self._create_default_materials()
        self._create_brewall_layer_materials()
    
    def _create_default_materials(self):
        """Create default materials for the library."""
        
        # Line materials
        self.materials["line_default"] = Material(
            name="line_default",
            material_type=MaterialType.LINE,
            base_color=(0.8, 0.8, 0.8, 1.0),
            roughness_factor=0.8
        )
        
        # Label materials
        self.materials["label_standard"] = Material(
            name="label_standard",
            material_type=MaterialType.LABEL,
            base_color=(1.0, 1.0, 1.0, 1.0),
            roughness_factor=0.5,
            emissive_factor=(0.1, 0.1, 0.1)
        )
        
        self.materials["label_important"] = Material(
            name="label_important",
            material_type=MaterialType.LABEL,
            base_color=(1.0, 1.0, 0.0, 1.0),
            roughness_factor=0.3,
            emissive_factor=(0.2, 0.2, 0.0)
        )
        
        # New label type materials
        self.materials["label_waypoint"] = Material(
            name="label_waypoint",
            material_type=MaterialType.LABEL,
            base_color=(1.0, 0.0, 0.0, 1.0),
            roughness_factor=0.2,
            emissive_factor=(0.3, 0.0, 0.0)
        )
        
        self.materials["label_zone"] = Material(
            name="label_zone",
            material_type=MaterialType.LABEL,
            base_color=(0.0, 0.5, 1.0, 1.0),
            roughness_factor=0.3,
            emissive_factor=(0.0, 0.1, 0.2)
        )
        
        self.materials["label_npc"] = Material(
            name="label_npc",
            material_type=MaterialType.LABEL,
            base_color=(0.0, 1.0, 0.0, 1.0),
            roughness_factor=0.4,
            emissive_factor=(0.0, 0.2, 0.0)
        )
        
        self.materials["label_item"] = Material(
            name="label_item",
            material_type=MaterialType.LABEL,
            base_color=(1.0, 1.0, 0.0, 1.0),
            roughness_factor=0.5,
            emissive_factor=(0.2, 0.2, 0.0)
        )
        
        # Waypoint materials
        self.materials["waypoint_general"] = Material(
            name="waypoint_general",
            material_type=MaterialType.WAYPOINT,
            base_color=(1.0, 0.0, 0.0, 1.0),
            roughness_factor=0.2,
            emissive_factor=(0.3, 0.0, 0.0)
        )
        
        self.materials["waypoint_wizard"] = Material(
            name="waypoint_wizard",
            material_type=MaterialType.WAYPOINT,
            base_color=(0.5, 0.0, 1.0, 1.0),
            roughness_factor=0.2,
            emissive_factor=(0.2, 0.0, 0.3)
        )
        
        self.materials["waypoint_druid"] = Material(
            name="waypoint_druid",
            material_type=MaterialType.WAYPOINT,
            base_color=(0.0, 0.8, 0.0, 1.0),
            roughness_factor=0.2,
            emissive_factor=(0.0, 0.2, 0.0)
        )
        
        # Water materials
        self.materials["water_shallow"] = Material(
            name="water_shallow",
            material_type=MaterialType.WATER,
            base_color=(0.4, 0.6, 1.0, 0.7),
            roughness_factor=0.1,
            alpha_mode="BLEND"
        )
        
        self.materials["water_deep"] = Material(
            name="water_deep",
            material_type=MaterialType.WATER,
            base_color=(0.1, 0.3, 0.8, 0.9),
            roughness_factor=0.05,
            alpha_mode="BLEND"
        )
        
        # Air materials
        self.materials["air"] = Material(
            name="air",
            material_type=MaterialType.AIR,
            base_color=(0.8, 0.9, 1.0, 0.3),
            roughness_factor=0.9,
            alpha_mode="BLEND"
        )
        
        # Terrain materials
        self.materials["terrain_ground"] = Material(
            name="terrain_ground",
            material_type=MaterialType.TERRAIN,
            base_color=(0.6, 0.4, 0.2, 1.0),
            roughness_factor=0.9
        )
        
        self.materials["terrain_rock"] = Material(
            name="terrain_rock",
            material_type=MaterialType.TERRAIN,
            base_color=(0.5, 0.5, 0.5, 1.0),
            roughness_factor=0.8
        )
        
        # UI materials
        self.materials["ui_compass"] = Material(
            name="ui_compass",
            material_type=MaterialType.UI,
            base_color=(1.0, 1.0, 1.0, 0.8),
            roughness_factor=0.5,
            alpha_mode="BLEND"
        )
    
    def _create_brewall_layer_materials(self):
        """Create a material for each Brewall semantic layer/type."""
        for rgb, layer in BREWALL_LAYER_COLOR_MAP.items():
            name = f"layer_{layer}"
            color = tuple([c / 255.0 for c in rgb] + [1.0])  # RGBA
            self.materials[name] = Material(
                name=name,
                material_type=MaterialType.LINE,
                base_color=color,
                roughness_factor=0.8,
                alpha_mode="OPAQUE"
            )
    
    def get_material(self, name: str) -> Optional[Material]:
        """Get a material by name."""
        return self.materials.get(name)
    
    def create_color_material(self, color: Tuple[int, int, int], 
                            material_type: MaterialType = MaterialType.LINE,
                            alpha: float = 1.0) -> Material:
        """
        Create a material from RGB color values.
        
        Args:
            color: RGB tuple (0-255)
            material_type: Type of material
            alpha: Alpha value (0.0-1.0)
            
        Returns:
            Material object
        """
        # Convert RGB to normalized values
        r, g, b = color
        normalized_color = (r / 255.0, g / 255.0, b / 255.0, alpha)
        
        # Generate unique name
        name = f"{material_type.value}_{r}_{g}_{b}_{int(alpha*100)}"
        
        # Create material
        material = Material(
            name=name,
            material_type=material_type,
            base_color=normalized_color,
            roughness_factor=0.8
        )
        
        # Store in library
        self.materials[name] = material
        
        return material
    
    def get_materials_by_type(self, material_type: MaterialType) -> List[Material]:
        """Get all materials of a specific type."""
        return [mat for mat in self.materials.values() if mat.material_type == material_type]
    
    def get_all_materials(self) -> List[Material]:
        """Get all materials in the library."""
        return list(self.materials.values())
    
    def get_material_by_layer(self, layer: str) -> Optional[Material]:
        """Get a material by Brewall semantic layer/type."""
        return self.materials.get(f"layer_{layer}")

class MaterialAssigner:
    """Assigns materials to mesh data based on various criteria."""
    
    def __init__(self, material_library: MaterialLibrary):
        """
        Initialize the material assigner.
        
        Args:
            material_library: Library of available materials
        """
        self.library = material_library
        self.assigned_materials = {}  # Cache for assigned materials
    
    def assign_material_by_semantic_layer(self, semantic_layer: str) -> Material:
        """
        Assign material based on semantic layer name.
        
        Args:
            semantic_layer: Semantic layer name (e.g., 'walls', 'doors', 'water', etc.)
            
        Returns:
            Assigned material
        """
        # Try to get material directly by layer name
        material = self.library.get_material_by_layer(semantic_layer)
        if material:
            return material
        
        # Handle new label type semantic layers
        if semantic_layer.startswith("labels_"):
            label_type = semantic_layer.replace("labels_", "")
            material_name = f"label_{label_type}"
            material = self.library.get_material(material_name)
            if material:
                return material
        
        # Fallback mappings for common semantic layers
        layer_mappings = {
            'walls': 'wall',
            'doors': 'door',
            'water': 'water_deep',
            'teleporters': 'teleporter',
            'spawns': 'spawn',
            'npcs': 'npc',
            'items': 'item',
            'corpses': 'corpse',
            'waypoints': 'waypoint_general',
            'labels': 'label_standard',
            'air': 'air',
            'terrain': 'terrain_ground',
            'ui': 'ui_compass'
        }
        
        # Check fallback mappings
        if semantic_layer in layer_mappings:
            material = self.library.get_material(layer_mappings[semantic_layer])
            if material:
                return material
        
        # Final fallback to default line material
        return self.library.get_material("line_default")
    
    def assign_material_to_line(self, segment_color: Tuple[int, int, int], 
                               segment_type: str = "default", layer: str = None) -> Material:
        """
        Assign material to a line segment based on semantic layer/type if available, otherwise by color/type.
        """
        if layer:
            mat = self.library.get_material_by_layer(layer)
            if mat:
                return mat
        # Fallback to previous logic
        # Check for special line types first
        if segment_type == "water":
            # Determine water depth by color intensity
            r, g, b = segment_color
            intensity = (r + g + b) / 3
            if intensity > 128:
                return self.library.get_material("water_shallow")
            else:
                return self.library.get_material("water_deep")
        
        elif segment_type == "air":
            return self.library.get_material("air")
        
        elif segment_type == "ui":
            return self.library.get_material("ui_compass")
        
        elif segment_type == "terrain":
            # Determine terrain type by color
            r, g, b = segment_color
            if r > g and r > b:  # Reddish - rock
                return self.library.get_material("terrain_rock")
            else:  # Brownish - ground
                return self.library.get_material("terrain_ground")
        
        else:
            # Create color-based material for standard lines
            return self.library.create_color_material(
                segment_color, 
                MaterialType.LINE
            )
    
    def assign_material_to_label(self, label_color: Tuple[int, int, int],
                                label_size: int) -> Material:
        """
        Assign material to a label based on color and size.
        
        Args:
            label_color: RGB color of the label
            label_size: Size of the label (indicates importance)
            
        Returns:
            Assigned material
        """
        # Important labels (large size) get special treatment
        if label_size > 15:
            return self.library.get_material("label_important")
        
        # Create color-based material for standard labels
        return self.library.create_color_material(
            label_color,
            MaterialType.LABEL
        )
    
    def assign_material_to_waypoint(self, waypoint_type: str = "waypoint",
                                   special_visual: bool = True) -> Material:
        """
        Assign material to a waypoint based on type and visual settings.
        
        Args:
            waypoint_type: Type of waypoint
            special_visual: Whether to use special visual treatment
            
        Returns:
            Assigned material
        """
        if not special_visual:
            # Use general waypoint material for non-special waypoints
            return self.library.get_material("waypoint_general")
        
        # Assign based on waypoint type
        if waypoint_type == "wizard":
            return self.library.get_material("waypoint_wizard")
        elif waypoint_type == "druid":
            return self.library.get_material("waypoint_druid")
        else:
            return self.library.get_material("waypoint_general")
    
    def get_material_key(self, material: Material) -> str:
        """Generate a unique key for a material."""
        return f"{material.name}_{material.material_type.value}"
    
    def get_all_assigned_materials(self) -> List[Material]:
        """Get all materials that have been assigned."""
        return list(set(self.assigned_materials.values()))

class MaterialOptimizer:
    """Optimizes materials by combining similar ones and reducing redundancy."""
    
    def __init__(self, material_library: MaterialLibrary):
        """
        Initialize the material optimizer.
        
        Args:
            material_library: Library of materials to optimize
        """
        self.library = material_library
    
    def optimize_materials(self, materials: List[Material]) -> List[Material]:
        """
        Optimize a list of materials by combining similar ones.
        
        Args:
            materials: List of materials to optimize
            
        Returns:
            Optimized list of materials
        """
        if not materials:
            return materials
        
        # Group materials by type and similar properties
        material_groups = {}
        
        for material in materials:
            # Create a key based on material properties
            key = self._create_material_key(material)
            
            if key not in material_groups:
                material_groups[key] = []
            material_groups[key].append(material)
        
        # Select representative material from each group
        optimized_materials = []
        
        for key, group in material_groups.items():
            # Use the first material as representative
            representative = group[0]
            
            # Update name to reflect combination
            if len(group) > 1:
                representative.name = f"combined_{representative.material_type.value}_{len(group)}"
            
            optimized_materials.append(representative)
        
        return optimized_materials
    
    def _create_material_key(self, material: Material) -> str:
        """Create a key for grouping similar materials."""
        # Round color values to reduce precision
        color_key = tuple(round(c, 2) for c in material.base_color)
        
        return f"{material.material_type.value}_{color_key}_{material.roughness_factor}_{material.alpha_mode}"
    
    def merge_similar_colors(self, materials: List[Material], 
                           color_tolerance: float = 0.1) -> List[Material]:
        """
        Merge materials with similar colors.
        
        Args:
            materials: List of materials to merge
            color_tolerance: Tolerance for color similarity (0.0-1.0)
            
        Returns:
            Merged list of materials
        """
        if not materials:
            return materials
        
        # Group by material type first
        type_groups = {}
        for material in materials:
            if material.material_type not in type_groups:
                type_groups[material.material_type] = []
            type_groups[material.material_type].append(material)
        
        merged_materials = []
        
        for material_type, type_materials in type_groups.items():
            # Group by similar colors within each type
            color_groups = {}
            
            for material in type_materials:
                color_key = self._find_similar_color_group(
                    material.base_color, color_groups, color_tolerance
                )
                
                if color_key not in color_groups:
                    color_groups[color_key] = []
                color_groups[color_key].append(material)
            
            # Use representative material from each color group
            for color_key, group in color_groups.items():
                representative = group[0]
                if len(group) > 1:
                    representative.name = f"merged_{material_type.value}_{len(group)}"
                merged_materials.append(representative)
        
        return merged_materials
    
    def _find_similar_color_group(self, color: Tuple[float, float, float, float],
                                 color_groups: Dict,
                                 tolerance: float) -> str:
        """Find or create a color group for a given color."""
        for existing_color in color_groups.keys():
            if self._colors_are_similar(color, existing_color, tolerance):
                return existing_color
        
        # Create new color group
        return str(color)
    
    def _colors_are_similar(self, color1: Tuple[float, float, float, float],
                           color2: Tuple[float, float, float, float],
                           tolerance: float) -> bool:
        """Check if two colors are similar within tolerance."""
        # Compare RGB components (ignore alpha for similarity)
        for i in range(3):
            if abs(color1[i] - color2[i]) > tolerance:
                return False
        return True

# Brewall mapping standards: RGB color to semantic layer/type
BREWALL_LAYER_COLOR_MAP = {
    (255, 0, 200): "wall",           # Magenta
    (255, 255, 0): "door",          # Yellow
    (0, 0, 255): "water",           # Blue
    (255, 0, 0): "lava",            # Red
    (0, 255, 0): "zone_line",       # Green
    (0, 255, 255): "safe_point",    # Cyan
    (255, 128, 0): "lift",          # Orange
    (128, 64, 0): "bridge",         # Brown
    (255, 128, 255): "platform",    # Pink
    (128, 255, 255): "ladder",      # Light Cyan
    (255, 255, 255): "invisible",   # White
    (128, 128, 128): "ground",      # Gray
    (0, 0, 0): "void",              # Black
    (255, 128, 128): "ramp",        # Light Red
    (128, 255, 128): "stairs",      # Light Green
    (128, 128, 255): "portal",      # Light Blue
    (255, 128, 64): "elevator",     # Orange-Brown
    (255, 64, 255): "teleport",     # Purple-Pink
    (255, 255, 128): "light",       # Light Yellow
    (0, 128, 255): "path",          # Sky Blue
    (255, 64, 0): "fire",           # Orange-Red
    (0, 128, 0): "forest",          # Dark Green
    (128, 0, 255): "magic",         # Violet
    (255, 0, 128): "trap",          # Pink-Red
    (128, 255, 0): "grass",         # Light Green-Yellow
    (0, 255, 128): "swamp",         # Green-Cyan
    (128, 0, 0): "danger",          # Dark Red
    (0, 128, 128): "cave",          # Teal
    (128, 128, 0): "ruins",         # Olive
    (0, 0, 128): "deep_water",      # Navy
    (128, 0, 128): "special",       # Purple
    # ... add more as needed ...
}

# Human-friendly display names for each layer
BREWALL_LAYER_DISPLAY_NAMES = {
    "wall": "Wall",
    "door": "Door",
    "water": "Water",
    "lava": "Lava",
    "zone_line": "Zone Line",
    "safe_point": "Safe Point",
    "lift": "Lift/Elevator",
    "bridge": "Bridge",
    "platform": "Platform",
    "ladder": "Ladder",
    "invisible": "Invisible Wall",
    "ground": "Ground",
    "void": "Void",
    "ramp": "Ramp",
    "stairs": "Stairs",
    "portal": "Portal",
    "elevator": "Elevator",
    "teleport": "Teleport",
    "light": "Light Source",
    "path": "Path",
    "fire": "Fire",
    "forest": "Forest",
    "magic": "Magic",
    "trap": "Trap",
    "grass": "Grass",
    "swamp": "Swamp",
    "danger": "Danger",
    "cave": "Cave",
    "ruins": "Ruins",
    "deep_water": "Deep Water",
    "special": "Special",
    # ... add more as needed ...
} 