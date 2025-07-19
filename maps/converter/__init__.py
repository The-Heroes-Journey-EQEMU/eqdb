"""
EQDB Map Converter Package

This package contains the tools for converting Brewall mapping format files
into 3D glTF models for Babylon.js rendering.

The converter supports:
- Brewall format parsing (.txt, _1.txt, _2.txt files)
- Coordinate system transformation
- 3D geometry generation
- glTF export with pygltflib
- Integration with existing EQDB map functions
- Waypoint data integration
- Color preservation from mapping standards
"""

__version__ = "1.0.0"
__author__ = "EQDB Development Team"

from .parser import BrewallParser
from .geometry import GeometryGenerator
from .exporter import GLTFExporter
from .utils import CoordinateTransformer, MapData, LineSegment, Label, Waypoint

__all__ = [
    'BrewallParser',
    'GeometryGenerator', 
    'GLTFExporter',
    'CoordinateTransformer',
    'MapData',
    'LineSegment',
    'Label',
    'Waypoint'
] 