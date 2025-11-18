"""
Task Model
Defines tasks that can be assigned to robots.
"""

from enum import Enum
from typing import Optional, Tuple
from datetime import datetime


class TaskType(Enum):
    """Enum for different task types."""
    PICKUP = "pickup"
    DROPOFF = "dropoff"
    CHARGE = "charge"
    MOVE = "move"
    PATROL = "patrol"


class TaskStatus(Enum):
    """Enum for task status."""
    PENDING = "pending"
    EN_ROUTE = "en_route"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """
    Represents a task assigned to a robot.
    
    Attributes:
        task_id (str): Unique task identifier
        robot_id (int): ID of the robot assigned to this task
        task_type (TaskType): Type of task
        target_x (int): Target x-coordinate
        target_y (int): Target y-coordinate
        status (TaskStatus): Current task status
        priority (int): Task priority (1-10, higher is more urgent)
        created_at (datetime): When the task was created
        started_at (datetime): When the robot started the task
        completed_at (datetime): When the task was completed
        estimated_steps (int): Estimated steps to complete
        actual_steps (int): Actual steps taken
    """
    
    _task_counter = 0
    
    def __init__(
        self,
        robot_id: int,
        task_type: TaskType,
        target_x: int,
        target_y: int,
        priority: int = 5
    ):
        """
        Initialize a new task.
        
        Args:
            robot_id: ID of the robot to assign this task to
            task_type: Type of task
            target_x: Target x-coordinate (0-19)
            target_y: Target y-coordinate (0-19)
            priority: Task priority (1-10, default 5)
        """
        Task._task_counter += 1
        self.task_id = f"T{Task._task_counter:04d}"
        self.robot_id = robot_id
        self.task_type = task_type
        self.target_x = target_x
        self.target_y = target_y
        self.status = TaskStatus.PENDING
        self.priority = max(1, min(10, priority))
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.estimated_steps = 0
        self.actual_steps = 0
        self.error_message: Optional[str] = None
    
    def start(self):
        """Mark the task as started."""
        if self.status == TaskStatus.PENDING:
            self.status = TaskStatus.EN_ROUTE
            self.started_at = datetime.now()
    
    def complete(self):
        """Mark the task as completed."""
        if self.status in [TaskStatus.EN_ROUTE, TaskStatus.IN_PROGRESS]:
            self.status = TaskStatus.COMPLETED
            self.completed_at = datetime.now()
    
    def fail(self, error_message: str):
        """Mark the task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
    
    def cancel(self):
        """Cancel the task."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def get_target(self) -> Tuple[int, int]:
        """Get the target coordinates as a tuple."""
        return (self.target_x, self.target_y)
    
    def increment_steps(self):
        """Increment the actual steps counter."""
        self.actual_steps += 1
    
    def get_duration(self) -> Optional[float]:
        """Get task duration in seconds."""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for JSON serialization."""
        return {
            "task_id": self.task_id,
            "robot_id": self.robot_id,
            "task_type": self.task_type.value,
            "target": {"x": self.target_x, "y": self.target_y},
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_steps": self.estimated_steps,
            "actual_steps": self.actual_steps,
            "duration": self.get_duration(),
            "error_message": self.error_message
        }
    
    def __repr__(self) -> str:
        """String representation of the task."""
        return (f"Task(id={self.task_id}, robot={self.robot_id}, "
                f"type={self.task_type.value}, target=({self.target_x},{self.target_y}), "
                f"status={self.status.value})")
