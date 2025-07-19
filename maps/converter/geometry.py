#!/usr/bin/env python3
"""
Geometry Generator for Map Conversion

This module handles the conversion of parsed map data into 3D geometry
suitable for glTF export and Babylon.js rendering.
"""

import numpy as np
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from parser import MapData, LineSegment, Label, Waypoint

@dataclass
class MeshData:
    """Container for generated mesh data."""
    vertices: np.ndarray
    faces: np.ndarray
    colors: np.ndarray
    name: str
    mesh_type: str  # 'line', 'label', 'waypoint'
    semantic_layer: Optional[str] = None  # Brewall semantic layer (e.g., 'walls', 'doors', 'water', etc.)

class GeometryGenerator:
    """Converts parsed map data into 3D geometry meshes."""
    
    def __init__(self, 
                 line_thickness: float = 2.0,
                 scale_factor: float = 1.0,
                 offset_x: float = 0.0,
                 offset_y: float = 0.0,
                 offset_z: float = 0.0,
                 verbose: bool = True):
        """
        Initialize the geometry generator.
        
        Args:
            line_thickness: Thickness of line segments in 3D space
            scale_factor: Scaling factor for coordinates
            offset_x/y/z: Offset values for coordinate transformation
            verbose: Enable verbose logging
        """
        self.line_thickness = line_thickness
        self.scale_factor = scale_factor
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.offset_z = offset_z
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
    
    def transform_coordinates(self, x: float, y: float, z: float) -> Tuple[float, float, float]:
        """Transform coordinates using scale and offset."""
        tx = (x + self.offset_x) * self.scale_factor
        ty = (y + self.offset_y) * self.scale_factor
        tz = (z + self.offset_z) * self.scale_factor
        return tx, ty, tz
    
    def generate_line_mesh(self, segment: LineSegment) -> Optional[MeshData]:
        """
        Convert a line segment to a 3D mesh.
        
        Creates a thin box along the line segment with the specified thickness.
        """
        # Transform coordinates
        x1, y1, z1 = self.transform_coordinates(segment.x1, segment.y1, segment.z1)
        x2, y2, z2 = self.transform_coordinates(segment.x2, segment.y2, segment.z2)
        
        # Create start and end points
        start = np.array([x1, y1, z1])
        end = np.array([x2, y2, z2])
        
        # Calculate line direction and length
        direction = end - start
        length = np.linalg.norm(direction)
        
        if length == 0:
            self.logger.warning(f"Zero-length line segment: {segment}")
            return None
        
        # Normalize direction
        direction = direction / length
        
        # Create perpendicular vectors for box cross-section
        # Use arbitrary perpendicular vector
        perp1 = np.array([-direction[1], direction[0], 0])
        if np.linalg.norm(perp1) == 0:
            perp1 = np.array([0, -direction[2], direction[1]])
        perp1 = perp1 / np.linalg.norm(perp1)
        
        perp2 = np.cross(direction, perp1)
        perp2 = perp2 / np.linalg.norm(perp2)
        
        # Create box vertices
        half_thickness = self.line_thickness / 2
        vertices = []
        
        # Bottom face
        vertices.extend([
            start - half_thickness * perp1 - half_thickness * perp2,
            start + half_thickness * perp1 - half_thickness * perp2,
            start + half_thickness * perp1 + half_thickness * perp2,
            start - half_thickness * perp1 + half_thickness * perp2
        ])
        
        # Top face
        vertices.extend([
            end - half_thickness * perp1 - half_thickness * perp2,
            end + half_thickness * perp1 - half_thickness * perp2,
            end + half_thickness * perp1 + half_thickness * perp2,
            end - half_thickness * perp1 + half_thickness * perp2
        ])
        
        # Define faces (triangles)
        faces = [
            # Bottom face
            [0, 1, 2], [0, 2, 3],
            # Top face
            [4, 6, 5], [4, 7, 6],
            # Side faces
            [0, 4, 1], [1, 4, 5],
            [1, 5, 2], [2, 5, 6],
            [2, 6, 3], [3, 6, 7],
            [3, 7, 0], [0, 7, 4]
        ]
        
        # Convert color to normalized RGB
        color = np.array([segment.r / 255.0, segment.g / 255.0, segment.b / 255.0])
        
        return MeshData(
            vertices=np.array(vertices),
            faces=np.array(faces),
            colors=np.tile(color, (len(vertices), 1)),
            name=f"line_{segment.x1}_{segment.y1}_{segment.x2}_{segment.y2}",
            mesh_type="line",
            semantic_layer=getattr(segment, 'layer', None)
        )
    
    def generate_label_mesh(self, label: Label) -> Optional[MeshData]:
        """
        Generate a 3D mesh for a label with proper text rendering and billboarding.
        
        Creates a billboard quad that faces the camera with proper text treatment.
        """
        # Transform coordinates
        x, y, z = self.transform_coordinates(label.x, label.y, label.z)
        
        # Determine label type and visual treatment
        label_type = self._classify_label(label.text)
        size_multiplier = self._get_label_size_multiplier(label_type, label.size)
        
        # Create a billboard quad that faces the camera
        # Size based on label type and text length
        base_size = label.size * size_multiplier
        text_length = len(label.text)
        width = base_size * (text_length * 0.6 + 1.0)  # Adjust width based on text length
        height = base_size * 1.2  # Fixed height ratio
        
        # Create quad vertices (facing camera)
        vertices = np.array([
            [-width/2, -height/2, 0],
            [width/2, -height/2, 0],
            [width/2, height/2, 0],
            [-width/2, height/2, 0]
        ])
        
        # Apply position offset
        vertices += np.array([x, y, z])
        
        # Create faces (two triangles)
        faces = np.array([[0, 1, 2], [0, 2, 3]])
        
        # Determine color based on label type
        if label_type == "waypoint":
            # Waypoints get special red color
            color = np.array([1.0, 0.0, 0.0])  # Bright red
        elif label_type == "zone":
            # Zone names get blue color
            color = np.array([0.0, 0.5, 1.0])  # Blue
        elif label_type == "npc":
            # NPC names get green color
            color = np.array([0.0, 1.0, 0.0])  # Green
        elif label_type == "item":
            # Item names get yellow color
            color = np.array([1.0, 1.0, 0.0])  # Yellow
        else:
            # Default: use label's original color
            color = np.array([label.r / 255.0, label.g / 255.0, label.b / 255.0])
        
        return MeshData(
            vertices=vertices,
            faces=faces,
            colors=np.tile(color, (len(vertices), 1)),
            name=f"label_{label_type}_{label.text}_{x}_{y}",
            mesh_type="label",
            semantic_layer=f"labels_{label_type}"
        )
    
    def _classify_label(self, text: str) -> str:
        """
        Classify label text to determine visual treatment.
        
        Args:
            text: Label text to classify
            
        Returns:
            Label type: 'waypoint', 'zone', 'npc', 'item', or 'general'
        """
        text_lower = text.lower().strip()
        
        # Waypoint indicators
        if any(keyword in text_lower for keyword in ['waypoint', 'bind', 'bind point', 'safe spot']):
            return "waypoint"
        
        # Zone names (typically capitalized, no spaces, or specific patterns)
        if (text.isupper() or 
            any(keyword in text_lower for keyword in ['zone', 'plane', 'temple', 'tower', 'keep', 'fortress'])):
            return "zone"
        
        # NPC names (typically proper nouns, often with titles)
        if any(keyword in text_lower for keyword in ['lord', 'king', 'queen', 'guard', 'merchant', 'trainer', 'npc']):
            return "npc"
        
        # Item names (often in quotes or specific patterns)
        if text.startswith('"') and text.endswith('"'):
            return "item"
        
        # Default classification
        return "general"
    
    def _get_label_size_multiplier(self, label_type: str, base_size: int) -> float:
        """
        Get size multiplier based on label type and base size.
        
        Args:
            label_type: Type of label
            base_size: Base size from Brewall file
            
        Returns:
            Size multiplier for visual scaling
        """
        # Base multipliers by type
        type_multipliers = {
            "waypoint": 15.0,  # Waypoints should be very visible
            "zone": 12.0,      # Zone names should be prominent
            "npc": 8.0,        # NPC names moderately visible
            "item": 6.0,       # Items smaller
            "general": 10.0    # Default size
        }
        
        base_multiplier = type_multipliers.get(label_type, 10.0)
        
        # Adjust based on base size
        if base_size <= 5:
            return base_multiplier * 0.8
        elif base_size >= 15:
            return base_multiplier * 1.2
        else:
            return base_multiplier
    
    def generate_waypoint_mesh(self, waypoint: Waypoint) -> Optional[MeshData]:
        """
        Generate a distinctive 3D mesh for a waypoint.
        
        Creates a distinctive marker with multiple visual elements to make waypoints easily identifiable.
        """
        # Transform coordinates
        x, y, z = self.transform_coordinates(waypoint.x, waypoint.y, waypoint.z)
        
        # Create a distinctive marker with multiple elements
        # Main cylinder
        radius = 25.0
        height = 50.0
        
        # Generate cylinder vertices
        vertices = []
        segments = 16
        
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            vx = radius * np.cos(angle)
            vy = radius * np.sin(angle)
            
            # Bottom circle
            vertices.append([vx, vy, -height/2])
            # Top circle
            vertices.append([vx, vy, height/2])
        
        # Add a top cone for better visibility
        cone_height = 30.0
        cone_radius = 15.0
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            vx = cone_radius * np.cos(angle)
            vy = cone_radius * np.sin(angle)
            
            # Cone base (same as cylinder top)
            vertices.append([vx, vy, height/2])
            # Cone tip
            vertices.append([0, 0, height/2 + cone_height])
        
        # Apply position offset
        vertices = np.array(vertices) + np.array([x, y, z])
        
        # Generate faces
        faces = []
        
        # Cylinder side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.extend([
                [i*2, next_i*2, next_i*2+1],
                [i*2, next_i*2+1, i*2+1]
            ])
        
        # Cylinder top and bottom faces
        for i in range(1, segments-1):
            faces.extend([
                [0, i*2, (i+1)*2],  # Bottom
                [1, (i+1)*2+1, i*2+1]  # Top
            ])
        
        # Cone faces
        cone_base_start = segments * 2
        for i in range(segments):
            next_i = (i + 1) % segments
            # Cone side faces
            faces.extend([
                [cone_base_start + i*2, cone_base_start + next_i*2, cone_base_start + next_i*2+1],
                [cone_base_start + i*2, cone_base_start + next_i*2+1, cone_base_start + i*2+1]
            ])
        
        # Waypoint color - bright red for high visibility
        if waypoint.special_visual:
            color = np.array([1.0, 0.0, 0.0])  # Bright red
        else:
            color = np.array([0.8, 0.2, 0.2])  # Darker red
        
        return MeshData(
            vertices=vertices,
            faces=np.array(faces),
            colors=np.tile(color, (len(vertices), 1)),
            name=f"waypoint_{waypoint.zone_name}_{x}_{y}",
            mesh_type="waypoint",
            semantic_layer="waypoints"
        )
    
    def generate_all_geometry(self, map_data: MapData) -> List[MeshData]:
        """
        Generate 3D geometry for all elements in the map data.
        
        Args:
            map_data: Parsed map data containing line segments, labels, and waypoints
            
        Returns:
            List of MeshData objects for all generated geometry
        """
        meshes = []
        
        if self.verbose:
            self.logger.info(f"Generating geometry for zone: {map_data.zone_name}")
            self.logger.info(f"  Line segments: {len(map_data.line_segments)}")
            self.logger.info(f"  Labels: {len(map_data.labels)}")
            self.logger.info(f"  Waypoints: {len(map_data.waypoints)}")
        
        # Generate line segment meshes
        for i, segment in enumerate(map_data.line_segments):
            mesh = self.generate_line_mesh(segment)
            if mesh:
                meshes.append(mesh)
        
        # Generate label meshes
        for i, label in enumerate(map_data.labels):
            mesh = self.generate_label_mesh(label)
            if mesh:
                meshes.append(mesh)
        
        # Generate waypoint meshes
        for i, waypoint in enumerate(map_data.waypoints):
            mesh = self.generate_waypoint_mesh(waypoint)
            if mesh:
                meshes.append(mesh)
        
        if self.verbose:
            self.logger.info(f"Generated {len(meshes)} meshes total")
        
        return meshes
    
    def optimize_geometry(self, meshes: List[MeshData]) -> List[MeshData]:
        """
        Optimize geometry by combining similar meshes and removing duplicates.
        
        Args:
            meshes: List of mesh data to optimize
            
        Returns:
            Optimized list of mesh data
        """
        if not meshes:
            return meshes
        
        # Group meshes by type and color
        mesh_groups = {}
        
        for mesh in meshes:
            # Create a key based on mesh type and average color
            avg_color = np.mean(mesh.colors, axis=0)
            color_key = tuple(np.round(avg_color, 3))
            key = (mesh.mesh_type, color_key)
            
            if key not in mesh_groups:
                mesh_groups[key] = []
            mesh_groups[key].append(mesh)
        
        # Combine meshes in each group
        optimized_meshes = []
        
        for (mesh_type, color_key), group_meshes in mesh_groups.items():
            if len(group_meshes) == 1:
                # Single mesh, no optimization needed
                optimized_meshes.append(group_meshes[0])
            else:
                # Combine multiple meshes
                combined_mesh = self._combine_meshes(group_meshes, mesh_type)
                if combined_mesh:
                    optimized_meshes.append(combined_mesh)
        
        if self.verbose:
            self.logger.info(f"Optimized {len(meshes)} meshes to {len(optimized_meshes)} meshes")
        
        return optimized_meshes
    
    def _combine_meshes(self, meshes: List[MeshData], mesh_type: str) -> Optional[MeshData]:
        """Combine multiple meshes into a single mesh."""
        if not meshes:
            return None
        
        all_vertices = []
        all_faces = []
        all_colors = []
        vertex_offset = 0
        
        for mesh in meshes:
            all_vertices.append(mesh.vertices)
            # Adjust face indices for the combined mesh
            adjusted_faces = mesh.faces + vertex_offset
            all_faces.append(adjusted_faces)
            all_colors.append(mesh.colors)
            vertex_offset += len(mesh.vertices)
        
        # Combine all data
        combined_vertices = np.vstack(all_vertices)
        combined_faces = np.vstack(all_faces)
        combined_colors = np.vstack(all_colors)
        
        return MeshData(
            vertices=combined_vertices,
            faces=combined_faces,
            colors=combined_colors,
            name=f"combined_{mesh_type}_{len(meshes)}_meshes",
            mesh_type=mesh_type
        )
    
    def calculate_bounding_box(self, meshes: List[MeshData]) -> Dict[str, float]:
        """Calculate the bounding box of all meshes."""
        if not meshes:
            return {"min_x": 0, "min_y": 0, "min_z": 0, 
                   "max_x": 0, "max_y": 0, "max_z": 0}
        
        all_vertices = np.vstack([mesh.vertices for mesh in meshes])
        
        min_coords = np.min(all_vertices, axis=0)
        max_coords = np.max(all_vertices, axis=0)
        
        return {
            "min_x": float(min_coords[0]),
            "min_y": float(min_coords[1]),
            "min_z": float(min_coords[2]),
            "max_x": float(max_coords[0]),
            "max_y": float(max_coords[1]),
            "max_z": float(max_coords[2])
        } 