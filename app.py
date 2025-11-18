"""
Warehouse Fleet Simulator - Main Application
FastAPI backend for simulating and managing warehouse robots.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from typing import Dict, List, Optional

from fleet.fleet_manager import FleetManager
from models.robot import RobotStatus
from models.schemas import (
    RobotResponse,
    FleetSummaryResponse,
    ResetResponse,
    APIInfoResponse,
    ErrorResponse,
    TaskAssignmentRequest,
    TaskAssignmentResponse,
    TaskResponse,
    EnhancedFleetSummaryResponse
)


# Global fleet manager instance
fleet_manager: FleetManager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Starts the simulation on startup and stops it on shutdown.
    """
    # Startup: Initialize and start the fleet simulation
    global fleet_manager
    fleet_manager = FleetManager(num_robots=5, grid_size=20, update_interval=2)
    fleet_manager.start_simulation()
    print("\n" + "="*60)
    print("🚀 Warehouse Fleet Simulator is running!")
    print("="*60)
    print(f"📍 API available at: http://localhost:8000")
    print(f"📚 API docs at: http://localhost:8000/docs")
    print(f"🤖 Simulating {fleet_manager.num_robots} robots")
    print(f"🔄 Update interval: {fleet_manager.update_interval} seconds")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown: Stop the simulation
    if fleet_manager:
        fleet_manager.stop_simulation()
    print("\n👋 Warehouse Fleet Simulator stopped")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Warehouse Fleet Simulator",
    description="Backend API for simulating and managing warehouse robots on a grid",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware (useful for frontend integration later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== API ENDPOINTS ====================

@app.get("/", response_model=APIInfoResponse)
async def root() -> Dict:
    """
    Root endpoint - API information and health check.
    
    Returns:
        Dictionary with API information
    """
    return {
        "message": "Warehouse Fleet Management System API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "GET /robots": "Get current state of all robots",
            "GET /robots/{robot_id}": "Get state of a specific robot",
            "GET /fleet/summary": "Get enhanced fleet statistics with tasks",
            "POST /assign_task": "Assign a task to a robot",
            "GET /tasks": "Get all tasks (active, completed, failed)",
            "POST /tasks/{task_id}/cancel": "Cancel an active task",
            "POST /reset": "Reset all robots to initial state",
            "GET /docs": "Interactive API documentation"
        }
    }


@app.get("/robots", response_model=List[RobotResponse])
async def get_robots() -> List[Dict]:
    """
    Get current state of all robots.
    
    Returns:
        List of robot data with id, x, y, status, and battery
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    return fleet_manager.get_fleet_status()


@app.get("/robots/{robot_id}", response_model=RobotResponse, responses={404: {"model": ErrorResponse}})
async def get_robot(robot_id: int) -> Dict:
    """
    Get current state of a specific robot.
    
    Args:
        robot_id: ID of the robot to retrieve
    
    Returns:
        Robot data with id, x, y, status, and battery
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    # Find robot by ID
    for robot in fleet_manager.robots:
        if robot.id == robot_id:
            return robot.to_dict()
    
    raise HTTPException(status_code=404, detail=f"Robot with ID {robot_id} not found")


@app.get("/fleet/summary", response_model=EnhancedFleetSummaryResponse)
async def get_fleet_summary() -> Dict:
    """
    Get enhanced summary statistics of the fleet.
    Includes active tasks, idle robots, errors, completed tasks, and more.
    
    Returns:
        Dictionary with comprehensive fleet statistics
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    return fleet_manager.get_fleet_summary()


@app.get("/environment")
async def get_environment() -> Dict:
    """
    Get the warehouse environment layout.
    Returns the grid with cell types (empty, obstacle, charging_station, delivery_zone).
    
    Returns:
        Dictionary with grid layout, dimensions, and special locations
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    return fleet_manager.warehouse_grid.to_dict()


@app.post("/reset", response_model=ResetResponse)
async def reset_fleet() -> Dict:
    """
    Reset all robots to initial state.
    Repositions all robots randomly and recharges batteries to 100%.
    
    Returns:
        Confirmation message with updated robot data
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    fleet_manager.reset_fleet()
    
    return {
        "message": "Fleet reset successfully",
        "robots": fleet_manager.get_fleet_status()
    }


# ==================== TASK MANAGEMENT ENDPOINTS ====================

@app.post("/assign_task", response_model=TaskAssignmentResponse)
async def assign_task(request: TaskAssignmentRequest) -> Dict:
    """
    Assign a task to a specific robot.
    
    The robot will navigate to the target coordinates and complete the task.
    
    Args:
        request: Task assignment request with robot_id, task_type, target coordinates, and priority
    
    Returns:
        Task assignment result with task and robot details
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    result = fleet_manager.assign_task(
        robot_id=request.robot_id,
        task_type=request.task_type,
        target_x=request.target_x,
        target_y=request.target_y,
        priority=request.priority
    )
    
    if result is None:
        raise HTTPException(status_code=404, detail=f"Robot with ID {request.robot_id} not found")
    
    if not result.get("success", False):
        raise HTTPException(status_code=400, detail=result.get("error", "Task assignment failed"))
    
    return result


@app.get("/tasks")
async def get_tasks() -> Dict:
    """
    Get all tasks (active, completed, and failed).
    
    Returns:
        Dictionary with lists of tasks by status
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    return fleet_manager.get_all_tasks()


@app.post("/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> Dict:
    """
    Cancel an active task.
    
    Args:
        task_id: ID of the task to cancel
    
    Returns:
        Confirmation message
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    success = fleet_manager.cancel_task(task_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Active task with ID {task_id} not found")
    
    return {
        "message": f"Task {task_id} cancelled successfully",
        "task_id": task_id
    }


# ==================== JOB MANAGEMENT ENDPOINTS ====================

@app.post("/jobs/add")
async def add_job(
    pickup_x: int,
    pickup_y: int,
    delivery_x: Optional[int] = None,
    delivery_y: Optional[int] = None,
    priority: int = 5
) -> Dict:
    """
    Add a new delivery job to the queue.
    If delivery coordinates are not provided, automatically finds the nearest delivery zone.
    
    Args:
        pickup_x: Pickup X coordinate
        pickup_y: Pickup Y coordinate
        delivery_x: Delivery X coordinate (optional - auto-finds nearest if not provided)
        delivery_y: Delivery Y coordinate (optional - auto-finds nearest if not provided)
        priority: Job priority (1-10, default: 5)
    
    Returns:
        Job details
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")

    # Validate pickup coordinates
    if not (0 <= pickup_x < fleet_manager.grid_size and 0 <= pickup_y < fleet_manager.grid_size):
        raise HTTPException(status_code=400, detail="Invalid pickup coordinates")
    
    # Validate delivery coordinates if provided
    if delivery_x is not None and delivery_y is not None:
        if not (0 <= delivery_x < fleet_manager.grid_size and 0 <= delivery_y < fleet_manager.grid_size):
            raise HTTPException(status_code=400, detail="Invalid delivery coordinates")
        delivery = (delivery_x, delivery_y)
    else:
        delivery = None
    
    try:
        job = fleet_manager.job_manager.add_job((pickup_x, pickup_y), delivery, priority)
        return {
            "message": "Job added successfully (auto-delivery)" if delivery is None else "Job added successfully",
            "job": job.to_dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/jobs")
async def get_jobs() -> Dict:
    """
    Get all jobs (pending, active, completed, failed).
    
    Returns:
        Dictionary with job lists organized by status
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    return fleet_manager.job_manager.get_all_jobs()


@app.delete("/jobs/{job_id}")
async def cancel_job(job_id: str) -> Dict:
    """
    Cancel a pending or active job.
    
    Args:
        job_id: ID of the job to cancel
    
    Returns:
        Confirmation message
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    success = fleet_manager.job_manager.cancel_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Job with ID {job_id} not found")
    
    # If job was active, clear it from the robot
    for robot in fleet_manager.robots:
        if robot.current_job and robot.current_job.job_id == job_id:
            robot.current_job = None
            robot.status = RobotStatus.IDLE
            robot.path = []
            break
    
    return {
        "message": f"Job {job_id} cancelled successfully",
        "job_id": job_id
    }


@app.get("/jobs/statistics")
async def get_job_statistics() -> Dict:
    """
    Get job statistics (total, pending, active, completed, failed, success rate, etc.).
    
    Returns:
        Job statistics
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    return fleet_manager.job_manager.get_statistics()


# ==================== ENVIRONMENT CONFIGURATION ENDPOINTS ====================

@app.post("/environment/update")
async def update_environment(
    action: str,  # "add" or "remove"
    cell_type: str,  # "obstacle", "pickup_zone", "delivery_zone", "charging_station"
    x: int,
    y: int
) -> Dict:
    """
    Dynamically update the environment by adding or removing cells.
    
    Args:
        action: "add" or "remove"
        cell_type: Type of cell to add/remove
        x: X coordinate
        y: Y coordinate
    
    Returns:
        Confirmation message with updated environment
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    # Validate coordinates
    if not (0 <= x < fleet_manager.grid_size and 0 <= y < fleet_manager.grid_size):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    warehouse_grid = fleet_manager.warehouse_grid
    
    if action == "add":
        if cell_type == "obstacle":
            success = warehouse_grid.add_obstacle(x, y)
        elif cell_type == "pickup_zone":
            success = warehouse_grid.add_pickup_zone(x, y)
        elif cell_type == "delivery_zone":
            success = warehouse_grid.add_delivery_zone(x, y)
        elif cell_type == "charging_station":
            success = warehouse_grid.add_charging_station(x, y)
        elif cell_type == "starting_station":
            success = warehouse_grid.add_starting_station(x, y)
        else:
            raise HTTPException(status_code=400, detail="Invalid cell type")
        
        if success:
            # Update pathfinder obstacles
            fleet_manager.pathfinder.set_warehouse_grid(warehouse_grid)
            return {
                "message": f"Added {cell_type} at ({x}, {y})",
                "environment": warehouse_grid.to_dict()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Cannot add {cell_type} at ({x}, {y}) - cell not empty")
    
    elif action == "remove":
        if cell_type == "obstacle":
            success = warehouse_grid.remove_obstacle(x, y)
        else:
            # For other cell types, set back to empty
            from models.environment import CellType
            current_type = warehouse_grid.get_cell_type(x, y)
            if current_type and current_type.value == cell_type:
                success = warehouse_grid.set_cell_type(x, y, CellType.EMPTY)
            else:
                success = False
        
        if success:
            # Update pathfinder obstacles
            fleet_manager.pathfinder.set_warehouse_grid(warehouse_grid)
            return {
                "message": f"Removed {cell_type} at ({x}, {y})",
                "environment": warehouse_grid.to_dict()
            }
        else:
            raise HTTPException(status_code=400, detail=f"Cannot remove {cell_type} at ({x}, {y})")
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'add' or 'remove'")


@app.post("/environment/add")
async def add_environment_element(
    cell_type: str,  # "obstacle", "pickup_zone", "delivery_zone", "charging_station", "starting_station"
    x: int,
    y: int
) -> Dict:
    """
    Add a new element to the environment.
    
    Args:
        cell_type: Type of cell to add
        x: X coordinate  
        y: Y coordinate
    
    Returns:
        Confirmation message with updated environment
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    # Validate coordinates
    if not (0 <= x < fleet_manager.grid_size and 0 <= y < fleet_manager.grid_size):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    warehouse_grid = fleet_manager.warehouse_grid
    
    if cell_type == "obstacle":
        success = warehouse_grid.add_obstacle(x, y)
    elif cell_type == "pickup_zone":
        success = warehouse_grid.add_pickup_zone(x, y)
    elif cell_type == "delivery_zone":
        success = warehouse_grid.add_delivery_zone(x, y)
    elif cell_type == "charging_station":
        success = warehouse_grid.add_charging_station(x, y)
    elif cell_type == "starting_station":
        success = warehouse_grid.add_starting_station(x, y)
    else:
        raise HTTPException(status_code=400, detail="Invalid cell type")
    
    if success:
        # Update pathfinder obstacles
        fleet_manager.pathfinder.set_warehouse_grid(warehouse_grid)
        return {
            "message": f"Added {cell_type} at ({x}, {y})",
            "environment": warehouse_grid.to_dict()
        }
    else:
        raise HTTPException(status_code=400, detail=f"Cannot add {cell_type} at ({x}, {y}) - cell not empty")


@app.delete("/environment/remove")
async def remove_environment_element(
    cell_type: str,  # "obstacle", "pickup_zone", "delivery_zone", "charging_station", "starting_station"
    x: int,
    y: int
) -> Dict:
    """
    Remove an element from the environment.
    
    Args:
        cell_type: Type of cell to remove
        x: X coordinate
        y: Y coordinate
    
    Returns:
        Confirmation message with updated environment
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    # Validate coordinates
    if not (0 <= x < fleet_manager.grid_size and 0 <= y < fleet_manager.grid_size):
        raise HTTPException(status_code=400, detail="Invalid coordinates")
    
    warehouse_grid = fleet_manager.warehouse_grid
    
    # Check if the cell has the expected type and remove it
    from models.environment import CellType
    current_type = warehouse_grid.get_cell_type(x, y)
    
    if current_type and current_type.value == cell_type:
        success = warehouse_grid.set_cell_type(x, y, CellType.EMPTY)
    else:
        raise HTTPException(status_code=400, detail=f"No {cell_type} found at ({x}, {y})")
    
    if success:
        # Update pathfinder obstacles
        fleet_manager.pathfinder.set_warehouse_grid(warehouse_grid)
        return {
            "message": f"Removed {cell_type} at ({x}, {y})",
            "environment": warehouse_grid.to_dict()
        }
    else:
        raise HTTPException(status_code=400, detail=f"Cannot remove {cell_type} at ({x}, {y})")


# ==================== ROBOT CHARGING ENDPOINT ====================

@app.post("/robot/charge")
async def force_robot_charge(robot_id: int) -> Dict:
    """
    Force a robot to go to the nearest charging station.
    
    Args:
        robot_id: ID of the robot to send for charging
    
    Returns:
        Status of the charging command
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    robot = fleet_manager.get_robot_by_id(robot_id)
    if not robot:
        raise HTTPException(status_code=404, detail=f"Robot {robot_id} not found")
    
    if robot.is_dead():
        raise HTTPException(status_code=400, detail=f"Robot {robot_id} is dead and cannot move")
    
    # Find nearest charging station
    nearest_station = fleet_manager.warehouse_grid.find_nearest_charging_station(robot.x, robot.y)
    if not nearest_station:
        raise HTTPException(status_code=400, detail="No charging stations available")
    
    # If robot has a job, interrupt it for charging
    if robot.has_job():
        robot.interrupt_job_for_charging()
    
    # If robot has a task, interrupt it for charging  
    if robot.has_task():
        robot.interrupt_task_for_charging()
    
    # Send robot to charge
    fleet_manager._send_robot_to_charge(robot, nearest_station)
    
    return {
        "message": f"Robot {robot_id} sent to charging station at {nearest_station}",
        "robot": robot.to_dict(),
        "charging_station": {"x": nearest_station[0], "y": nearest_station[1]},
        "battery_level": robot.battery
    }


# ==================== CONTINUOUS OPERATION ENDPOINTS ====================

@app.post("/continuous/start")
async def start_continuous_mode(
    max_jobs: int = 3,
    interval: int = 5
) -> Dict:
    """
    Start continuous operation mode.
    
    Args:
        max_jobs: Maximum number of active jobs to maintain (default: 3)
        interval: Seconds between job generation (default: 5)
    
    Returns:
        Status confirmation
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    if max_jobs < 1 or max_jobs > 20:
        raise HTTPException(status_code=400, detail="max_jobs must be between 1 and 20")
    
    if interval < 1 or interval > 60:
        raise HTTPException(status_code=400, detail="interval must be between 1 and 60 seconds")
    
    fleet_manager.set_continuous_mode(True, max_jobs, interval)
    
    return {
        "message": "Continuous operation mode started",
        "max_jobs": max_jobs,
        "interval": interval,
        "pickup_zones": len(fleet_manager.warehouse_grid.pickup_zones),
        "delivery_zones": len(fleet_manager.warehouse_grid.delivery_zones)
    }


@app.post("/continuous/stop")
async def stop_continuous_mode() -> Dict:
    """
    Stop continuous operation mode.
    
    Returns:
        Status confirmation
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    fleet_manager.set_continuous_mode(False)
    
    return {
        "message": "Continuous operation mode stopped",
        "pending_jobs": len(fleet_manager.job_manager.pending_jobs),
        "active_jobs": len(fleet_manager.job_manager.active_jobs)
    }


@app.get("/continuous/status")
async def get_continuous_status() -> Dict:
    """
    Get current continuous operation status.
    
    Returns:
        Continuous mode configuration and stats
    """
    if fleet_manager is None:
        raise HTTPException(status_code=503, detail="Fleet manager not initialized")
    
    return {
        "enabled": fleet_manager.continuous_mode,
        "max_jobs": fleet_manager.max_active_jobs,
        "interval": fleet_manager.job_generation_interval,
        "last_generation": fleet_manager.last_job_generation,
        "pending_jobs": len(fleet_manager.job_manager.pending_jobs),
        "active_jobs": len(fleet_manager.job_manager.active_jobs),
        "pickup_zones": len(fleet_manager.warehouse_grid.pickup_zones),
        "delivery_zones": len(fleet_manager.warehouse_grid.delivery_zones)
    }


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    """
    Main entry point for the application.
    Running this file starts the FastAPI server with auto-reload enabled.
    """
    print("\n🚀 Starting Warehouse Fleet Simulator...")
    print("Press CTRL+C to stop the server\n")
    
    # Run the FastAPI application with Uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,
        reload=True,  # Auto-reload on code changes (development mode)
        log_level="info"
    )
