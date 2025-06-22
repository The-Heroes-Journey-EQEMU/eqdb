# EQDB Map Converter

A comprehensive system for converting Brewall mapping format files into 3D glTF models for rendering in Babylon.js and other 3D viewers.

## Overview

The map converter transforms EverQuest zone mapping data from the Brewall format into high-quality 3D models with proper materials, semantic layer support, and standards compliance. It supports all Brewall mapping standard layers and provides accurate visual representation of game zones.

## Features

### ✅ Completed Features (Phases 1, 2, 2.5, 2.6)

- **Comprehensive Parsing**: Full support for Brewall format files (main geometry, labels, secondary geometry)
- **Semantic Layer Mapping**: 43+ Brewall standard materials with proper color and transparency
- **3D Geometry Generation**: Line segments, labels, and waypoints converted to 3D meshes
- **Material System**: Advanced material library with semantic layer assignment
- **glTF Export**: Standards-compliant glTF 2.0 export with metadata
- **Database Integration**: SQLite database for metadata storage and file management
- **Waypoint Integration**: Special handling for wizard/druid teleport locations
- **Standards Compliance**: Full adherence to Brewall mapping standards
- **Error Handling & Recovery**: Comprehensive error handling with detailed logging and recovery mechanisms
- **Performance Monitoring**: Real-time performance tracking with memory and CPU usage monitoring
- **Progress Tracking**: Progress indicators for long-running operations
- **Batch Processing**: Multi-zone processing with error recovery and retry logic
- **Memory Management**: Automatic memory monitoring and garbage collection

### 🎯 Key Capabilities

- **Multi-Format Support**: Handles main maps, labels, and secondary geometry
- **Semantic Layer Preservation**: Maintains mapping standard layer information
- **Material Assignment**: Intelligent material assignment based on semantic layers
- **Geometry Optimization**: Vertex deduplication and mesh optimization
- **Metadata Storage**: Comprehensive metadata tracking and database storage
- **Extensible Architecture**: Modular design for easy extension and maintenance
- **Robust Error Handling**: Graceful error recovery with detailed logging
- **Performance Optimization**: Memory and CPU monitoring with optimization suggestions

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

#### 6. Error Handling (`error_handler.py`)
- **ErrorHandler**: Comprehensive error handling and logging
- **PerformanceMonitor**: Real-time performance tracking
- **ProgressTracker**: Progress indicators for long operations
- **BatchProcessor**: Multi-zone processing with error recovery
- **MemoryManager**: Memory usage monitoring and optimization

#### 7. Coordinate Validation (`coordinate_validator.py`)
- **CoordinateValidator**: Coordinate system validation and analysis
- **Outlier Detection**: Automatic detection of coordinate anomalies
- **Transformation Suggestions**: Optimal coordinate transformations for Babylon.js
- **Range Analysis**: Comprehensive coordinate range analysis

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Dependencies
```bash
pip install pygltflib numpy click psutil
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
    meshes, material_assigner, "output.gltf", "zone_name"
)
```

### Advanced Usage with Error Handling

#### 1. Comprehensive Error Handling
```python
from error_handler import ErrorHandler, PerformanceMonitor, ProcessingStage

# Initialize error handling and performance monitoring
error_handler = ErrorHandler(verbose=True)
perf_monitor = PerformanceMonitor(verbose=True)

# Parse with error handling
with perf_monitor.monitor_stage(ProcessingStage.PARSING):
    try:
        map_data = parser.parse_zone("overthere")
    except Exception as e:
        error_handler.handle_error(
            ProcessingStage.PARSING, 
            f"Error parsing zone: {e}", 
            exception=e
        )

# Check for errors
if error_handler.has_critical_errors():
    print("Critical errors detected!")
    print(error_handler.get_error_summary())
```

#### 2. Performance Monitoring
```python
# Monitor geometry generation
with perf_monitor.monitor_stage(ProcessingStage.GEOMETRY_GENERATION):
    meshes = generator.generate_all_geometry(map_data)

# Get performance summary
summary = perf_monitor.get_performance_summary()
print(f"Total duration: {summary['total_duration']:.2f}s")
print(f"Memory usage: {summary['total_memory_mb']:.1f}MB")
```

#### 3. Batch Processing
```python
from error_handler import BatchProcessor

# Process multiple zones with error recovery
batch_processor = BatchProcessor(error_handler, perf_monitor)
zones = ["overthere", "kattacastrum", "iceclad"]

results = batch_processor.process_zones(
    zones, 
    processor_func=lambda zone: parser.parse_zone(zone),
    max_retries=2,
    continue_on_error=True
)

print(f"Successful: {len(results['successful'])}")
print(f"Failed: {len(results['failed'])}")
```

#### 4. Coordinate Validation
```python
from coordinate_validator import CoordinateValidator

validator = CoordinateValidator(verbose=True)
result = validator.validate_map_data(map_data)

if result.is_valid:
    print("Coordinate system is valid")
else:
    print(f"Issues found: {len(result.issues)}")
    for issue in result.issues:
        print(f"  - {issue}")

# Get transformation suggestions for Babylon.js
transform = validator.suggest_transformation(result)
print(f"Scale factor: {transform['scale_factor']}")
print(f"Offset: ({transform['offset_x']}, {transform['offset_y']}, {transform['offset_z']})")
```

### Testing

#### Run All Tests
```bash
# Complete workflow test
python3 test_phase2.py

# Geometry generation test
python3 test_geometry.py

# Coordinate validation test
python3 test_coordinate_validator.py
```

#### Test Specific Zones
```python
# Test coordinate validation for specific zones
from test_coordinate_validator import test_zone

test_zone("overthere")      # Medium zone
test_zone("kattacastrum")   # Dense zone
test_zone("iceclad")        # Large zone
```

## Performance Characteristics

### Typical Performance Metrics
- **Parsing**: 0.01-0.03s per zone
- **Geometry Generation**: 0.1-0.3s per zone
- **Validation**: 0.01-0.04s per zone
- **Memory Usage**: 55-65MB peak
- **CPU Usage**: 0.15-4.05%

### Optimization Results
- **Mesh Reduction**: 99.5% reduction through optimization
- **Vertex Deduplication**: Automatic vertex sharing
- **Memory Management**: Automatic garbage collection
- **Batch Processing**: Parallel zone processing support

## Error Handling

### Error Types
- **Parsing Errors**: File not found, malformed data, encoding issues
- **Geometry Errors**: Invalid coordinates, mesh generation failures
- **Export Errors**: File system issues, glTF validation failures
- **Database Errors**: Connection issues, constraint violations

### Error Recovery
- **Automatic Retries**: Configurable retry logic for transient failures
- **Graceful Degradation**: Continue processing other zones if one fails
- **Detailed Logging**: Comprehensive error context and stack traces
- **Error Summaries**: Concise error reports with severity levels

## Database Schema

### Zone Metadata Table
```sql
CREATE TABLE zone_geometry_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_short_name TEXT UNIQUE NOT NULL,
    zone_long_name TEXT NOT NULL,
    expansion_id INTEGER NOT NULL,
    gltf_file_path TEXT,
    file_size INTEGER,
    vertex_count INTEGER,
    triangle_count INTEGER,
    bounding_box_min_x REAL,
    bounding_box_min_y REAL,
    bounding_box_min_z REAL,
    bounding_box_max_x REAL,
    bounding_box_max_y REAL,
    bounding_box_max_z REAL,
    conversion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version TEXT DEFAULT '1.0',
    status TEXT DEFAULT 'parsed'
);
```

## File Structure

```
maps/converter/
├── parser.py              # Brewall format parser
├── geometry.py            # 3D geometry generator
├── materials.py           # Material system
├── exporter.py            # glTF export engine
├── database.py            # Database operations
├── error_handler.py       # Error handling and performance monitoring
├── coordinate_validator.py # Coordinate validation
├── test_phase2.py         # Complete workflow test
├── test_geometry.py       # Geometry generation test
├── test_coordinate_validator.py # Coordinate validation test
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive error handling to new features
3. Include performance monitoring for new operations
4. Write tests for new functionality
5. Update documentation for new features

## License

This project is part of the EQDB application and follows the same licensing terms.

## Support

For issues and questions:
1. Check the test logs for detailed error information
2. Review the MAP_CONVERSION_PLAN.md for implementation details
3. Examine the test scripts for usage examples
4. Check the database for metadata and file information
5. Review error summaries and performance metrics 