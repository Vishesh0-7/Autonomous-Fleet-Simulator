"""
Warehouse Environment Model
Defines the warehouse grid with different cell types (empty, obstacle, charging station, delivery zone)
"""

from enum import Enum
from typing import List, Tuple, Optional, Dict
import random


class CellType(str, Enum):
    """Types of cells in the warehouse grid"""
    EMPTY = "empty"
    OBSTACLE = "obstacle"
    CHARGING_STATION = "charging_station"
    DELIVERY_ZONE = "delivery_zone"
    PICKUP_ZONE = "pickup_zone"
    STARTING_STATION = "starting_station"


class WarehouseGrid:
    """
    Represents the warehouse environment as a 2D grid.
    Manages cell types, charging stations, delivery zones, and obstacles.
    """
    
    def __init__(self, width: int = 20, height: int = 20):
        self.width = width
        self.height = height
        self.grid: List[List[CellType]] = []
        self.charging_stations: List[Tuple[int, int]] = []
        self.delivery_zones: List[Tuple[int, int]] = []
        self.pickup_zones: List[Tuple[int, int]] = []
        self.starting_stations: List[Tuple[int, int]] = []
        self.obstacles: List[Tuple[int, int]] = []
        
        # Initialize grid with empty cells
        self._initialize_grid()
        
        # Add default environment features
        self._add_default_features()
    
    def _initialize_grid(self):
        """Initialize the grid with all empty cells"""
        self.grid = [
            [CellType.EMPTY for _ in range(self.width)]
            for _ in range(self.height)
        ]
    
    def _add_default_features(self):
        """Add default charging stations, delivery zones, pickup zones, starting station, and obstacles"""
        # Add starting station (center of grid)
        center_x, center_y = self.width // 2, self.height // 2
        self.set_cell_type(center_x, center_y, CellType.STARTING_STATION)
        self.starting_stations.append((center_x, center_y))
        
        # Add charging stations (4 corners)
        charging_positions = [
            (1, 1),                       # Top-left
            (1, self.height - 2),         # Bottom-left
            (self.width - 2, 1),          # Top-right
            (self.width - 2, self.height - 2)  # Bottom-right
        ]
        
        for x, y in charging_positions:
            self.set_cell_type(x, y, CellType.CHARGING_STATION)
            self.charging_stations.append((x, y))
        
        # Add pickup zones (left and top sides)
        pickup_positions = [
            (3, center_y - 2),
            (3, center_y + 2),
            (center_x - 2, 3),
            (center_x + 2, 3),
        ]
        
        for x, y in pickup_positions:
            if self.is_valid_position(x, y) and self.get_cell_type(x, y) == CellType.EMPTY:
                self.set_cell_type(x, y, CellType.PICKUP_ZONE)
                self.pickup_zones.append((x, y))
        
        # Add delivery zones (right and bottom sides)
        delivery_positions = [
            (self.width - 4, center_y - 2),
            (self.width - 4, center_y + 2),
            (center_x - 2, self.height - 4),
            (center_x + 2, self.height - 4),
        ]
        
        for x, y in delivery_positions:
            if self.is_valid_position(x, y) and self.get_cell_type(x, y) == CellType.EMPTY:
                self.set_cell_type(x, y, CellType.DELIVERY_ZONE)
                self.delivery_zones.append((x, y))
        
        # Add some random obstacles (about 5-8% of grid)
        num_obstacles = int(self.width * self.height * 0.05)
        added = 0
        attempts = 0
        max_attempts = num_obstacles * 10
        
        while added < num_obstacles and attempts < max_attempts:
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            attempts += 1
            
            # Don't place obstacles on special cells or near starting station
            if (self.get_cell_type(x, y) == CellType.EMPTY and 
                abs(x - center_x) > 2 and abs(y - center_y) > 2):
                self.set_cell_type(x, y, CellType.OBSTACLE)
                self.obstacles.append((x, y))
                added += 1
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within grid bounds"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_cell_type(self, x: int, y: int) -> Optional[CellType]:
        """Get the type of cell at given position"""
        if not self.is_valid_position(x, y):
            return None
        return self.grid[y][x]
    
    def set_cell_type(self, x: int, y: int, cell_type: CellType) -> bool:
        """Set the type of cell at given position"""
        if not self.is_valid_position(x, y):
            return False
        
        old_type = self.grid[y][x]
        self.grid[y][x] = cell_type
        
        # Update tracking lists
        pos = (x, y)
        
        # Remove from old tracking list
        if old_type == CellType.CHARGING_STATION and pos in self.charging_stations:
            self.charging_stations.remove(pos)
        elif old_type == CellType.DELIVERY_ZONE and pos in self.delivery_zones:
            self.delivery_zones.remove(pos)
        elif old_type == CellType.PICKUP_ZONE and pos in self.pickup_zones:
            self.pickup_zones.remove(pos)
        elif old_type == CellType.STARTING_STATION and pos in self.starting_stations:
            self.starting_stations.remove(pos)
        elif old_type == CellType.OBSTACLE and pos in self.obstacles:
            self.obstacles.remove(pos)
        
        # Add to new tracking list
        if cell_type == CellType.CHARGING_STATION and pos not in self.charging_stations:
            self.charging_stations.append(pos)
        elif cell_type == CellType.DELIVERY_ZONE and pos not in self.delivery_zones:
            self.delivery_zones.append(pos)
        elif cell_type == CellType.PICKUP_ZONE and pos not in self.pickup_zones:
            self.pickup_zones.append(pos)
        elif cell_type == CellType.STARTING_STATION and pos not in self.starting_stations:
            self.starting_stations.append(pos)
        elif cell_type == CellType.OBSTACLE and pos not in self.obstacles:
            self.obstacles.append(pos)
        
        return True
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a robot can move to this cell"""
        if not self.is_valid_position(x, y):
            return False
        
        cell_type = self.get_cell_type(x, y)
        # Robots can walk on empty cells, charging stations, delivery zones, pickup zones, and starting stations
        return cell_type in [CellType.EMPTY, CellType.CHARGING_STATION, 
                            CellType.DELIVERY_ZONE, CellType.PICKUP_ZONE, 
                            CellType.STARTING_STATION]
    
    def is_charging_station(self, x: int, y: int) -> bool:
        """Check if position is a charging station"""
        return self.get_cell_type(x, y) == CellType.CHARGING_STATION
    
    def is_delivery_zone(self, x: int, y: int) -> bool:
        """Check if position is a delivery zone"""
        return self.get_cell_type(x, y) == CellType.DELIVERY_ZONE
    
    def is_pickup_zone(self, x: int, y: int) -> bool:
        """Check if position is a pickup zone"""
        return self.get_cell_type(x, y) == CellType.PICKUP_ZONE
    
    def is_starting_station(self, x: int, y: int) -> bool:
        """Check if position is a starting station"""
        return self.get_cell_type(x, y) == CellType.STARTING_STATION
    
    def find_nearest_pickup_zone(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Find the nearest pickup zone using Manhattan distance"""
        if not self.pickup_zones:
            return None
        
        def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        current_pos = (x, y)
        nearest = min(self.pickup_zones, key=lambda zone: manhattan_distance(current_pos, zone))
        return nearest
    
    def get_starting_station(self) -> Optional[Tuple[int, int]]:
        """Get the primary starting station (first one in list)"""
        return self.starting_stations[0] if self.starting_stations else None
    
    def find_nearest_charging_station(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """
        Find the nearest charging station using Manhattan distance.
        Returns (x, y) of nearest station or None if no stations exist.
        """
        if not self.charging_stations:
            return None
        
        def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        current_pos = (x, y)
        nearest = min(self.charging_stations, key=lambda station: manhattan_distance(current_pos, station))
        return nearest
    
    def find_nearest_delivery_zone(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Find the nearest delivery zone using Manhattan distance"""
        if not self.delivery_zones:
            return None
        
        def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        
        current_pos = (x, y)
        nearest = min(self.delivery_zones, key=lambda zone: manhattan_distance(current_pos, zone))
        return nearest
    
    def get_random_empty_position(self) -> Tuple[int, int]:
        """Get a random empty position on the grid"""
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if self.get_cell_type(x, y) == CellType.EMPTY:
                return (x, y)
            
            attempts += 1
        
        # Fallback: return any valid position
        return (0, 0)
    
    def add_obstacle(self, x: int, y: int) -> bool:
        """Add an obstacle at the given position"""
        if self.get_cell_type(x, y) == CellType.EMPTY:
            return self.set_cell_type(x, y, CellType.OBSTACLE)
        return False
    
    def remove_obstacle(self, x: int, y: int) -> bool:
        """Remove an obstacle at the given position"""
        if self.get_cell_type(x, y) == CellType.OBSTACLE:
            return self.set_cell_type(x, y, CellType.EMPTY)
        return False
    
    def add_charging_station(self, x: int, y: int) -> bool:
        """Add a charging station at the given position"""
        if self.get_cell_type(x, y) == CellType.EMPTY:
            return self.set_cell_type(x, y, CellType.CHARGING_STATION)
        return False
    
    def add_delivery_zone(self, x: int, y: int) -> bool:
        """Add a delivery zone at the given position"""
        if self.get_cell_type(x, y) == CellType.EMPTY:
            return self.set_cell_type(x, y, CellType.DELIVERY_ZONE)
        return False
    
    def add_pickup_zone(self, x: int, y: int) -> bool:
        """Add a pickup zone at the given position"""
        if self.get_cell_type(x, y) == CellType.EMPTY:
            return self.set_cell_type(x, y, CellType.PICKUP_ZONE)
        return False
    
    def add_starting_station(self, x: int, y: int) -> bool:
        """Add a starting station at the given position"""
        if self.get_cell_type(x, y) == CellType.EMPTY:
            return self.set_cell_type(x, y, CellType.STARTING_STATION)
        return False
    
    def to_dict(self) -> Dict:
        """Convert grid to dictionary for JSON serialization"""
        return {
            "width": self.width,
            "height": self.height,
            "grid": [[cell.value for cell in row] for row in self.grid],
            "charging_stations": self.charging_stations,
            "delivery_zones": self.delivery_zones,
            "pickup_zones": self.pickup_zones,
            "starting_stations": self.starting_stations,
            "obstacles": self.obstacles
        }
    
    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get walkable neighboring cells (up, down, left, right only - no diagonals)"""
        neighbors = []
        directions = [
            (0, -1),  # Up
            (0, 1),   # Down
            (-1, 0),  # Left
            (1, 0)    # Right
        ]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
