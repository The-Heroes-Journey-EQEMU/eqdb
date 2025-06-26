# Map Conversion Script - Comprehensive Development Plan

## Overview
This plan outlines the development of a map conversion system that transforms Brewall mapping format files into 3D glTF models for rendering in Babylon.js. The system will start with a proof of concept using the "overthere" zone and expand to support all available maps **up to the Planes of Power (PoP) expansion**.

## Scope Definition

### Expansion Coverage
- **Target Range**: Expansions 0-4 (Classic through Planes of Power)
- **Classic (0)**: Original EverQuest zones
- **Kunark (1)**: Ruins of Kunark expansion
- **Velious (2)**: Scars of Velious expansion  
- **Luclin (3)**: Shadows of Luclin expansion
- **Planes of Power (4)**: Planes of Power expansion
- **Excluded**: All expansions after PoP (Ykesha, LDoN, GoD, etc.)

### Zone Count Estimation
Based on the database structure and existing zone listings:
- **Classic**: ~50 zones
- **Kunark**: ~25 zones
- **Velious**: ~20 zones
- **Luclin**: ~15 zones
- **Planes of Power**: ~25 zones
- **Total Target**: ~135 zones (vs. 400+ total zones)

### Benefits of PoP Limitation
- **Reduced Scope**: ~65% reduction in total zones to process
- **Faster Development**: Focus on core game content
- **Better Testing**: More manageable validation process
- **User Focus**: Covers the most popular and classic content
- **Performance**: Smaller dataset for web delivery

## File Format Analysis

### Brewall Map File Structure
Based on analysis of `maps/brewall/overthere.txt`, `overthere_1.txt`, and `overthere_2.txt`:

#### Main Map File (e.g., `overthere.txt`)
- **Format**: `L x1, y1, z1, x2, y2, z2, r, g, b`
- **Type**: Line segments representing terrain, walls, and boundaries
- **Coordinates**: 3D world coordinates (x, y, z)
- **Colors**: RGB values (0-255) for line coloring
- **Purpose**: Primary geometry and terrain features

#### Label File (e.g., `overthere_1.txt`)
- **Format**: `P x, y, z, r, g, b, size, label_text`
- **Type**: Point markers with text labels
- **Coordinates**: 3D world coordinates for label placement
- **Colors**: RGB values for text color
- **Size**: Numeric value indicating text size/importance
- **Purpose**: NPCs, merchants, zones, points of interest

#### Secondary Geometry File (e.g., `overthere_2.txt`)
- **Format**: `L x1, y1, z1, x2, y2, z2, r, g, b`
- **Type**: Additional line segments (possibly UI elements, compass markers)
- **Purpose**: Secondary visual elements, compass rose, UI overlays

## Existing Map System Integration

### Current Map Functions in utils.py
The project already has basic map functionality that should be integrated:

#### `get_map_data(short_name)` - Line Segment Parser
- **Location**: `utils.py:2755`
- **Function**: Parses main map files (`.txt`) for line segments
- **Format**: Returns list of dictionaries with x1,y1,z1,x2,y2,z2 coordinates and RGB colors
- **Integration**: Can be enhanced for 3D conversion while maintaining backward compatibility

#### `get_map_poi(short_name)` - Point of Interest Parser
- **Location**: `utils.py:2775`
- **Function**: Parses point of interest files (`_1.txt`) for labels
- **Format**: Returns list of dictionaries with x,y,z coordinates, RGB colors, and label text
- **Integration**: Can be enhanced for 3D label generation

#### `get_zone_waypoint(short_name)` - Teleport Locations
- **Location**: `utils.py:51`
- **Function**: Provides hardcoded waypoint coordinates for each zone
- **Purpose**: Wizard/Druid teleport locations, zone entry points
- **Integration**: Should be added as special teleport markers in 3D viewer
- **Special Handling**: These should be highlighted as special teleport spots with distinct visual treatment

### File Management Strategy
- **Source Files**: `maps/brewall/*` files are in `.gitignore` (can be downloaded)
- **Generated Files**: `maps/output/` and `maps/viewer/` should be version controlled
- **Strategy**: Ignore source Brewall files, commit generated glTF and viewer assets

## Development Phases

### Phase 1: Foundation & Analysis (Week 1)
**Goal**: Establish the basic framework and understand the data structure

#### Task 1.1: Project Structure Setup
- [x] Create `maps/converter/` directory structure
- [x] Set up Python virtual environment
- [x] Install required dependencies:
  - [x] `pygltflib` for glTF generation
  - [x] `numpy` for coordinate processing
  - [x] `click` for CLI interface
  - [x] `logging` for verbose output
- [x] Update `.gitignore` to exclude `maps/brewall/*` but include `maps/output/` and `maps/viewer/`

#### Task 1.2: Enhanced File Parser Development
- [x] Create `MapParser` class to handle Brewall format
- [x] Enhance existing `get_map_data()` and `get_map_poi()` functions for 3D conversion
- [x] Implement line segment parsing (`L` records) with color preservation
- [x] Implement point label parsing (`P` records) with color preservation
- [x] Add coordinate system validation
- [x] Add color value validation according to mapping standards
- [x] Implement verbose logging for debugging
- [x] **NEW**: Integrate `get_zone_waypoint()` data as special teleport markers (now all waypoints are type 'waypoint', field removed)

#### Task 1.3: Data Structure Design
- [x] Define `LineSegment` class with coordinates and colors
- [x] Define `Label` class with position, color, size, and text
- [x] Define `Waypoint` class for teleport locations (special handling, no type field)
- [x] Define `MapData` class to hold all parsed elements
- [x] Implement data validation and error handling
- [x] **NEW**: Create unified interface that supports both 2D and 3D rendering

#### Task 1.4: Coordinate System Analysis
- [x] Analyze coordinate ranges and scales
- [x] Determine appropriate scaling factors for 3D rendering
- [x] Identify coordinate system transformations needed
- [x] Document coordinate system conventions
- [x] **NEW**: Map waypoint coordinates to 3D space

### Phase 2: Core Conversion Engine (Week 2)
**Goal**: Build the core conversion logic from parsed data to 3D geometry

#### Task 2.1: Geometry Generation
- [x] Create `GeometryGenerator` class
- [x] Implement line segment to 3D mesh conversion
- [x] Add line thickness and material properties
- [x] Implement coordinate scaling and transformation
- [x] Add geometry optimization (vertex deduplication)
- [x] **NEW**: Preserve original colors from mapping standards

#### Task 2.2: Material System
- [x] Create material definitions for different line types
- [x] Implement color-based material assignment
- [x] Add transparency support for water/air elements
- [x] Create material library for common elements
- [x] **NEW**: Special materials for waypoints and teleport locations

#### Task 2.3: Enhanced Label System
- [ ] Implement 3D text label generation
- [ ] Add label positioning and orientation
- [ ] Implement label scaling based on size parameter
- [ ] Add label visibility and culling logic
- [ ] **NEW**: Special visual treatment for waypoints (wizard/druid circles)

#### Task 2.4: glTF Export
- [x] Integrate `pygltflib` for glTF generation
- [x] Implement mesh export with proper indexing
- [x] Add material and texture export
- [x] Implement scene graph structure
- [x] Add metadata and asset information
- [x] **NEW**: Include waypoint metadata in glTF

#### Task 2.5: Brewall Standards Layer Mapping (COMPLETED ✅)
- [x] Create a mapping table from Brewall standard RGB colors to semantic layer/type names (e.g., wall, door, water, lava, zone_line, etc.)
- [x] Expand `MaterialLibrary` to include a material for each Brewall semantic layer/type, with correct color, transparency, and properties
- [x] Update the parser to tag each line segment with its semantic type (if the color matches a known standard)
- [x] Update the `MaterialAssigner` to assign materials by semantic type, not just by color
- [x] Ensure all Brewall mapping standard layers are visually and semantically represented in the 3D output

**Phase 2.5 Summary**: Successfully implemented comprehensive semantic layer material mapping system with 43+ Brewall standard materials, enhanced geometry generation with semantic layer preservation, and standards-compliant material assignment. All Brewall mapping standard layers are now properly represented with appropriate materials for accurate 3D visualization.

### Phase 3: Proof of Concept - Overthere Zone (Week 3)
**Goal**: Complete end-to-end conversion of the overthere zone

#### Task 3.1: Single Zone Conversion
- [ ] Convert `overthere.txt` to 3D geometry
- [ ] Convert `overthere_1.txt` to 3D labels
- [ ] Convert `overthere_2.txt` to secondary geometry
- [ ] **NEW**: Add waypoint data from `get_zone_waypoint('overthere')`
- [ ] Generate complete glTF file
- [ ] Validate glTF file structure and content

#### Task 3.2: Babylon.js Integration
- [ ] Create basic Babylon.js viewer
- [ ] Implement Arc Rotate Camera with mouse controls
- [ ] Add zoom, pan, and rotate functionality
- [ ] Implement proper lighting setup
- [ ] Add label rendering and interaction
- [ ] **NEW**: Special waypoint visualization and interaction

#### Task 3.3: Visual Validation
- [ ] Compare rendered output with original map
- [ ] Verify coordinate accuracy and scaling
- [ ] Test label positioning and readability
- [ ] Validate color reproduction from mapping standards
- [ ] **NEW**: Verify waypoint placement accuracy
- [ ] Performance testing and optimization

#### Task 3.4: Documentation and Testing
- [ ] Create usage documentation
- [ ] Write unit tests for core components
- [ ] Create integration tests
- [ ] Document coordinate system and transformations
- [ ] **NEW**: Test backward compatibility with existing map functions

### Phase 4: Enhanced Features (Week 4)
**Goal**: Add advanced features and optimizations

#### Task 4.1: Performance Optimization
- [ ] Implement geometry batching
- [ ] Add level-of-detail (LOD) system
- [ ] Optimize vertex and index buffers
- [ ] Implement frustum culling
- [ ] Add geometry compression

#### Task 4.2: Interactive Features
- [ ] Add click-to-select functionality
- [ ] Implement label highlighting
- [ ] Add search and filter capabilities
- [ ] Create zone boundary visualization
- [ ] Add pathfinding visualization
- [ ] **NEW**: Waypoint teleport simulation/visualization
- [ ] **NEW**: Add Height filtering, to show layers

#### Task 4.3: Advanced Rendering
- [ ] Implement custom shaders for terrain
- [ ] Add water and special effects
- [ ] Implement day/night lighting
- [ ] Add atmospheric effects
- [ ] Create minimap overlay
- [ ] **NEW**: Special effects for waypoints (particles, glow, etc.)

#### Task 4.4: Export Options
- [ ] Add multiple glTF format options (binary/text)
- [ ] Implement OBJ export for compatibility
- [ ] Add FBX export option
- [ ] Create compressed archive formats
- [ ] Add batch processing capabilities

### Phase 5: Multi-Zone Support (Week 5)
**Goal**: Extend the system to handle all available zones up to PoP

#### Task 5.1: Batch Processing
- [ ] Create zone discovery and enumeration for expansions 0-4
- [ ] Implement parallel processing
- [ ] Add progress tracking and reporting
- [ ] Create error handling and recovery
- [ ] Add validation and quality checks
- [ ] **NEW**: Process all waypoint data for available zones
- [ ] **NEW**: Filter zones by expansion ID (0-4 only)

#### Task 5.2: Zone Management
- [ ] Create zone metadata system
- [ ] Implement zone categorization by expansion
- [ ] Add zone relationship mapping
- [ ] Create zone search and filtering
- [ ] Implement zone comparison tools
- [ ] **NEW**: Waypoint network visualization across zones
- [ ] **NEW**: Expansion-based zone grouping

#### Task 5.3: Database Integration
- [ ] Integrate with existing EQDB database
- [ ] Add zone information lookup with expansion filtering
- [ ] Implement NPC and item placement
- [ ] Add quest and spawn point visualization
- [ ] Create dynamic content updates
- [ ] **NEW**: Link waypoints to zone database entries
- [ ] **NEW**: Filter NPC spawns by expansion (0-4)

#### Task 5.4: Web Integration
- [ ] Create web-based viewer
- [ ] Add zone selection interface with expansion filtering
- [ ] Implement user preferences
- [ ] Add sharing and export features
- [ ] Create mobile-responsive design

### Phase 6: Production Deployment (Week 6)
**Goal**: Prepare the system for production use

#### Task 6.1: Quality Assurance
- [ ] Comprehensive testing of all PoP-era zones
- [ ] Performance benchmarking
- [ ] Memory usage optimization
- [ ] Error handling and logging
- [ ] Security review and hardening
- [ ] **NEW**: Waypoint accuracy verification across all zones
- [ ] **NEW**: Expansion coverage validation

#### Task 6.2: Documentation
- [ ] Complete API documentation
- [ ] User manual and tutorials
- [ ] Developer documentation
- [ ] Deployment guide
- [ ] Troubleshooting guide

#### Task 6.3: Integration
- [ ] Integrate with main EQDB application
- [ ] Add map viewer to web interface
- [ ] Implement user authentication
- [ ] Add admin controls and management
- [ ] Create monitoring and analytics
- [ ] **NEW**: Maintain backward compatibility with existing map functions

#### Task 6.4: Deployment
- [ ] Set up production environment
- [ ] Configure automated builds
- [ ] Implement CI/CD pipeline
- [ ] Set up monitoring and alerting
- [ ] Create backup and recovery procedures

### Phase 7: NPC Spawn Integration (Week 7)
**Goal**: Add dynamic NPC spawn data from the game database for questing and NPC hunting

#### Task 7.1: Database Schema Analysis
- [ ] Analyze existing NPC spawn tables: `Spawn2`, `SpawnEntry`, `SpawnGroup`, `NPCTypes`
- [ ] Map coordinate systems between database and map files
- [ ] Identify spawn group relationships and NPC variations
- [ ] Document respawn timers and spawn conditions
- [ ] **NEW**: Create spawn data extraction utilities
- [ ] **NEW**: Filter spawns by expansion (0-4 only)

#### Task 7.2: NPC Spawn Visualization
- [ ] Create `NPCSpawn` class for spawn point data
- [ ] Implement spawn point 3D markers with distinct visual treatment
- [ ] Add spawn group visualization (multiple NPCs at same location)
- [ ] Implement respawn timer visualization
- [ ] **NEW**: Add spawn condition indicators (time-based, trigger-based, etc.)

#### Task 7.3: Quest Integration
- [ ] Link NPC spawns to quest data from database
- [ ] Implement quest NPC highlighting and filtering
- [ ] Add quest chain visualization across multiple spawns
- [ ] Create quest progress tracking in 3D viewer
- [ ] **NEW**: Quest-specific spawn point highlighting

#### Task 7.4: Interactive NPC Features
- [ ] Add click-to-highlight NPC spawn functionality
- [ ] Implement NPC search and filter by name, level, race, class
- [ ] Add spawn point information tooltips
- [ ] Create NPC path visualization (if movement data available)
- [ ] **NEW**: Zoom-to-NPC functionality for quest targets

#### Task 7.5: Advanced Spawn Features
- [ ] Implement spawn density heat maps
- [ ] Add spawn time-based filtering (day/night spawns)
- [ ] Create spawn group relationship visualization
- [ ] Add spawn condition indicators (faction requirements, etc.)
- [ ] **NEW**: Spawn prediction based on respawn timers

#### Task 7.6: Performance Optimization
- [ ] Implement spawn data caching and lazy loading
- [ ] Add spawn point clustering for dense areas
- [ ] Optimize spawn marker rendering for large zones
- [ ] Create spawn data compression for web delivery
- [ ] **NEW**: Progressive spawn loading based on camera position

## Technical Specifications

### File Structure
```
maps/
├── converter/
│   ├── __init__.py
│   ├── parser.py          # Enhanced Brewall format parser
│   ├── geometry.py        # 3D geometry generation
│   ├── materials.py       # Material definitions
│   ├── exporter.py        # glTF export functionality
│   ├── viewer.py          # Babylon.js viewer
│   ├── utils.py           # Utility functions
│   ├── spawns.py          # NPC spawn integration (Phase 7)
│   └── tests/             # Test suite
├── output/                # Generated glTF files (version controlled)
├── viewer/                # Babylon.js viewer files (version controlled)
├── brewall/               # Source files (gitignored)
└── docs/                  # Documentation
```

### Dependencies
```python
# Core dependencies
pygltflib>=1.15.0
numpy>=1.21.0
click>=8.0.0

# Optional dependencies
trimesh>=3.9.0  # For advanced geometry processing
pillow>=8.0.0   # For texture processing
```

### API Design
```python
class MapConverter:
    def __init__(self, config: ConverterConfig):
        """Initialize converter with configuration"""
        
    def parse_zone(self, zone_name: str) -> MapData:
        """Parse all files for a given zone including waypoints"""
        
    def convert_to_gltf(self, map_data: MapData) -> glTF:
        """Convert parsed data to glTF format"""
        
    def export_zone(self, zone_name: str, output_path: str):
        """Complete conversion and export of a zone"""
        
    def batch_convert(self, zone_list: List[str], output_dir: str):
        """Convert multiple zones in batch"""
        
    def get_waypoint_data(self, zone_name: str) -> WaypointData:
        """Get waypoint data for a zone"""
        
    # Phase 7 additions
    def get_npc_spawns(self, zone_name: str) -> List[NPCSpawn]:
        """Get NPC spawn data for a zone from database"""
        
    def highlight_quest_npcs(self, quest_id: int) -> List[NPCSpawn]:
        """Highlight NPCs related to a specific quest"""
        
    def search_npcs(self, search_term: str, zone_name: str = None) -> List[NPCSpawn]:
        """Search for NPCs by name, level, race, or class"""
        
    # Expansion filtering
    def get_zones_by_expansion(self, max_expansion: int = 4) -> List[str]:
        """Get zones up to specified expansion (default: PoP)"""
```

### Enhanced Data Structures
```python
class LineSegment:
    x1, y1, z1: float  # Start coordinates
    x2, y2, z2: float  # End coordinates
    r, g, b: int       # RGB color values (0-255)
    
class Label:
    x, y, z: float     # Position coordinates
    r, g, b: int       # RGB color values (0-255)
    size: int          # Text size/importance
    text: str          # Label text
    
class Waypoint:
    x, y, z: float     # Position coordinates
    zone_name: str     # Zone name
    waypoint_type: str # "wizard", "druid", "zone_entry", etc.
    special_visual: bool # Whether to use special visual treatment

# Phase 7 additions
class NPCSpawn:
    x, y, z: float     # Spawn coordinates
    npc_id: int        # NPC ID from database
    npc_name: str      # NPC name
    level: int         # NPC level
    race: str          # NPC race
    class_type: str    # NPC class
    respawn_time: int  # Respawn timer in seconds
    spawn_group: str   # Spawn group name
    spawn_id: int      # Spawn2 ID
    group_id: int      # SpawnGroup ID
    chance: float      # Spawn chance percentage
    quest_related: bool # Whether NPC is related to active quests
    special_visual: bool # Whether to use special visual treatment
    expansion: int     # Expansion ID (0-4 for PoP era)
```

## Success Criteria

### Phase 1 Success
- [ ] Successfully parse overthere zone files
- [ ] Extract all line segments and labels
- [ ] **NEW**: Include waypoint data from existing utils.py function
- [ ] Validate coordinate and color data
- [ ] Generate comprehensive logging output
- [ ] Maintain backward compatibility with existing map functions

### Phase 2 Success
- [ ] Generate valid glTF files
- [ ] Maintain coordinate accuracy
- [ ] Preserve color information from mapping standards
- [ ] Include proper material definitions
- [ ] **NEW**: Special waypoint visualization

### Phase 3 Success
- [ ] Render overthere zone in Babylon.js
- [ ] Display all geometry and labels correctly
- [ ] **NEW**: Show waypoints as special teleport locations
- [ ] Implement camera controls
- [ ] Achieve acceptable performance

### Phase 4 Success
- [ ] Optimize rendering performance
- [ ] Add interactive features
- [ ] Implement advanced visual effects
- [ ] Support multiple export formats
- [ ] **NEW**: Enhanced waypoint interaction
- [ ] **NEW**: Height filtering functionality

### Phase 5 Success
- [ ] Convert all PoP-era zones (expansions 0-4)
- [ ] Implement batch processing
- [ ] Integrate with EQDB database
- [ ] Create web-based interface
- [ ] **NEW**: Complete waypoint network across all zones
- [ ] **NEW**: Expansion-based zone filtering

### Phase 6 Success
- [ ] Deploy to production environment
- [ ] Achieve production-level performance
- [ ] Complete documentation
- [ ] User acceptance testing
- [ ] **NEW**: Maintain full backward compatibility
- [ ] **NEW**: Validate PoP-era coverage

### Phase 7 Success
- [ ] **NEW**: Successfully integrate NPC spawn data from database
- [ ] **NEW**: Display spawn points with distinct visual treatment
- [ ] **NEW**: Implement quest NPC highlighting and zoom functionality
- [ ] **NEW**: Add NPC search and filtering capabilities
- [ ] **NEW**: Create spawn density and relationship visualizations
- [ ] **NEW**: Achieve acceptable performance with large numbers of spawns
- [ ] **NEW**: Filter spawns by PoP-era expansions only

## Risk Mitigation

### Technical Risks
- **Coordinate System Complexity**: Start with simple zones, document transformations
- **Performance Issues**: Implement progressive loading and LOD systems
- **File Format Variations**: Create robust parsing with error handling
- **Browser Compatibility**: Test across multiple browsers and devices
- **Backward Compatibility**: Ensure existing map functions continue to work
- **Database Performance**: Optimize spawn data queries and caching

### Timeline Risks
- **Scope Creep**: Focus on core functionality first, add features incrementally
- **Dependency Issues**: Use stable, well-maintained libraries
- **Integration Complexity**: Maintain clear interfaces and documentation

### Quality Risks
- **Data Accuracy**: Implement comprehensive validation and testing
- **Visual Quality**: Establish clear quality standards and review process
- **User Experience**: Conduct user testing and gather feedback
- **Color Accuracy**: Ensure mapping standard colors are preserved exactly
- **Spawn Data Accuracy**: Validate NPC spawn coordinates and relationships

## Future Enhancements

### Advanced Features
- **Real-time Updates**: Live zone data updates
- **User Annotations**: Allow users to add notes and markers
- **Pathfinding**: Visual pathfinding between points
- **Mobile Support**: Native mobile applications
- **VR/AR Support**: Virtual and augmented reality viewing
- **Waypoint Networks**: Visualize teleport networks across zones
- **NPC Movement**: Track and visualize NPC movement patterns
- **Spawn Prediction**: Predict spawn times based on historical data

### Integration Opportunities
- **Discord Bot**: Zone information and navigation
- **Mobile App**: Standalone mobile application
- **API Services**: Public API for third-party integrations
- **Analytics**: Usage analytics and insights
- **Quest Tracking**: Integration with quest tracking systems

## Key Discoveries and Integration Points

### Existing Map System
- **Current Functions**: `get_map_data()`, `get_map_poi()`, `get_zone_waypoint()` in utils.py
- **Integration Strategy**: Enhance existing functions while maintaining backward compatibility
- **Waypoint Data**: Hardcoded teleport locations for each zone should be special markers
- **Color Preservation**: Must maintain exact colors from mapping standards

### Database Integration
- **NPC Spawn Tables**: `Spawn2`, `SpawnEntry`, `SpawnGroup`, `NPCTypes` contain spawn data
- **Coordinate Mapping**: Database coordinates need transformation to map coordinate system
- **Quest Integration**: NPC spawns can be linked to quest data for highlighting
- **Performance**: Large numbers of spawns require optimization strategies
- **Expansion Filtering**: Focus on expansions 0-4 (Classic through PoP)

### File Management
- **Source Files**: `maps/brewall/*` files are gitignored (downloadable)
- **Generated Files**: `maps/output/` and `maps/viewer/` should be version controlled
- **Strategy**: Ignore source, commit generated assets

### Backward Compatibility
- **Existing Usage**: NPC and zone pages use `utils.get_map_data()`
- **Requirement**: Must maintain existing 2D map functionality
- **Solution**: Create unified interface supporting both 2D and 3D rendering

### Scope Benefits
- **Reduced Complexity**: ~135 zones vs. 400+ total zones
- **Faster Development**: Focus on core game content
- **Better Testing**: More manageable validation process
- **User Focus**: Covers the most popular and classic content
- **Performance**: Smaller dataset for web delivery

This plan provides a comprehensive roadmap for developing the map conversion system, with clear phases, tasks, and success criteria. Each phase builds upon the previous one, ensuring a solid foundation and incremental feature development while integrating with existing functionality. The addition of NPC spawn integration in Phase 7 will make the 3D maps incredibly useful for questing and NPC hunting, with features like quest NPC highlighting, zoom-to-NPC functionality, and spawn point visualization. The PoP-era scope limitation ensures the project remains manageable while covering the most important and popular game content. 