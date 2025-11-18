"""
Pathfinding Utilities
Implements A* pathfinding algorithm for robot navigation.
"""

import heapq
from typing import List, Tuple, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from models.environment import WarehouseGrid


class PathFinder:
    """
    A* pathfinding implementation for grid-based navigation.
    Integrates with WarehouseGrid for environment-aware pathfinding.
    """
    
    def __init__(self, grid_size: int = 20, warehouse_grid: 'WarehouseGrid' = None):
        """
        Initialize the pathfinder.
        
        Args:
            grid_size: Size of the grid (default: 20 for 20x20)
            warehouse_grid: Optional WarehouseGrid instance for environment awareness
        """
        self.grid_size = grid_size
        self.obstacles: Set[Tuple[int, int]] = set()
        self.warehouse_grid = warehouse_grid
        
        # If warehouse grid is provided, sync obstacles
        if self.warehouse_grid:
            self.obstacles = set(self.warehouse_grid.obstacles)
    
    def set_warehouse_grid(self, warehouse_grid: 'WarehouseGrid'):
        """
        Set the warehouse grid and sync obstacles.
        
        Args:
            warehouse_grid: WarehouseGrid instance
        """
        self.warehouse_grid = warehouse_grid
        self.obstacles = set(self.warehouse_grid.obstacles)
    
    def add_obstacle(self, x: int, y: int):
        """Add an obstacle at the given position."""
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            self.obstacles.add((x, y))
    
    def remove_obstacle(self, x: int, y: int):
        """Remove an obstacle at the given position."""
        self.obstacles.discard((x, y))
    
    def clear_obstacles(self):
        """Clear all obstacles."""
        self.obstacles.clear()
    
    def is_valid_position(self, x: int, y: int, occupied_positions: Set[Tuple[int, int]] = None) -> bool:
        """
        Check if a position is valid (within bounds, walkable, and not occupied).
        Uses WarehouseGrid if available for environment-aware validation.
        
        Args:
            x: X-coordinate
            y: Y-coordinate
            occupied_positions: Set of positions occupied by other robots
        
        Returns:
            True if position is valid, False otherwise
        """
        # Check bounds
        if not (0 <= x < self.grid_size and 0 <= y < self.grid_size):
            return False
        
        # If warehouse grid is available, use it for walkability check
        if self.warehouse_grid:
            if not self.warehouse_grid.is_walkable(x, y):
                return False
        else:
            # Fallback to manual obstacle checking
            if (x, y) in self.obstacles:
                return False
        
        # Check if position is occupied by another robot
        if occupied_positions and (x, y) in occupied_positions:
            return False
        
        return True
    
    def heuristic(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """
        Calculate Manhattan distance heuristic.
        
        Args:
            pos1: Starting position (x, y)
            pos2: Goal position (x, y)
        
        Returns:
            Manhattan distance between positions
        """
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_neighbors(self, pos: Tuple[int, int], occupied_positions: Set[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """
        Get valid neighboring positions (4-directional movement).
        
        Args:
            pos: Current position (x, y)
            occupied_positions: Set of positions occupied by other robots
        
        Returns:
            List of valid neighbor positions
        """
        x, y = pos
        neighbors = []
        
        # Check 4 directions: up, down, left, right
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y, occupied_positions):
                neighbors.append((new_x, new_y))
        
        return neighbors
    
    def find_path(
        self, 
        start: Tuple[int, int], 
        goal: Tuple[int, int],
        occupied_positions: Set[Tuple[int, int]] = None
    ) -> Optional[List[Tuple[int, int]]]:
        """
        Find the shortest path from start to goal using A* algorithm.
        
        Args:
            start: Starting position (x, y)
            goal: Goal position (x, y)
            occupied_positions: Set of positions occupied by other robots
        
        Returns:
            List of positions representing the path, or None if no path exists
        """
        # If start equals goal, return empty path
        if start == goal:
            return []
        
        # If goal is not valid, return None
        if not self.is_valid_position(goal[0], goal[1]):
            return None
        
        # Priority queue: (f_score, counter, position)
        counter = 0
        open_set = [(0, counter, start)]
        came_from = {}
        
        # Cost from start to position
        g_score = {start: 0}
        
        # Estimated total cost from start to goal through position
        f_score = {start: self.heuristic(start, goal)}
        
        # Set of evaluated positions
        closed_set = set()
        
        while open_set:
            _, _, current = heapq.heappop(open_set)
            
            # Check if we reached the goal
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            closed_set.add(current)
            
            # Check all neighbors
            for neighbor in self.get_neighbors(current, occupied_positions):
                if neighbor in closed_set:
                    continue
                
                # Calculate tentative g_score
                tentative_g_score = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    # This path to neighbor is better
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, goal)
                    
                    counter += 1
                    heapq.heappush(open_set, (f_score[neighbor], counter, neighbor))
        
        # No path found
        return None
    
    def get_next_step(
        self,
        current: Tuple[int, int],
        goal: Tuple[int, int],
        occupied_positions: Set[Tuple[int, int]] = None
    ) -> Optional[Tuple[int, int]]:
        """
        Get the next step towards the goal.
        
        Args:
            current: Current position (x, y)
            goal: Goal position (x, y)
            occupied_positions: Set of positions occupied by other robots
        
        Returns:
            Next position to move to, or None if no path exists
        """
        path = self.find_path(current, goal, occupied_positions)
        if path and len(path) > 0:
            return path[0]
        return None
