"""
Robot Model
Defines the Robot class with properties for position, status, and battery.
"""

from enum import Enum
from typing import Dict, Optional, List, Tuple
import random


class RobotStatus(Enum):
    """Enum for robot operational status."""
    IDLE = "idle"
    MOVING = "moving"
    CHARGING = "charging"
    DELIVERING = "delivering"
    RETURNING = "returning"
    EN_ROUTE = "en_route"
    WORKING = "working"
    ERROR = "error"
    DEAD = "dead"  # Battery depleted, cannot move
    PICKING_UP = "picking_up"  # At pickup location, loading item
    DROPPING_OFF = "dropping_off"  # At delivery location, unloading item
    RETURNING_TO_START = "returning_to_start"  # Returning to starting station


class Robot:
    """
    Represents a warehouse robot with position, status, and battery level.
    
    Attributes:
        id (int): Unique identifier for the robot
        x (int): X-coordinate on the grid (0-19)
        y (int): Y-coordinate on the grid (0-19)
        status (RobotStatus): Current operational status
        battery (int): Battery level (0-100%)
        current_task: Current task assigned to this robot
        path: Current path the robot is following
        total_tasks_completed (int): Number of tasks completed
        total_distance_traveled (int): Total distance traveled
        error_count (int): Number of errors encountered
    """
    
    def __init__(self, robot_id: int, x: int = 0, y: int = 0, 
                 status: RobotStatus = RobotStatus.IDLE, battery: int = 100):
        """
        Initialize a robot with given parameters.
        
        Args:
            robot_id: Unique identifier for the robot
            x: Initial x-coordinate (default: 0)
            y: Initial y-coordinate (default: 0)
            status: Initial status (default: IDLE)
            battery: Initial battery level (default: 100)
        """
        self.id = robot_id
        self.x = x
        self.y = y
        self.status = status
        self.battery = battery
        self.current_task = None
        self.path: List[Tuple[int, int]] = []
        self.total_tasks_completed = 0
        self.total_distance_traveled = 0
        self.error_count = 0
        self.last_error: Optional[str] = None
        self.interrupted_task = None  # Store task that was interrupted due to low battery
        self.previous_position: Tuple[int, int] = (x, y)  # Track previous position
        self.current_job = None  # Current delivery job
        self.interrupted_job = None  # Store job that was interrupted due to low battery
        self.pickup_complete = False  # Flag for pickup completion
        self.dropoff_complete = False  # Flag for dropoff completion
        self.action_start_time: Optional[float] = None  # Time when pickup/dropoff started
    
    def update_position(self, grid_size: int = 20):
        """
        Update robot position randomly within grid bounds.
        
        Args:
            grid_size: Size of the grid (default: 20 for 20x20 grid)
        """
        # Randomly move in one of 4 directions or stay in place
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        
        # Ensure robot stays within grid bounds
        self.x = max(0, min(grid_size - 1, self.x + dx))
        self.y = max(0, min(grid_size - 1, self.y + dy))
    
    def update_status(self):
        """Randomly update robot status to simulate activity."""
        # 70% chance to keep current status, 30% to change
        if random.random() < 0.3:
            self.status = random.choice(list(RobotStatus))
    
    def update_battery(self):
        """
        Update battery level based on status.
        - Charging: increase battery
        - Moving/Delivering: decrease battery
        - Idle/Returning: slight decrease
        """
        if self.status == RobotStatus.CHARGING:
            # Increase battery while charging (up to 100%)
            self.battery = min(100, self.battery + random.randint(5, 15))
            # If fully charged and no task, go idle
            if self.battery >= 100 and not self.current_task:
                self.status = RobotStatus.IDLE
        elif self.status in [RobotStatus.MOVING, RobotStatus.DELIVERING, RobotStatus.EN_ROUTE, RobotStatus.WORKING]:
            # Decrease battery while active
            self.battery = max(0, self.battery - random.randint(1, 3))
        else:
            # Slight decrease for idle/returning
            self.battery = max(0, self.battery - random.randint(0, 1))
        
        # If battery is critically low, force charging or error status
        if self.battery <= 0:
            self.status = RobotStatus.ERROR
            self.last_error = "Battery depleted"
            self.error_count += 1
        elif self.battery < 20 and self.status != RobotStatus.CHARGING:
            self.status = RobotStatus.CHARGING
    
    def drain_battery(self, amount: int = 1):
        """
        Drain battery by specified amount (used when moving).
        
        Args:
            amount: Amount of battery to drain (default: 1 per move)
        """
        self.battery = max(0, self.battery - amount)
        
        # Check if battery is dead
        if self.battery <= 0:
            self.status = RobotStatus.DEAD
            self.last_error = "Battery depleted - robot is dead"
            self.error_count += 1
            # Cancel current task if any
            if self.current_task:
                self.interrupted_task = self.current_task
                self.current_task.cancel()
                self.current_task = None
            self.path = []
    
    def charge_battery(self, amount: int = 5) -> bool:
        """
        Charge battery by specified amount.
        
        Args:
            amount: Amount of battery to charge (default: 5 per tick)
        
        Returns:
            True if battery is fully charged, False otherwise
        """
        self.battery = min(100, self.battery + amount)
        
        # If fully charged, restore from dead status
        if self.battery >= 100:
            if self.status == RobotStatus.DEAD:
                self.status = RobotStatus.IDLE
                self.last_error = None
            return True
        return False
    
    def is_dead(self) -> bool:
        """Check if robot is dead (battery depleted)."""
        return self.battery <= 0 or self.status == RobotStatus.DEAD
    
    def needs_charging(self, threshold: int = 15) -> bool:
        """
        Check if robot needs to charge urgently.
        
        Args:
            threshold: Battery percentage threshold (default: 15%)
        
        Returns:
            True if battery is below threshold and not already charging/dead
        """
        return (self.battery < threshold and 
                self.status not in [RobotStatus.CHARGING, RobotStatus.DEAD])
    
    def interrupt_job_for_charging(self):
        """
        Interrupt current job to go charge.
        Stores the job for later resumption.
        """
        if self.current_job and self.status != RobotStatus.DEAD:
            self.interrupted_job = self.current_job
            self.current_job = None
            self.pickup_complete = False
            self.dropoff_complete = False
            self.path = []
            self.status = RobotStatus.EN_ROUTE  # En route to charging station
            self.last_error = f"Low battery - job paused for charging"
    
    def resume_interrupted_job(self):
        """
        Resume job that was interrupted due to low battery.
        Only if battery is sufficient now.
        """
        if self.interrupted_job and self.battery > 30:
            self.current_job = self.interrupted_job
            self.interrupted_job = None
            # Reset job state - will restart from pickup
            self.pickup_complete = False
            self.dropoff_complete = False
            self.status = RobotStatus.EN_ROUTE
            self.last_error = None
            print(f"✓ Robot {self.id} resumed interrupted job {self.interrupted_job.job_id if self.interrupted_job else 'unknown'}")
            return True
        return False
    
    def assign_job(self, job):
        """
        Assign a delivery job to this robot.
        
        Args:
            job: Job object to assign
        """
        self.current_job = job
        self.pickup_complete = False
        self.dropoff_complete = False
        self.status = RobotStatus.EN_ROUTE
    
    def start_pickup(self):
        """Start pickup action at pickup location"""
        self.status = RobotStatus.PICKING_UP
        self.action_start_time = None  # Will be set by fleet manager
        self.pickup_complete = False
    
    def complete_pickup(self):
        """Complete pickup action"""
        self.pickup_complete = True
        self.status = RobotStatus.EN_ROUTE
        self.action_start_time = None
    
    def start_dropoff(self):
        """Start dropoff action at delivery location"""
        self.status = RobotStatus.DROPPING_OFF
        self.action_start_time = None  # Will be set by fleet manager
        self.dropoff_complete = False
    
    def complete_dropoff(self):
        """Complete dropoff action"""
        self.dropoff_complete = True
        self.status = RobotStatus.RETURNING_TO_START
        self.action_start_time = None
    
    def complete_job(self):
        """Complete the current job"""
        self.current_job = None
        self.pickup_complete = False
        self.dropoff_complete = False
        self.status = RobotStatus.IDLE
        self.action_start_time = None
    
    def has_job(self) -> bool:
        """Check if robot has an active job"""
        return self.current_job is not None
    
    def reset(self, x: int = None, y: int = None):
        """
        Reset robot to initial state.
        
        Args:
            x: X-coordinate to reset to (random if None)
            y: Y-coordinate to reset to (random if None)
        """
        if x is None:
            x = random.randint(0, 19)
        if y is None:
            y = random.randint(0, 19)
        
        self.x = x
        self.y = y
        self.status = RobotStatus.IDLE
        self.battery = 100
        self.current_task = None
        self.path = []
        self.last_error = None
        self.interrupted_task = None
        self.previous_position = (self.x, self.y)
        self.current_job = None
        self.pickup_complete = False
        self.dropoff_complete = False
        self.action_start_time = None
    
    def assign_task(self, task):
        """
        Assign a task to this robot.
        
        Args:
            task: Task object to assign
        """
        self.current_task = task
        task.start()
        self.status = RobotStatus.EN_ROUTE
    
    def move_to(self, target_x: int, target_y: int):
        """
        Move robot one step closer to target using simple pathfinding.
        
        Args:
            target_x: Target x-coordinate
            target_y: Target y-coordinate
        
        Returns:
            True if reached target, False otherwise
        """
        # If already at target
        if self.x == target_x and self.y == target_y:
            return True
        
        # Simple greedy movement (move closer on one axis at a time)
        dx = target_x - self.x
        dy = target_y - self.y
        
        # Move horizontally first if needed
        if dx != 0:
            self.x += 1 if dx > 0 else -1
            self.total_distance_traveled += 1
        # Otherwise move vertically
        elif dy != 0:
            self.y += 1 if dy > 0 else -1
            self.total_distance_traveled += 1
        
        # Check if reached target
        return self.x == target_x and self.y == target_y
    
    def move_along_path(self) -> bool:
        """
        Move robot along its assigned path.
        Drains battery per move.
        
        Returns:
            True if reached end of path, False otherwise
        """
        if not self.path:
            return True
        
        # Store previous position
        self.previous_position = (self.x, self.y)
        
        # Get next position from path
        next_pos = self.path[0]
        self.x, self.y = next_pos
        self.total_distance_traveled += 1
        self.path.pop(0)
        
        # Drain battery for movement
        self.drain_battery(1)
        
        # If current task exists, increment its steps
        if self.current_task:
            self.current_task.increment_steps()
        
        return len(self.path) == 0
    
    def complete_task(self):
        """Complete the current task and update status."""
        if self.current_task:
            self.current_task.complete()
            self.total_tasks_completed += 1
            self.current_task = None
            self.path = []
        self.status = RobotStatus.IDLE
    
    def has_task(self) -> bool:
        """Check if robot has an active task."""
        return self.current_task is not None
    
    def is_low_battery(self, threshold: int = 30) -> bool:
        """
        Check if robot has low battery.
        
        Args:
            threshold: Battery percentage threshold
        
        Returns:
            True if battery is below threshold
        """
        return self.battery < threshold
    
    def to_dict(self) -> Dict:
        """
        Convert robot to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the robot
        """
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "status": self.status.value,
            "battery": self.battery,
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "current_job": self.current_job.to_dict() if self.current_job else None,
            "interrupted_task": self.interrupted_task.to_dict() if self.interrupted_task else None,
            "path": self.path,
            "tasks_completed": self.total_tasks_completed,
            "distance_traveled": self.total_distance_traveled,
            "error_count": self.error_count,
            "last_error": self.last_error,
            "is_dead": self.is_dead(),
            "needs_charging": self.needs_charging(),
            "pickup_complete": self.pickup_complete,
            "dropoff_complete": self.dropoff_complete
        }
    
    def __repr__(self) -> str:
        """String representation of the robot."""
        return (f"Robot(id={self.id}, pos=({self.x},{self.y}), "
                f"status={self.status.value}, battery={self.battery}%)")
