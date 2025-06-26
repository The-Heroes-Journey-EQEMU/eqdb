# Database Storage and Conversion Process Analysis

## Database Storage Options for Zone Geometry

### Overview
This document analyzes the optimal database storage strategy for 3D zone geometry data and provides a detailed explanation of the conversion process from Brewall mapping format to Babylon.js rendering.

**Update:**
- The hybrid approach is the recommended and implemented solution: glTF files are stored in the filesystem (or CDN) for fast serving, and only metadata (zone info, file path, stats, waypoints) is stored in the database for queries and relationships.
- 3D geometry is never stored as rows in the database—only as files.
- All waypoints are now of type 'waypoint'.

## Database Storage Strategy

### Option 1: File-Based Storage (Recommended for Initial Implementation)

#### Advantages
- **Simplicity**: Direct glTF file storage in filesystem
- **Performance**: Fast file serving, no database queries
- **Caching**: Browser and CDN caching work naturally
- **Version Control**: Easy to track changes in git
- **Scalability**: Files can be served from CDN
- **Backup**: Simple file-based backup strategy

#### Implementation
```python
# File structure
maps/
├── output/
│   ├── gltf/
│   │   ├── classic/
│   │   │   ├── qeynos.gltf
│   │   │   ├── freeport.gltf
│   │   │   └── ...
│   │   ├── kunark/
│   │   ├── velious/
│   │   ├── luclin/
│   │   └── pop/
│   ├── metadata/
│   │   ├── zones.json          # Zone metadata and file references
│   │   ├── waypoints.json      # Waypoint data
│   │   └── spawns.json         # NPC spawn data (Phase 7)
│   └── viewer/
│       ├── index.html          # Babylon.js viewer
│       ├── viewer.js           # Viewer logic
│       └── styles.css          # Viewer styling
```

#### Database Schema for Metadata
```sql
-- Zone metadata table (SQLite for local storage)
CREATE TABLE zone_geometry_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_short_name TEXT UNIQUE NOT NULL,
    zone_long_name TEXT NOT NULL,
    expansion_id INTEGER NOT NULL,
    gltf_file_path TEXT NOT NULL,
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
    status TEXT DEFAULT 'converted' -- 'converted', 'processing', 'error'
);

-- Waypoint data table
CREATE TABLE zone_waypoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_short_name TEXT NOT NULL,
    waypoint_type TEXT NOT NULL, -- 'wizard', 'druid', 'zone_entry'
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    heading REAL DEFAULT 0.0,
    description TEXT,
    special_visual BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (zone_short_name) REFERENCES zone_geometry_metadata(zone_short_name)
);

-- NPC spawn data table (Phase 7)
CREATE TABLE zone_spawns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_short_name TEXT NOT NULL,
    npc_id INTEGER NOT NULL,
    npc_name TEXT NOT NULL,
    x REAL NOT NULL,
    y REAL NOT NULL,
    z REAL NOT NULL,
    heading REAL DEFAULT 0.0,
    level INTEGER,
    race TEXT,
    class_type TEXT,
    respawn_time INTEGER,
    spawn_group TEXT,
    spawn_id INTEGER,
    group_id INTEGER,
    chance REAL,
    quest_related BOOLEAN DEFAULT FALSE,
    expansion_id INTEGER NOT NULL,
    FOREIGN KEY (zone_short_name) REFERENCES zone_geometry_metadata(zone_short_name)
);
```

### Option 2: Binary Database Storage

#### Advantages
- **Centralized**: All data in one database
- **Transactions**: ACID compliance for data integrity
- **Querying**: SQL queries for metadata and relationships
- **Backup**: Single database backup strategy

#### Disadvantages
- **Performance**: Slower than file serving for large glTF files
- **Complexity**: More complex implementation
- **Memory**: Database must load entire glTF into memory
- **Caching**: More complex caching strategy needed

#### Implementation
```sql
-- Binary storage table
CREATE TABLE zone_geometry_binary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_short_name TEXT UNIQUE NOT NULL,
    gltf_data BLOB NOT NULL,           -- Binary glTF data
    gltf_size INTEGER NOT NULL,
    compression_type TEXT DEFAULT 'none', -- 'none', 'gzip', 'lz4'
    metadata TEXT,                     -- JSON metadata
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version TEXT DEFAULT '1.0'
);
```

### Option 3: Hybrid Approach (Recommended for Production)

#### Strategy
- **glTF Files**: Store in filesystem/CDN for fast serving
- **Metadata**: Store in database for querying and relationships
- **Caching**: Redis/Memcached for frequently accessed metadata

#### Implementation
```python
class ZoneGeometryDB:
    def __init__(self, db_path: str, file_storage_path: str):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.file_storage_path = file_storage_path
        
    def store_zone_geometry(self, zone_name: str, gltf_data: bytes, metadata: dict):
        """Store glTF file and metadata"""
        # Store file
        file_path = f"{self.file_storage_path}/{zone_name}.gltf"
        with open(file_path, 'wb') as f:
            f.write(gltf_data)
            
        # Store metadata
        with self.engine.connect() as conn:
            conn.execute(text("""
                INSERT OR REPLACE INTO zone_geometry_metadata 
                (zone_short_name, zone_long_name, expansion_id, gltf_file_path, 
                 file_size, vertex_count, triangle_count, bounding_box_min_x, 
                 bounding_box_min_y, bounding_box_min_z, bounding_box_max_x, 
                 bounding_box_max_y, bounding_box_max_z, version, status)
                VALUES (:zone_name, :long_name, :expansion_id, :file_path,
                        :file_size, :vertex_count, :triangle_count, :min_x,
                        :min_y, :min_z, :max_x, :max_y, :max_z, :version, 'converted')
            """), {
                'zone_name': zone_name,
                'long_name': metadata['long_name'],
                'expansion_id': metadata['expansion_id'],
                'file_path': file_path,
                'file_size': len(gltf_data),
                'vertex_count': metadata['vertex_count'],
                'triangle_count': metadata['triangle_count'],
                'min_x': metadata['bounding_box']['min_x'],
                'min_y': metadata['bounding_box']['min_y'],
                'min_z': metadata['bounding_box']['min_z'],
                'max_x': metadata['bounding_box']['max_x'],
                'max_y': metadata['bounding_box']['max_y'],
                'max_z': metadata['bounding_box']['max_z'],
                'version': '1.0'
            })
            conn.commit()
    
    def get_zone_geometry_url(self, zone_name: str) -> str:
        """Get URL for zone geometry file"""
        return f"/maps/output/gltf/{zone_name}.gltf"
    
    def get_zone_metadata(self, zone_name: str) -> dict:
        """Get zone metadata from database"""
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT * FROM zone_geometry_metadata 
                WHERE zone_short_name = :zone_name
            """), {'zone_name': zone_name}).fetchone()
            
            if result:
                return dict(result._mapping)
            return None
```

## Conversion Process: Brewall to Babylon.js

### Step 1: Brewall Format Parsing

#### File Structure Analysis
```python
class BrewallParser:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        
    def parse_zone_files(self, zone_name: str) -> MapData:
        """Parse all Brewall files for a zone"""
        map_data = MapData(zone_name)
        
        # Parse main geometry file
        main_file = f"maps/brewall/{zone_name}.txt"
        if os.path.exists(main_file):
            self.logger.info(f"Parsing main geometry file: {main_file}")
            map_data.line_segments = self._parse_line_segments(main_file)
        
        # Parse label file
        label_file = f"maps/brewall/{zone_name}_1.txt"
        if os.path.exists(label_file):
            self.logger.info(f"Parsing label file: {label_file}")
            map_data.labels = self._parse_labels(label_file)
        
        # Parse secondary geometry file
        secondary_file = f"maps/brewall/{zone_name}_2.txt"
        if os.path.exists(secondary_file):
            self.logger.info(f"Parsing secondary geometry file: {secondary_file}")
            map_data.secondary_segments = self._parse_line_segments(secondary_file)
        
        # Add waypoint data
        waypoint_data = utils.get_zone_waypoint(zone_name)
        if waypoint_data:
            self.logger.info(f"Adding waypoint data for zone: {zone_name}")
            map_data.waypoints = self._create_waypoints(waypoint_data, zone_name)
        
        return map_data
    
    def _parse_line_segments(self, file_path: str) -> List[LineSegment]:
        """Parse line segments from Brewall format"""
        segments = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line.startswith('L'):
                    try:
                        parts = line.split()
                        if len(parts) >= 10:
                            segment = LineSegment(
                                x1=float(parts[1].strip(',')),
                                y1=float(parts[2].strip(',')),
                                z1=float(parts[3].strip(',')),
                                x2=float(parts[4].strip(',')),
                                y2=float(parts[5].strip(',')),
                                z2=float(parts[6].strip(',')),
                                r=int(parts[7].strip(',')),
                                g=int(parts[8].strip(',')),
                                b=int(parts[9].strip(','))
                            )
                            segments.append(segment)
                        else:
                            self.logger.warning(f"Invalid line format at line {line_num}: {line}")
                    except (ValueError, IndexError) as e:
                        self.logger.error(f"Error parsing line {line_num}: {line} - {e}")
        
        self.logger.info(f"Parsed {len(segments)} line segments from {file_path}")
        return segments
    
    def _parse_labels(self, file_path: str) -> List[Label]:
        """Parse labels from Brewall format"""
        labels = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line.startswith('P'):
                    try:
                        parts = line.split()
                        if len(parts) >= 9:
                            # Extract label text (everything after size)
                            size = int(parts[7].strip(','))
                            label_text = ' '.join(parts[8:]).replace('_', ' ')
                            
                            label = Label(
                                x=float(parts[1].strip(',')),
                                y=float(parts[2].strip(',')),
                                z=float(parts[3].strip(',')),
                                r=int(parts[4].strip(',')),
                                g=int(parts[5].strip(',')),
                                b=int(parts[6].strip(',')),
                                size=size,
                                text=label_text
                            )
                            labels.append(label)
                        else:
                            self.logger.warning(f"Invalid label format at line {line_num}: {line}")
                    except (ValueError, IndexError) as e:
                        self.logger.error(f"Error parsing label at line {line_num}: {line} - {e}")
        
        self.logger.info(f"Parsed {len(labels)} labels from {file_path}")
        return labels
```

### Step 2: Coordinate System Transformation

#### Coordinate Analysis and Scaling
```python
class CoordinateTransformer:
    def __init__(self):
        self.scale_factor = 1.0
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.offset_z = 0.0
        
    def analyze_coordinates(self, map_data: MapData) -> dict:
        """Analyze coordinate ranges and determine scaling"""
        all_coords = []
        
        # Collect all coordinates
        for segment in map_data.line_segments:
            all_coords.extend([segment.x1, segment.y1, segment.z1, 
                              segment.x2, segment.y2, segment.z2])
        
        for label in map_data.labels:
            all_coords.extend([label.x, label.y, label.z])
        
        for waypoint in map_data.waypoints:
            all_coords.extend([waypoint.x, waypoint.y, waypoint.z])
        
        if not all_coords:
            return {'min': [0, 0, 0], 'max': [0, 0, 0], 'range': [0, 0, 0]}
        
        # Calculate bounds
        min_coords = [min(all_coords[::3]), min(all_coords[1::3]), min(all_coords[2::3])]
        max_coords = [max(all_coords[::3]), max(all_coords[1::3]), max(all_coords[2::3])]
        range_coords = [max_coords[i] - min_coords[i] for i in range(3)]
        
        # Determine appropriate scale factor for 3D viewing
        max_range = max(range_coords)
        if max_range > 0:
            # Scale to fit in a reasonable 3D space (e.g., 1000 units)
            self.scale_factor = 1000.0 / max_range
        else:
            self.scale_factor = 1.0
        
        # Calculate center offset
        self.offset_x = -(min_coords[0] + max_coords[0]) / 2
        self.offset_y = -(min_coords[1] + max_coords[1]) / 2
        self.offset_z = -(min_coords[2] + max_coords[2]) / 2
        
        return {
            'min': min_coords,
            'max': max_coords,
            'range': range_coords,
            'scale_factor': self.scale_factor,
            'offset': [self.offset_x, self.offset_y, self.offset_z]
        }
    
    def transform_coordinates(self, map_data: MapData) -> MapData:
        """Transform all coordinates to 3D space"""
        for segment in map_data.line_segments:
            segment.x1 = (segment.x1 + self.offset_x) * self.scale_factor
            segment.y1 = (segment.y1 + self.offset_y) * self.scale_factor
            segment.z1 = (segment.z1 + self.offset_z) * self.scale_factor
            segment.x2 = (segment.x2 + self.offset_x) * self.scale_factor
            segment.y2 = (segment.y2 + self.offset_y) * self.scale_factor
            segment.z2 = (segment.z2 + self.offset_z) * self.scale_factor
        
        for label in map_data.labels:
            label.x = (label.x + self.offset_x) * self.scale_factor
            label.y = (label.y + self.offset_y) * self.scale_factor
            label.z = (label.z + self.offset_z) * self.scale_factor
        
        for waypoint in map_data.waypoints:
            waypoint.x = (waypoint.x + self.offset_x) * self.scale_factor
            waypoint.y = (waypoint.y + self.offset_y) * self.scale_factor
            waypoint.z = (waypoint.z + self.offset_z) * self.scale_factor
        
        return map_data
```

### Step 3: 3D Geometry Generation

#### Line Segment to 3D Mesh Conversion
```python
class GeometryGenerator:
    def __init__(self, line_thickness: float = 2.0):
        self.line_thickness = line_thickness
        
    def generate_line_mesh(self, segment: LineSegment) -> dict:
        """Convert line segment to 3D mesh"""
        # Create a thin box along the line segment
        start = np.array([segment.x1, segment.y1, segment.z1])
        end = np.array([segment.x2, segment.y2, segment.z2])
        
        # Calculate line direction and length
        direction = end - start
        length = np.linalg.norm(direction)
        
        if length == 0:
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
        
        return {
            'vertices': np.array(vertices),
            'faces': np.array(faces),
            'color': [segment.r / 255.0, segment.g / 255.0, segment.b / 255.0]
        }
    
    def generate_label_mesh(self, label: Label) -> dict:
        """Generate 3D text mesh for label"""
        # For simplicity, create a billboard quad
        # In production, use a proper 3D text library
        
        # Create a simple quad facing the camera
        size = label.size * 10  # Scale based on label size
        
        vertices = np.array([
            [-size/2, -size/2, 0],
            [size/2, -size/2, 0],
            [size/2, size/2, 0],
            [-size/2, size/2, 0]
        ])
        
        faces = np.array([[0, 1, 2], [0, 2, 3]])
        
        return {
            'vertices': vertices,
            'faces': faces,
            'position': [label.x, label.y, label.z],
            'color': [label.r / 255.0, label.g / 255.0, label.b / 255.0],
            'text': label.text,
            'size': label.size
        }
    
    def generate_waypoint_mesh(self, waypoint: Waypoint) -> dict:
        """Generate special mesh for waypoint"""
        # Create a distinctive marker (e.g., cylinder or sphere)
        radius = 20.0
        height = 40.0
        
        # Generate cylinder vertices
        vertices = []
        segments = 16
        
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            # Bottom circle
            vertices.append([x, y, -height/2])
            # Top circle
            vertices.append([x, y, height/2])
        
        # Generate faces
        faces = []
        
        # Side faces
        for i in range(segments):
            next_i = (i + 1) % segments
            faces.extend([
                [i*2, next_i*2, next_i*2+1],
                [i*2, next_i*2+1, i*2+1]
            ])
        
        # Top and bottom faces
        for i in range(1, segments-1):
            faces.extend([
                [0, i*2, (i+1)*2],  # Bottom
                [1, (i+1)*2+1, i*2+1]  # Top
            ])
        
        return {
            'vertices': np.array(vertices),
            'faces': np.array(faces),
            'position': [waypoint.x, waypoint.y, waypoint.z],
            'color': [1.0, 0.0, 0.0] if waypoint.special_visual else [0.5, 0.5, 0.5],
            'waypoint_type': waypoint.waypoint_type
        }
```

### Step 4: glTF Generation

#### glTF Export with pygltflib
```python
class GLTFExporter:
    def __init__(self):
        self.scene_index = 0
        self.node_index = 0
        self.mesh_index = 0
        self.material_index = 0
        self.buffer_index = 0
        
    def export_map_data(self, map_data: MapData, output_path: str) -> dict:
        """Export map data to glTF format"""
        from pygltflib import GLTF2, Scene, Node, Mesh, Material, Buffer, BufferView, Accessor
        
        gltf = GLTF2()
        
        # Initialize arrays
        gltf.scenes = []
        gltf.nodes = []
        gltf.meshes = []
        gltf.materials = []
        gltf.buffers = []
        gltf.bufferViews = []
        gltf.accessors = []
        
        # Create scene
        scene = Scene()
        scene.nodes = []
        gltf.scenes.append(scene)
        
        # Create root node
        root_node = Node()
        root_node.name = f"{map_data.zone_name}_root"
        gltf.nodes.append(root_node)
        scene.nodes.append(self.node_index)
        self.node_index += 1
        
        # Process line segments
        for i, segment in enumerate(map_data.line_segments):
            mesh_data = self._generate_line_mesh(segment)
            if mesh_data:
                self._add_mesh_to_gltf(gltf, mesh_data, f"line_{i}")
        
        # Process labels
        for i, label in enumerate(map_data.labels):
            mesh_data = self._generate_label_mesh(label)
            if mesh_data:
                self._add_mesh_to_gltf(gltf, mesh_data, f"label_{i}")
        
        # Process waypoints
        for i, waypoint in enumerate(map_data.waypoints):
            mesh_data = self._generate_waypoint_mesh(waypoint)
            if mesh_data:
                self._add_mesh_to_gltf(gltf, mesh_data, f"waypoint_{i}")
        
        # Set default scene
        gltf.scene = 0
        
        # Save to file
        gltf.save(output_path)
        
        return {
            'file_path': output_path,
            'vertex_count': sum(len(mesh['vertices']) for mesh in gltf.meshes),
            'triangle_count': sum(len(mesh['faces']) for mesh in gltf.meshes),
            'material_count': len(gltf.materials)
        }
    
    def _add_mesh_to_gltf(self, gltf: GLTF2, mesh_data: dict, name: str):
        """Add mesh data to glTF structure"""
        # Create buffer view for vertices
        vertices_bytes = mesh_data['vertices'].tobytes()
        buffer_view = BufferView()
        buffer_view.buffer = self.buffer_index
        buffer_view.byteOffset = len(gltf.buffers[0].data) if gltf.buffers else 0
        buffer_view.byteLength = len(vertices_bytes)
        buffer_view.target = 34962  # ARRAY_BUFFER
        gltf.bufferViews.append(buffer_view)
        
        # Create accessor for vertices
        accessor = Accessor()
        accessor.bufferView = len(gltf.bufferViews) - 1
        accessor.componentType = 5126  # FLOAT
        accessor.count = len(mesh_data['vertices'])
        accessor.type = "VEC3"
        accessor.min = mesh_data['vertices'].min(axis=0).tolist()
        accessor.max = mesh_data['vertices'].max(axis=0).tolist()
        gltf.accessors.append(accessor)
        
        # Create buffer view for indices
        indices_bytes = mesh_data['faces'].tobytes()
        buffer_view = BufferView()
        buffer_view.buffer = self.buffer_index
        buffer_view.byteOffset = len(gltf.buffers[0].data) if gltf.buffers else 0
        buffer_view.byteLength = len(indices_bytes)
        buffer_view.target = 34963  # ELEMENT_ARRAY_BUFFER
        gltf.bufferViews.append(buffer_view)
        
        # Create accessor for indices
        accessor = Accessor()
        accessor.bufferView = len(gltf.bufferViews) - 1
        accessor.componentType = 5123  # UNSIGNED_SHORT
        accessor.count = len(mesh_data['faces']) * 3
        accessor.type = "SCALAR"
        gltf.accessors.append(accessor)
        
        # Create material
        material = Material()
        material.name = f"material_{self.material_index}"
        material.pbrMetallicRoughness = {
            "baseColorFactor": mesh_data['color'] + [1.0],
            "metallicFactor": 0.0,
            "roughnessFactor": 0.8
        }
        gltf.materials.append(material)
        
        # Create mesh
        mesh = Mesh()
        mesh.name = name
        mesh.primitives = [{
            "attributes": {
                "POSITION": len(gltf.accessors) - 2  # Vertex accessor
            },
            "indices": len(gltf.accessors) - 1,  # Index accessor
            "material": self.material_index
        }]
        gltf.meshes.append(mesh)
        
        # Create node
        node = Node()
        node.name = f"node_{name}"
        node.mesh = self.mesh_index
        if 'position' in mesh_data:
            node.translation = mesh_data['position']
        gltf.nodes.append(node)
        
        # Update indices
        self.mesh_index += 1
        self.material_index += 1
```

### Step 5: Babylon.js Integration

#### Web Viewer Implementation
```html
<!-- maps/viewer/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>EQDB 3D Zone Viewer</title>
    <script src="https://cdn.babylonjs.com/babylon.js"></script>
    <script src="https://cdn.babylonjs.com/loaders/babylonjs.loaders.min.js"></script>
    <style>
        #renderCanvas {
            width: 100%;
            height: 100vh;
            touch-action: none;
        }
        .controls {
            position: absolute;
            top: 10px;
            left: 10px;
            z-index: 100;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 10px;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <canvas id="renderCanvas"></canvas>
    <div class="controls">
        <h3>Zone: <span id="zoneName">Loading...</span></h3>
        <button onclick="resetCamera()">Reset Camera</button>
        <button onclick="toggleLabels()">Toggle Labels</button>
        <button onclick="toggleWaypoints()">Toggle Waypoints</button>
        <div id="info"></div>
    </div>
    
    <script>
        let canvas, engine, scene, camera;
        let zoneName = new URLSearchParams(window.location.search).get('zone') || 'overthere';
        
        // Initialize Babylon.js
        canvas = document.getElementById('renderCanvas');
        engine = new BABYLON.Engine(canvas, true);
        
        // Create scene
        scene = new BABYLON.Scene(engine);
        
        // Create camera
        camera = new BABYLON.ArcRotateCamera("camera", 0, Math.PI / 3, 1000, 
            BABYLON.Vector3.Zero(), scene);
        camera.attachControl(canvas, true);
        camera.lowerRadiusLimit = 100;
        camera.upperRadiusLimit = 5000;
        
        // Create lighting
        const light = new BABYLON.HemisphericLight("light", 
            new BABYLON.Vector3(0, 1, 0), scene);
        light.intensity = 0.7;
        
        const directionalLight = new BABYLON.DirectionalLight("dirLight", 
            new BABYLON.Vector3(0, -1, 0), scene);
        directionalLight.intensity = 0.5;
        
        // Load glTF model
        BABYLON.SceneLoader.ImportMesh("", `/maps/output/gltf/${zoneName}.gltf`, "", scene, 
            function (meshes) {
                console.log("Model loaded successfully");
                document.getElementById('zoneName').textContent = zoneName;
                
                // Set up interactions
                setupInteractions();
                
                // Auto-adjust camera
                autoAdjustCamera();
            },
            function (progress) {
                console.log("Loading progress:", progress);
            },
            function (error) {
                console.error("Error loading model:", error);
                document.getElementById('info').innerHTML = "Error loading zone data";
            }
        );
        
        function setupInteractions() {
            // Add click events for labels and waypoints
            scene.onPointerDown = function (evt) {
                const pickResult = scene.pick(scene.pointerX, scene.pointerY);
                if (pickResult.hit) {
                    const mesh = pickResult.pickedMesh;
                    if (mesh.name.startsWith('label_')) {
                        showLabelInfo(mesh);
                    } else if (mesh.name.startsWith('waypoint_')) {
                        showWaypointInfo(mesh);
                    }
                }
            };
        }
        
        function showLabelInfo(mesh) {
            const info = document.getElementById('info');
            info.innerHTML = `<strong>Label:</strong> ${mesh.name}<br>`;
        }
        
        function showWaypointInfo(mesh) {
            const info = document.getElementById('info');
            info.innerHTML = `<strong>Waypoint:</strong> ${mesh.name}<br>`;
        }
        
        function resetCamera() {
            camera.setPosition(new BABYLON.Vector3(0, 1000, 1000));
            camera.setTarget(BABYLON.Vector3.Zero());
        }
        
        function toggleLabels() {
            scene.meshes.forEach(mesh => {
                if (mesh.name.startsWith('label_')) {
                    mesh.setEnabled(!mesh.isEnabled());
                }
            });
        }
        
        function toggleWaypoints() {
            scene.meshes.forEach(mesh => {
                if (mesh.name.startsWith('waypoint_')) {
                    mesh.setEnabled(!mesh.isEnabled());
                }
            });
        }
        
        function autoAdjustCamera() {
            // Calculate bounding box of all meshes
            let minX = Infinity, minY = Infinity, minZ = Infinity;
            let maxX = -Infinity, maxY = -Infinity, maxZ = -Infinity;
            
            scene.meshes.forEach(mesh => {
                if (mesh.getBoundingInfo) {
                    const boundingInfo = mesh.getBoundingInfo();
                    const boundingBox = boundingInfo.boundingBox;
                    
                    minX = Math.min(minX, boundingBox.minimumWorld.x);
                    minY = Math.min(minY, boundingBox.minimumWorld.y);
                    minZ = Math.min(minZ, boundingBox.minimumWorld.z);
                    maxX = Math.max(maxX, boundingBox.maximumWorld.x);
                    maxY = Math.max(maxY, boundingBox.maximumWorld.y);
                    maxZ = Math.max(maxZ, boundingBox.maximumWorld.z);
                }
            });
            
            // Set camera position based on bounding box
            const center = new BABYLON.Vector3(
                (minX + maxX) / 2,
                (minY + maxY) / 2,
                (minZ + maxZ) / 2
            );
            
            const size = Math.max(maxX - minX, maxY - minY, maxZ - minZ);
            const distance = size * 2;
            
            camera.setPosition(center.add(new BABYLON.Vector3(distance, distance, distance)));
            camera.setTarget(center);
        }
        
        // Render loop
        engine.runRenderLoop(function () {
            scene.render();
        });
        
        // Handle window resize
        window.addEventListener('resize', function () {
            engine.resize();
        });
    </script>
</body>
</html>
```

## Performance Considerations

### File Size Optimization
```python
class GLTFOptimizer:
    def optimize_geometry(self, gltf_path: str, output_path: str):
        """Optimize glTF file for web delivery"""
        from pygltflib import GLTF2
        
        gltf = GLTF2.load(gltf_path)
        
        # Optimize meshes
        for mesh in gltf.meshes:
            for primitive in mesh.primitives:
                # Optimize vertex data
                self._optimize_vertices(gltf, primitive)
                
                # Optimize indices
                self._optimize_indices(gltf, primitive)
        
        # Compress buffer data
        self._compress_buffers(gltf)
        
        # Save optimized file
        gltf.save(output_path)
    
    def _optimize_vertices(self, gltf: GLTF2, primitive: dict):
        """Optimize vertex data by removing duplicates"""
        # Implementation for vertex deduplication
        pass
    
    def _optimize_indices(self, gltf: GLTF2, primitive: dict):
        """Optimize index data for better cache performance"""
        # Implementation for index optimization
        pass
    
    def _compress_buffers(self, gltf: GLTF2):
        """Compress buffer data using gzip"""
        # Implementation for buffer compression
        pass
```

### Caching Strategy
```python
class GeometryCache:
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        self.metadata_cache = {}
        
    def get_cached_geometry(self, zone_name: str) -> str:
        """Get cached geometry file path"""
        cache_path = f"{self.cache_dir}/{zone_name}.gltf"
        if os.path.exists(cache_path):
            return cache_path
        return None
    
    def cache_geometry(self, zone_name: str, gltf_path: str):
        """Cache geometry file"""
        cache_path = f"{self.cache_dir}/{zone_name}.gltf"
        shutil.copy2(gltf_path, cache_path)
    
    def get_metadata(self, zone_name: str) -> dict:
        """Get cached metadata"""
        if zone_name in self.metadata_cache:
            return self.metadata_cache[zone_name]
        
        # Load from database
        metadata = self._load_metadata_from_db(zone_name)
        self.metadata_cache[zone_name] = metadata
        return metadata
```

## Integration with Existing EQDB System

### API Endpoints
```python
# Add to api/routes.py
@v1.route('/maps/<zone_name>')
class ZoneMap(Resource):
    @v1.doc('Get 3D map data for a zone')
    @v1.response(200, 'Success')
    @v1.response(404, 'Zone not found')
    def get(self, zone_name):
        """Get 3D map data for a zone"""
        try:
            # Check if zone exists in database
            zone_data = zone_db.get_zone_raw_data(name=zone_name)
            if not zone_data:
                return {'message': 'Zone not found'}, 404
            
            # Get map metadata
            map_metadata = geometry_db.get_zone_metadata(zone_name)
            if not map_metadata:
                return {'message': '3D map data not available'}, 404
            
            # Return metadata and file URL
            return {
                'zone_name': zone_name,
                'zone_long_name': zone_data[0]['long_name'],
                'expansion_id': zone_data[0]['expansion'],
                'gltf_url': geometry_db.get_zone_geometry_url(zone_name),
                'viewer_url': f"/maps/viewer/?zone={zone_name}",
                'metadata': map_metadata
            }
        except Exception as e:
            logger.error(f"Error getting map data for {zone_name}: {e}")
            return {'message': 'Internal server error'}, 500

@v1.route('/maps/list')
class ZoneMapList(Resource):
    @v1.doc('Get list of available 3D maps')
    def get(self):
        """Get list of available 3D maps"""
        try:
            # Get all converted zones
            zones = geometry_db.get_all_converted_zones()
            return {'zones': zones}
        except Exception as e:
            logger.error(f"Error getting map list: {e}")
            return {'message': 'Internal server error'}, 500
```

### Frontend Integration
```typescript
// Add to fe/src/services/zoneService.ts
export const zoneService = {
  // ... existing methods ...
  
  get3DMapData: async (zoneName: string): Promise<any> => {
    const response = await api.get(`/maps/${zoneName}`)
    return response.data
  },
  
  get3DMapList: async (): Promise<{ zones: any[] }> => {
    const response = await api.get('/maps/list')
    return response.data
  },
  
  open3DViewer: (zoneName: string): void => {
    window.open(`/maps/viewer/?zone=${zoneName}`, '_blank')
  }
}
```

## Summary

### Recommended Database Strategy
1. **Hybrid Approach**: Store glTF files in filesystem, metadata in SQLite database
2. **File Organization**: Organize by expansion (classic, kunark, velious, luclin, pop)
3. **Caching**: Implement Redis/Memcached for frequently accessed metadata
4. **CDN**: Serve glTF files from CDN for optimal performance

### Conversion Process Summary
1. **Parse Brewall Files**: Extract line segments, labels, and waypoints
2. **Transform Coordinates**: Scale and center for 3D viewing
3. **Generate 3D Geometry**: Convert lines to meshes, create text labels
4. **Export glTF**: Use pygltflib to create standard 3D format
5. **Optimize**: Compress and optimize for web delivery
6. **Integrate**: Add to EQDB API and frontend

### Performance Optimizations
- **Geometry Batching**: Combine similar meshes
- **Level of Detail**: Multiple detail levels for different zoom levels
- **Frustum Culling**: Only render visible geometry
- **Texture Atlasing**: Combine textures for better performance
- **Progressive Loading**: Load geometry progressively based on camera position

This comprehensive approach ensures efficient storage, fast delivery, and optimal performance for the 3D map conversion system while maintaining integration with the existing EQDB infrastructure. 