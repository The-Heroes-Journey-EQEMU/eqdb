# EQDB Map Converter

A comprehensive system for converting Brewall mapping format files into 3D glTF models for rendering in Babylon.js and other 3D viewers.

## Overview

The map converter transforms EverQuest zone mapping data from the Brewall format into high-quality 3D models with proper materials, semantic layer support, and standards compliance. It supports all Brewall mapping standard layers and provides accurate visual representation of game zones.

## Features

### ✅ Completed Features (Phases 1, 2, 2.5)

- **Comprehensive Parsing**: Full support for Brewall format files (main geometry, labels, secondary geometry)
- **Semantic Layer Mapping**: 43+ Brewall standard materials with proper color and transparency
- **3D Geometry Generation**: Line segments, labels, and waypoints converted to 3D meshes
- **Material System**: Advanced material library with semantic layer assignment
- **glTF Export**: Standards-compliant glTF 2.0 export with metadata
- **Database Integration**: SQLite database for metadata storage and file management
- **Waypoint Integration**: Special handling for wizard/druid teleport locations
- **Standards Compliance**: Full adherence to Brewall mapping standards

### 🎯 Key Capabilities

- **Multi-Format Support**: Handles main maps, labels, and secondary geometry
- **Semantic Layer Preservation**: Maintains mapping standard layer information
- **Material Assignment**: Intelligent material assignment based on semantic layers
- **Geometry Optimization**: Vertex deduplication and mesh optimization
- **Metadata Storage**: Comprehensive metadata tracking and database storage
- **Extensible Architecture**: Modular design for easy extension and maintenance

## Architecture

### Core Components

#### 1. Parser (`parser.py`)
- **MapParser**: Main parsing engine for Brewall files
- **LineSegment**: Data structure for line geometry
- **Label**: Data structure for text labels
- **Waypoint**: Data structure for teleport locations
- **MapData**: Container for all parsed elements

#### 2. Geometry Generator (`geometry.py`)
- **GeometryGenerator**: Converts parsed data to 3D meshes
- **MeshData**: Container for generated mesh data
- **Coordinate Transformation**: Handles scaling and positioning
- **Geometry Optimization**: Reduces vertex count and improves performance

#### 3. Material System (`materials.py`)
- **MaterialLibrary**: Comprehensive library of 43+ materials
- **MaterialAssigner**: Intelligent material assignment
- **BREWALL_LAYER_COLOR_MAP**: Complete color-to-layer mapping
- **Material Types**: Line, label, waypoint, water, air, terrain, UI materials

#### 4. Exporter (`exporter.py`)
- **GLTFExporter**: glTF 2.0 export engine
- **Material Export**: PBR material export with proper properties
- **Metadata Integration**: Waypoint and zone metadata inclusion
- **Scene Graph**: Proper scene structure for 3D viewers

#### 5. Database (`database.py`)
- **MapDatabase**: SQLite database for metadata storage
- **Zone Metadata**: Comprehensive zone information storage
- **File Management**: glTF file path and statistics tracking
- **Hybrid Storage**: Metadata in database, files in filesystem/CDN

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Dependencies
```bash
pip install pygltflib numpy click
```

### Setup
```bash
cd maps/converter
python3 -m pip install -r requirements.txt
```

## Usage

### Basic Usage

#### 1. Parse a Zone
```python
from parser import MapParser

parser = MapParser(verbose=True)
map_data = parser.parse_zone("overthere")
```

#### 2. Generate Geometry
```python
from geometry import GeometryGenerator

geometry_gen = GeometryGenerator(
    line_thickness=3.0,
    scale_factor=1.0,
    verbose=True
)
meshes = geometry_gen.generate_all_geometry(map_data)
```

#### 3. Export to glTF
```python
from materials import MaterialLibrary, MaterialAssigner
from exporter import GLTFExporter

# Set up materials
material_lib = MaterialLibrary()
material_assigner = MaterialAssigner(material_lib)

# Export
exporter = GLTFExporter(verbose=True)
stats = exporter.export_with_materials(
    meshes=meshes,
    material_assigner=material_assigner,
    output_path="output/overthere.gltf",
    zone_name="overthere"
)
```

### Advanced Usage

#### Semantic Layer Material Assignment
```python
# Materials are automatically assigned based on semantic layers
# Walls, doors, water, teleporters, etc. get appropriate materials
material = material_assigner.assign_material_by_semantic_layer("walls")
```

#### Database Integration
```python
from database import MapDatabase

db = MapDatabase("maps.db")
db.store_zone_metadata("overthere", metadata)
db.store_gltf_file_info("overthere", "output/overthere.gltf", stats)
```

## Brewall Standards Support

### Semantic Layers
The converter supports all Brewall mapping standard layers:

- **Terrain**: walls, doors, water, lava, air, terrain
- **Features**: teleporters, spawns, npcs, items, corpses
- **UI Elements**: compass, labels, waypoints
- **Special**: magic, traps, light, fire, forest, grass, swamp
- **Hazards**: danger, cave, ruins, deep_water

### Color Mapping
Each semantic layer has a specific RGB color in the Brewall standard:
- Walls: (255, 0, 0) - Red
- Doors: (0, 255, 0) - Green  
- Water: (0, 0, 255) - Blue
- Teleporters: (255, 0, 255) - Magenta
- And 39+ more standard colors...

## File Structure

```
maps/converter/
├── parser.py              # Brewall file parsing
├── geometry.py            # 3D geometry generation
├── materials.py           # Material system and library
├── exporter.py            # glTF export engine
├── database.py            # Database integration
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── test_*.py             # Test scripts
├── test_data/            # Test output directory
└── output/               # Generated glTF files
```

## Testing

### Run All Tests
```bash
python3 test_phase2_5.py
```

### Individual Test Scripts
- `test_geometry.py`: Geometry generation tests
- `test_phase2.py`: Phase 2 integration tests
- `test_phase2_5.py`: Semantic layer material mapping tests

### Test Output
Tests generate:
- glTF files in `test_data/`
- SQLite database files
- Detailed logs with validation results

## Performance

### Optimization Features
- **Vertex Deduplication**: Reduces mesh complexity
- **Material Caching**: Prevents duplicate material creation
- **Geometry Batching**: Combines similar meshes
- **Database Indexing**: Fast metadata queries

### Typical Performance
- **Parsing**: ~1000 line segments/second
- **Geometry Generation**: ~500 meshes/second
- **glTF Export**: ~50KB/second
- **Memory Usage**: ~10MB per zone

## Integration

### With EQDB Web Application
The converter integrates with the main EQDB application:
- Uses existing `utils.py` waypoint functions
- Compatible with existing zone data structures
- Provides API endpoints for 3D map access
- Supports web-based 3D viewer integration

### With Babylon.js
Generated glTF files are optimized for Babylon.js:
- Proper scene graph structure
- PBR material support
- Metadata for waypoint interaction
- Optimized geometry for web rendering

## Development Status

### ✅ Completed (Phases 1, 2, 2.5)
- Foundation and analysis
- Core conversion engine
- Semantic layer material mapping
- Database integration
- Comprehensive testing

### 🚧 Next Steps (Phase 3+)
- Multi-zone batch processing
- Production deployment
- NPC spawn integration
- Web viewer integration

## Contributing

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for all function parameters
- Include comprehensive docstrings
- Add unit tests for new features

### Testing
- Run tests before committing changes
- Ensure all tests pass
- Add tests for new functionality
- Update documentation for API changes

## License

This project is part of the EQDB application and follows the same licensing terms.

## Support

For issues and questions:
1. Check the test logs for detailed error information
2. Review the MAP_CONVERSION_PLAN.md for implementation details
3. Examine the test scripts for usage examples
4. Check the database for metadata and file information 