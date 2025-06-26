#!/usr/bin/env python3
"""
glTF Exporter for Map Conversion

This module handles the export of 3D geometry and materials to glTF format
for use with Babylon.js and other 3D viewers.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

try:
    from pygltflib import GLTF2, Scene, Node, Mesh, Material as GLTFMaterial, Buffer, BufferView, Accessor
    from pygltflib import Asset, Primitive
except ImportError:
    print("Warning: pygltflib not installed. Install with: pip install pygltflib")
    GLTF2 = None

from geometry import MeshData
from materials import Material, MaterialLibrary, MaterialAssigner

class GLTFExporter:
    """Exports 3D geometry and materials to glTF format."""
    
    def __init__(self, verbose: bool = True):
        """
        Initialize the glTF exporter.
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
        
        if GLTF2 is None:
            raise ImportError("pygltflib is required for glTF export")
    
    def export_meshes_to_gltf(self, meshes: List[MeshData], 
                             materials: List[Material],
                             output_path: str,
                             zone_name: str = "unknown") -> Dict[str, Any]:
        """
        Export a list of meshes to glTF format.
        
        Args:
            meshes: List of mesh data to export
            materials: List of materials to export
            output_path: Path to save the glTF file
            zone_name: Name of the zone for metadata
            
        Returns:
            Dictionary containing export metadata
        """
        if not meshes:
            self.logger.warning("No meshes to export")
            return {}
        
        # Create glTF structure
        gltf = GLTF2()
        
        # Initialize arrays
        gltf.scenes = []
        gltf.nodes = []
        gltf.meshes = []
        gltf.materials = []
        gltf.buffers = []
        gltf.bufferViews = []
        gltf.accessors = []
        
        # Create asset information
        gltf.asset = Asset(
            version="2.0",
            generator="EQDB Map Converter",
            copyright="EQDB Development Team"
        )
        
        # Create scene
        scene = Scene()
        scene.nodes = []
        gltf.scenes.append(scene)
        
        # Create root node
        root_node = Node()
        root_node.name = f"{zone_name}_root"
        gltf.nodes.append(root_node)
        scene.nodes.append(0)  # Root node index
        
        # Create buffer for all geometry data
        buffer_data = bytearray()
        gltf.buffers.append(Buffer(byteLength=0))
        
        # Export materials
        material_indices = self._export_materials(gltf, materials)
        
        # Export meshes
        mesh_indices = self._export_meshes(gltf, meshes, material_indices, buffer_data)
        
        # Create nodes for each mesh
        for i, mesh in enumerate(meshes):
            node = Node()
            node.name = mesh.name
            node.mesh = mesh_indices[i]
            gltf.nodes.append(node)
            
            # Add to root node's children
            if not hasattr(root_node, 'children'):
                root_node.children = []
            root_node.children.append(len(gltf.nodes) - 1)
        
        # Update buffer with actual data
        gltf.buffers[0].byteLength = len(buffer_data)
        gltf.buffers[0].uri = f"data:application/octet-stream;base64,{buffer_data.hex()}"
        
        # Set default scene
        gltf.scene = 0
        
        # Save to file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        gltf.save(output_path)
        
        # Calculate export statistics
        stats = self._calculate_export_stats(meshes, materials, output_path)
        
        if self.verbose:
            self.logger.info(f"Exported {len(meshes)} meshes to {output_path}")
            self.logger.info(f"Total vertices: {stats['total_vertices']:,}")
            self.logger.info(f"Total faces: {stats['total_faces']:,}")
            self.logger.info(f"File size: {stats['file_size']:,} bytes")
        
        return stats
    
    def _export_materials(self, gltf: GLTF2, materials: List[Material]) -> Dict[str, int]:
        """Export materials to glTF format."""
        material_indices = {}
        
        for i, material in enumerate(materials):
            gltf_material = GLTFMaterial()
            gltf_material.name = material.name
            
            # Set PBR metallic roughness properties
            gltf_material.pbrMetallicRoughness = {
                "baseColorFactor": list(material.base_color),
                "metallicFactor": material.metallic_factor,
                "roughnessFactor": material.roughness_factor
            }
            
            # Set alpha mode
            if material.alpha_mode != "OPAQUE":
                gltf_material.alphaMode = material.alpha_mode
                gltf_material.alphaCutoff = material.alpha_cutoff
            
            # Set double-sided property
            if material.double_sided:
                gltf_material.doubleSided = True
            
            # Set emissive factor
            if any(factor > 0 for factor in material.emissive_factor):
                gltf_material.emissiveFactor = list(material.emissive_factor)
            
            gltf.materials.append(gltf_material)
            material_indices[material.name] = i
        
        return material_indices
    
    def _export_meshes(self, gltf: GLTF2, meshes: List[MeshData], 
                      material_indices: Dict[str, int], 
                      buffer_data: bytearray) -> List[int]:
        """Export meshes to glTF format."""
        mesh_indices = []
        
        for mesh in meshes:
            # Create buffer views and accessors for vertices
            vertex_data = mesh.vertices.astype('float32').tobytes()
            vertex_offset = len(buffer_data)
            buffer_data.extend(vertex_data)
            
            vertex_buffer_view = BufferView(
                buffer=0,
                byteOffset=vertex_offset,
                byteLength=len(vertex_data),
                target=34962  # ARRAY_BUFFER
            )
            gltf.bufferViews.append(vertex_buffer_view)
            
            vertex_accessor = Accessor(
                bufferView=len(gltf.bufferViews) - 1,
                componentType=5126,  # FLOAT
                count=len(mesh.vertices),
                type="VEC3",
                min=mesh.vertices.min(axis=0).tolist(),
                max=mesh.vertices.max(axis=0).tolist()
            )
            gltf.accessors.append(vertex_accessor)
            
            # Create buffer views and accessors for indices
            index_data = mesh.faces.astype('uint16').tobytes()
            index_offset = len(buffer_data)
            buffer_data.extend(index_data)
            
            index_buffer_view = BufferView(
                buffer=0,
                byteOffset=index_offset,
                byteLength=len(index_data),
                target=34963  # ELEMENT_ARRAY_BUFFER
            )
            gltf.bufferViews.append(index_buffer_view)
            
            index_accessor = Accessor(
                bufferView=len(gltf.bufferViews) - 1,
                componentType=5123,  # UNSIGNED_SHORT
                count=len(mesh.faces) * 3,
                type="SCALAR"
            )
            gltf.accessors.append(index_accessor)
            
            # Create primitive
            primitive = Primitive(
                attributes={"POSITION": len(gltf.accessors) - 2},
                indices=len(gltf.accessors) - 1
            )
            
            # Assign material if available
            if hasattr(mesh, 'material_name') and mesh.material_name in material_indices:
                primitive.material = material_indices[mesh.material_name]
            
            # Create mesh
            gltf_mesh = Mesh()
            gltf_mesh.name = mesh.name
            gltf_mesh.primitives = [primitive]
            gltf.meshes.append(gltf_mesh)
            
            mesh_indices.append(len(gltf.meshes) - 1)
        
        return mesh_indices
    
    def _calculate_export_stats(self, meshes: List[MeshData], 
                               materials: List[Material], 
                               output_path: str) -> Dict[str, Any]:
        """Calculate export statistics."""
        total_vertices = sum(len(mesh.vertices) for mesh in meshes)
        total_faces = sum(len(mesh.faces) for mesh in meshes)
        
        # Calculate bounding box
        all_vertices = []
        for mesh in meshes:
            all_vertices.extend(mesh.vertices)
        
        if all_vertices:
            import numpy as np
            vertices_array = np.array(all_vertices)
            min_coords = vertices_array.min(axis=0)
            max_coords = vertices_array.max(axis=0)
            bounding_box = {
                "min_x": float(min_coords[0]),
                "min_y": float(min_coords[1]),
                "min_z": float(min_coords[2]),
                "max_x": float(max_coords[0]),
                "max_y": float(max_coords[1]),
                "max_z": float(max_coords[2])
            }
        else:
            bounding_box = {"min_x": 0, "min_y": 0, "min_z": 0, 
                          "max_x": 0, "max_y": 0, "max_z": 0}
        
        # Get file size
        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
        
        return {
            "total_vertices": total_vertices,
            "total_faces": total_faces,
            "mesh_count": len(meshes),
            "material_count": len(materials),
            "file_size": file_size,
            "bounding_box": bounding_box
        }
    
    def export_with_materials(self, meshes: List[MeshData], 
                            material_assigner: MaterialAssigner,
                            output_path: str,
                            zone_name: str = "unknown") -> Dict[str, Any]:
        """
        Export meshes with automatic material assignment.
        
        Args:
            meshes: List of mesh data to export
            material_assigner: Material assigner for automatic material assignment
            output_path: Path to save the glTF file
            zone_name: Name of the zone for metadata
            
        Returns:
            Dictionary containing export metadata
        """
        # Assign materials to meshes
        assigned_materials = []
        material_names = []
        
        for mesh in meshes:
            # Determine material based on semantic layer first, then fall back to type/color
            if mesh.semantic_layer:
                # Use semantic layer for material assignment
                material = material_assigner.assign_material_by_semantic_layer(mesh.semantic_layer)
                if self.verbose:
                    self.logger.info(f"Assigned material '{material.name}' to mesh '{mesh.name}' based on semantic layer '{mesh.semantic_layer}'")
            elif mesh.mesh_type == "waypoint":
                material = material_assigner.assign_material_to_waypoint("waypoint", True)
                if self.verbose:
                    self.logger.info(f"Assigned material '{material.name}' to waypoint mesh '{mesh.name}'")
            elif mesh.mesh_type == "label":
                # Use default color for labels (will be overridden by actual color)
                material = material_assigner.assign_material_to_label((255, 255, 255), 10)
                if self.verbose:
                    self.logger.info(f"Assigned material '{material.name}' to label mesh '{mesh.name}'")
            else:
                # For lines, use the average color from the mesh
                avg_color = mesh.colors.mean(axis=0) * 255
                material = material_assigner.assign_material_to_line(
                    (int(avg_color[0]), int(avg_color[1]), int(avg_color[2]))
                )
                if self.verbose:
                    self.logger.info(f"Assigned material '{material.name}' to line mesh '{mesh.name}' based on color {tuple(avg_color.astype(int))}")
            
            assigned_materials.append(material)
            material_names.append(material.name)
        
        # Remove duplicates while preserving order
        unique_materials = []
        seen_names = set()
        for material in assigned_materials:
            if material.name not in seen_names:
                unique_materials.append(material)
                seen_names.add(material.name)
        
        # Export with materials
        return self.export_meshes_to_gltf(meshes, unique_materials, output_path, zone_name)
    
    def create_waypoint_metadata(self, waypoints: List) -> Dict[str, Any]:
        """
        Create metadata for waypoints to include in glTF extras.
        
        Args:
            waypoints: List of waypoint data
            
        Returns:
            Dictionary containing waypoint metadata
        """
        waypoint_data = []
        
        for waypoint in waypoints:
            waypoint_info = {
                "x": waypoint.x,
                "y": waypoint.y,
                "z": waypoint.z,
                "zone_name": waypoint.zone_name,
                "description": waypoint.description,
                "special_visual": waypoint.special_visual
            }
            waypoint_data.append(waypoint_info)
        
        return {
            "waypoints": waypoint_data,
            "waypoint_count": len(waypoint_data)
        }
    
    def export_with_extras(self, meshes: List[MeshData],
                          materials: List[Material],
                          output_path: str,
                          zone_name: str = "unknown",
                          extras: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Export with additional metadata in glTF extras.
        
        Args:
            meshes: List of mesh data to export
            materials: List of materials to export
            output_path: Path to save the glTF file
            zone_name: Name of the zone for metadata
            extras: Additional metadata to include
            
        Returns:
            Dictionary containing export metadata
        """
        # Export basic glTF
        stats = self.export_meshes_to_gltf(meshes, materials, output_path, zone_name)
        
        # Add extras to the file if provided
        if extras:
            # Load the glTF file
            gltf = GLTF2.load(output_path)
            
            # Add extras to the asset
            if not hasattr(gltf.asset, 'extras'):
                gltf.asset.extras = {}
            
            gltf.asset.extras.update(extras)
            
            # Save updated file
            gltf.save(output_path)
            
            if self.verbose:
                self.logger.info(f"Added extras to glTF: {list(extras.keys())}")
        
        return stats 