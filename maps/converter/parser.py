import os
import logging
import sys
from typing import List, Optional
from dataclasses import dataclass, field
from materials import BREWALL_LAYER_COLOR_MAP

# Add the parent directory to the path to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import utils

# Data classes for map elements
@dataclass
class LineSegment:
    x1: float
    y1: float
    z1: float
    x2: float
    y2: float
    z2: float
    r: int
    g: int
    b: int
    layer: str = None  # Brewall semantic type/layer

@dataclass
class Label:
    x: float
    y: float
    z: float
    r: int
    g: int
    b: int
    size: int
    text: str

@dataclass
class Waypoint:
    x: float
    y: float
    z: float
    zone_name: str
    special_visual: bool = True
    description: Optional[str] = None

@dataclass
class MapData:
    zone_name: str
    line_segments: List[LineSegment] = field(default_factory=list)
    labels: List[Label] = field(default_factory=list)
    waypoints: List[Waypoint] = field(default_factory=list)
    secondary_segments: List[LineSegment] = field(default_factory=list)

class MapParser:
    def __init__(self, maps_dir: str = "../../maps/brewall", verbose: bool = True):
        self.maps_dir = os.path.abspath(maps_dir)
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
        if self.verbose:
            logging.basicConfig(level=logging.INFO)

    def parse_zone(self, zone_name: str) -> MapData:
        """Parse all Brewall files for a given zone, including waypoints."""
        map_data = MapData(zone_name=zone_name)
        self.logger.info(f"Parsing zone: {zone_name}")
        # Parse main geometry
        map_data.line_segments = self.parse_line_segments(zone_name)
        # Parse labels
        map_data.labels = self.parse_labels(zone_name)
        # Parse secondary geometry
        map_data.secondary_segments = self.parse_secondary_segments(zone_name)
        # Parse waypoints
        map_data.waypoints = self.parse_waypoints(zone_name)
        return map_data

    def parse_line_segments(self, zone_name: str) -> List[LineSegment]:
        """Parse L records from main map file."""
        segments = []
        file_path = os.path.join(self.maps_dir, f"{zone_name}.txt")
        if not os.path.exists(file_path):
            self.logger.warning(f"Main map file not found: {file_path}")
            return segments
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('L'):
                    parts = line.split()
                    try:
                        r = int(parts[7].strip(','))
                        g = int(parts[8].strip(','))
                        b = int(parts[9].strip(','))
                        color_tuple = (r, g, b)
                        layer = BREWALL_LAYER_COLOR_MAP.get(color_tuple, None)
                        segment = LineSegment(
                            x1=float(parts[1].strip(',')),
                            y1=float(parts[2].strip(',')),
                            z1=float(parts[3].strip(',')),
                            x2=float(parts[4].strip(',')),
                            y2=float(parts[5].strip(',')),
                            z2=float(parts[6].strip(',')),
                            r=r,
                            g=g,
                            b=b,
                            layer=layer
                        )
                        segments.append(segment)
                    except Exception as e:
                        self.logger.error(f"Error parsing line segment: {line.strip()} - {e}")
        self.logger.info(f"Parsed {len(segments)} line segments from {file_path}")
        return segments

    def parse_labels(self, zone_name: str) -> List[Label]:
        """Parse P records from label file."""
        labels = []
        file_path = os.path.join(self.maps_dir, f"{zone_name}_1.txt")
        if not os.path.exists(file_path):
            self.logger.warning(f"Label file not found: {file_path}")
            return labels
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('P'):
                    parts = line.split()
                    try:
                        size = int(parts[7].strip(','))
                        text = ' '.join(parts[8:]).replace('_', ' ')
                        label = Label(
                            x=float(parts[1].strip(',')),
                            y=float(parts[2].strip(',')),
                            z=float(parts[3].strip(',')),
                            r=int(parts[4].strip(',')),
                            g=int(parts[5].strip(',')),
                            b=int(parts[6].strip(',')),
                            size=size,
                            text=text
                        )
                        labels.append(label)
                    except Exception as e:
                        self.logger.error(f"Error parsing label: {line.strip()} - {e}")
        self.logger.info(f"Parsed {len(labels)} labels from {file_path}")
        return labels

    def parse_secondary_segments(self, zone_name: str) -> List[LineSegment]:
        """Parse L records from secondary geometry file (_2.txt)."""
        segments = []
        file_path = os.path.join(self.maps_dir, f"{zone_name}_2.txt")
        if not os.path.exists(file_path):
            self.logger.info(f"No secondary geometry file for: {zone_name}")
            return segments
        with open(file_path, 'r') as f:
            for line in f:
                if line.startswith('L'):
                    parts = line.split()
                    try:
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
                    except Exception as e:
                        self.logger.error(f"Error parsing secondary segment: {line.strip()} - {e}")
        self.logger.info(f"Parsed {len(segments)} secondary segments from {file_path}")
        return segments

    def parse_waypoints(self, zone_name: str) -> List[Waypoint]:
        """Parse waypoint data using existing utils.get_zone_waypoint() function."""
        waypoints = []
        waypoint_data = utils.get_zone_waypoint(zone_name)
        
        if waypoint_data and len(waypoint_data) > 0:
            # Create waypoint with special visual treatment
            waypoint = Waypoint(
                x=waypoint_data.get('x', 0.0),
                y=waypoint_data.get('y', 0.0),
                z=waypoint_data.get('z', 0.0),
                zone_name=zone_name,
                special_visual=True,
                description="Waypoint"
            )
            waypoints.append(waypoint)
            self.logger.info(f"Added waypoint for {zone_name}: ({waypoint.x}, {waypoint.y}, {waypoint.z})")
        else:
            self.logger.info(f"No waypoint data found for zone: {zone_name}")
        
        return waypoints 