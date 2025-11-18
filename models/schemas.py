"""
API Response Models
Pydantic models for API request/response validation and documentation.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class RobotResponse(BaseModel):
    """Response model for a single robot."""
    id: int = Field(..., description="Unique robot identifier", example=1)
    x: int = Field(..., ge=0, le=19, description="X-coordinate on grid (0-19)", example=15)
    y: int = Field(..., ge=0, le=19, description="Y-coordinate on grid (0-19)", example=8)
    status: str = Field(..., description="Current robot status", example="moving")
    battery: int = Field(..., ge=0, le=100, description="Battery level (0-100%)", example=87)

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "x": 15,
                "y": 8,
                "status": "moving",
                "battery": 87
            }
        }


class FleetSummaryResponse(BaseModel):
    """Response model for fleet summary statistics."""
    total_robots: int = Field(..., description="Total number of robots in fleet", example=5)
    average_battery: float = Field(..., description="Average battery level across fleet", example=78.4)
    status_distribution: Dict[str, int] = Field(
        ..., 
        description="Count of robots by status",
        example={"moving": 2, "idle": 1, "charging": 2}
    )
    grid_size: str = Field(..., description="Grid dimensions", example="20x20")


class ResetResponse(BaseModel):
    """Response model for fleet reset operation."""
    message: str = Field(..., description="Operation status message", example="Fleet reset successfully")
    robots: List[RobotResponse] = Field(..., description="Updated robot states after reset")


class APIInfoResponse(BaseModel):
    """Response model for API root endpoint."""
    message: str = Field(..., description="API welcome message")
    version: str = Field(..., description="API version")
    status: str = Field(..., description="API status")
    endpoints: Dict[str, str] = Field(..., description="Available endpoints and their descriptions")


class ErrorResponse(BaseModel):
    """Response model for error messages."""
    detail: str = Field(..., description="Error message describing what went wrong")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Robot with ID 10 not found"
            }
        }


class TaskAssignmentRequest(BaseModel):
    """Request model for assigning a task to a robot."""
    robot_id: int = Field(..., description="ID of the robot to assign the task to", example=1)
    task_type: str = Field(..., description="Type of task (pickup, dropoff, charge, move)", example="pickup")
    target_x: int = Field(..., ge=0, le=19, description="Target x-coordinate", example=15)
    target_y: int = Field(..., ge=0, le=19, description="Target y-coordinate", example=10)
    priority: int = Field(5, ge=1, le=10, description="Task priority (1-10, default 5)", example=5)


class TaskResponse(BaseModel):
    """Response model for a task."""
    task_id: str = Field(..., description="Unique task identifier", example="T0001")
    robot_id: int = Field(..., description="Robot assigned to this task", example=1)
    task_type: str = Field(..., description="Type of task", example="pickup")
    target: Dict[str, int] = Field(..., description="Target coordinates", example={"x": 15, "y": 10})
    status: str = Field(..., description="Current task status", example="en_route")
    priority: int = Field(..., description="Task priority", example=5)
    created_at: str = Field(..., description="ISO timestamp when task was created")
    started_at: Optional[str] = Field(None, description="ISO timestamp when task started")
    completed_at: Optional[str] = Field(None, description="ISO timestamp when task completed")
    estimated_steps: int = Field(..., description="Estimated steps to complete", example=20)
    actual_steps: int = Field(..., description="Actual steps taken", example=18)
    duration: Optional[float] = Field(None, description="Task duration in seconds", example=36.5)
    error_message: Optional[str] = Field(None, description="Error message if task failed")


class TaskAssignmentResponse(BaseModel):
    """Response model for task assignment."""
    success: bool = Field(..., description="Whether task assignment was successful", example=True)
    task: Optional[Dict] = Field(None, description="Task details if successful")
    robot: Optional[Dict] = Field(None, description="Robot details if successful")
    error: Optional[str] = Field(None, description="Error message if failed")


class EnhancedFleetSummaryResponse(BaseModel):
    """Enhanced response model for fleet summary with task and analytics data."""
    total_robots: int = Field(..., description="Total number of robots", example=5)
    active_tasks: int = Field(..., description="Number of active tasks", example=3)
    idle_robots: int = Field(..., description="Number of idle robots", example=2)
    average_battery: float = Field(..., description="Average battery across fleet", example=78.4)
    status_distribution: Dict[str, int] = Field(..., description="Robot status counts")
    grid_size: str = Field(..., description="Grid dimensions", example="20x20")
    errors: List[Dict] = Field(..., description="Current errors")
    completed_tasks: int = Field(..., description="Total completed tasks", example=15)
    failed_tasks: int = Field(..., description="Total failed tasks", example=1)
    uptime_percent: float = Field(..., description="System uptime percentage", example=98.5)
    low_battery_alerts: List[Dict] = Field(..., description="Recent low battery alerts")
    total_distance_traveled: int = Field(..., description="Total distance traveled by all robots", example=2450)
