"""
Fleet Manager
Manages the fleet of robots including initialization, updates, simulation, task assignment,
job management, and environment integration with charging stations and delivery zones.
"""

import random
import threading
import time
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
from models.robot import Robot, RobotStatus
from models.task import Task, TaskType, TaskStatus
from models.environment import WarehouseGrid
from models.job_manager import JobManager, Job, JobStatus
from utils.pathfinding import PathFinder


class FleetManager:
    """
    Manages a fleet of warehouse robots on a grid with environment awareness.
    
    Attributes:
        grid_size (int): Size of the grid (default: 20 for 20x20)
        num_robots (int): Number of robots in the fleet
        robots (List[Robot]): List of robot instances
        update_interval (int): Seconds between simulation updates
        warehouse_grid (WarehouseGrid): The warehouse environment
        pathfinder (PathFinder): Pathfinding utility
        active_tasks (List[Task]): List of active tasks
        completed_tasks (List[Task]): List of completed tasks
        failed_tasks (List[Task]): List of failed tasks
        start_time (datetime): When the fleet manager was initialized
        total_uptime (timedelta): Total uptime of the system
        low_battery_alerts (List[Dict]): List of low battery alerts
    """
    
    def __init__(self, num_robots: int = 5, grid_size: int = 20, 
                 update_interval: int = 2):
        """
        Initialize the fleet manager.
        
        Args:
            num_robots: Number of robots to create (default: 5)
            grid_size: Size of the grid (default: 20)
            update_interval: Seconds between updates (default: 2)
        """
        self.grid_size = grid_size
        self.num_robots = num_robots
        self.update_interval = update_interval
        self.robots: List[Robot] = []
        self._simulation_thread = None
        self._stop_simulation = False
        
        # Initialize warehouse environment
        self.warehouse_grid = WarehouseGrid(grid_size, grid_size)
        
        # Task management with environment-aware pathfinding
        self.pathfinder = PathFinder(grid_size, self.warehouse_grid)
        self.active_tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.failed_tasks: List[Task] = []
        
        # Job management
        self.job_manager = JobManager(self.warehouse_grid)
        
        # Continuous operation mode
        self.continuous_mode = False
        self.max_active_jobs = 3  # Maximum number of jobs to keep in queue
        self.job_generation_interval = 5  # Seconds between job generation
        self.last_job_generation = time.time()
        
        # Analytics
        self.start_time = datetime.now()
        self.total_uptime = timedelta(0)
        self.low_battery_alerts: List[Dict] = []
        
        # Initialize robots
        self._initialize_robots()
    
    def _initialize_robots(self):
        """Create robots at the starting station."""
        self.robots = []
        starting_station = self.warehouse_grid.get_starting_station()
        
        if not starting_station:
            print("⚠️  No starting station found, using random positions")
            starting_station = (self.grid_size // 2, self.grid_size // 2)
        
        for i in range(self.num_robots):
            robot = Robot(
                robot_id=i + 1,
                x=starting_station[0],
                y=starting_station[1],
                status=RobotStatus.IDLE,
                battery=100  # Start with full battery
            )
            self.robots.append(robot)
        print(f"✓ Initialized {self.num_robots} robots at starting station {starting_station}")
    
    def _generate_continuous_jobs(self):
        """Generate new jobs automatically when in continuous mode"""
        if not self.continuous_mode:
            return
        
        # Check if it's time to generate a new job
        current_time = time.time()
        if current_time - self.last_job_generation < self.job_generation_interval:
            return
        
        # Check if we have too many pending jobs already
        pending_count = len(self.job_manager.pending_jobs)
        active_count = len(self.job_manager.active_jobs)
        total_jobs = pending_count + active_count
        
        if total_jobs >= self.max_active_jobs:
            return
        
        # Generate a new job from a random pickup zone
        pickup_zones = self.warehouse_grid.pickup_zones
        if not pickup_zones:
            return  # No pickup zones available
        
        # Pick a random pickup zone
        import random
        pickup_location = random.choice(pickup_zones)
        
        # Create a new job (delivery will be auto-assigned to nearest delivery zone)
        try:
            job = self.job_manager.add_job_pickup_only(pickup_location, priority=5)
            self.last_job_generation = current_time
            print(f"🔄 Auto-generated job {job.job_id} at pickup {pickup_location}")
        except ValueError as e:
            print(f"⚠️  Could not generate continuous job: {e}")
    
    def set_continuous_mode(self, enabled: bool, max_jobs: int = 3, interval: int = 5):
        """
        Enable or disable continuous operation mode.
        
        Args:
            enabled: Whether to enable continuous mode
            max_jobs: Maximum number of active jobs to maintain
            interval: Seconds between job generation
        """
        self.continuous_mode = enabled
        self.max_active_jobs = max_jobs
        self.job_generation_interval = interval
        
        if enabled:
            print(f"✓ Continuous mode enabled: max {max_jobs} jobs, {interval}s interval")
        else:
            print("✓ Continuous mode disabled")
    
    def update_fleet(self):
        """Update all robots' positions, status, battery levels, handle charging logic, and manage jobs."""
        # Generate continuous jobs if enabled
        self._generate_continuous_jobs()
        
        # Auto-assign jobs to idle robots
        self._auto_assign_jobs()
        
        # Get occupied positions (excluding the robot itself)
        occupied_positions = {(r.x, r.y) for r in self.robots}
        
        for robot in self.robots:
            # Skip dead robots
            if robot.is_dead():
                continue
            
            # Handle robots at charging stations
            if self.warehouse_grid.is_charging_station(robot.x, robot.y):
                if robot.status == RobotStatus.CHARGING or robot.needs_charging():
                    robot.status = RobotStatus.CHARGING
                    fully_charged = robot.charge_battery(5)  # +5 per tick
                    
                    if fully_charged:
                        # Resume interrupted task if any
                        robot.resume_interrupted_task()
                        # Resume interrupted job if any
                        robot.resume_interrupted_job()
                        if not robot.has_task() and not robot.has_job():
                            robot.status = RobotStatus.IDLE
                    continue
            
            # Check if robot needs charging urgently (battery < 15%)
            if robot.needs_charging(15) and not robot.has_job():
                nearest_station = self.warehouse_grid.find_nearest_charging_station(robot.x, robot.y)
                if nearest_station:
                    # Create emergency charging task
                    self._send_robot_to_charge(robot, nearest_station)
                    self._add_low_battery_alert(robot)
                    continue
            
            # Check if robot with job needs charging
            if robot.needs_charging(15) and robot.has_job():
                # Interrupt job for charging
                robot.interrupt_job_for_charging()
                nearest_station = self.warehouse_grid.find_nearest_charging_station(robot.x, robot.y)
                if nearest_station:
                    self._send_robot_to_charge(robot, nearest_station)
                    self._add_low_battery_alert(robot)
                continue
            
            # Handle job-based movement (priority over tasks)
            if robot.has_job():
                self._update_robot_with_job(robot, occupied_positions)
            # Handle task-based movement
            elif robot.has_task():
                self._update_robot_with_task(robot, occupied_positions)
            else:
                # Idle robots stay at starting station
                if robot.status == RobotStatus.IDLE:
                    starting_station = self.warehouse_grid.get_starting_station()
                    if starting_station and (robot.x, robot.y) != starting_station:
                        # Return to starting station
                        robot.status = RobotStatus.RETURNING_TO_START
                        occupied = occupied_positions - {(robot.x, robot.y)}
                        path = self.pathfinder.find_path((robot.x, robot.y), starting_station, occupied)
                        if path:
                            robot.path = path

    
    def _update_robot_with_task(self, robot: Robot, occupied_positions: Set[Tuple[int, int]]):
        """
        Update robot that has an assigned task.
        
        Args:
            robot: Robot to update
            occupied_positions: Set of occupied grid positions
        """
        task = robot.current_task
        
        # If robot has a path, follow it
        if robot.path:
            reached_end = robot.move_along_path()
            if reached_end:
                # Reached target, complete task
                robot.status = RobotStatus.WORKING
        else:
            # Generate new path to target
            current_pos = (robot.x, robot.y)
            target_pos = task.get_target()
            
            # Remove current robot from occupied positions for pathfinding
            occupied_positions.discard(current_pos)
            path = self.pathfinder.find_path(current_pos, target_pos, occupied_positions)
            occupied_positions.add(current_pos)
            
            if path:
                robot.path = path
                robot.status = RobotStatus.EN_ROUTE
            else:
                # No path found, mark as failed
                task.fail("No path to target")
                self.failed_tasks.append(task)
                self.active_tasks.remove(task)
                robot.current_task = None
                robot.status = RobotStatus.IDLE
                return
        
        # Check if robot reached target and is working
        if robot.status == RobotStatus.WORKING:
            # Simulate task completion (you can add more complex logic here)
            robot.complete_task()
            self.completed_tasks.append(task)
            self.active_tasks.remove(task)
            print(f"✓ Robot {robot.id} completed {task.task_type.value} task {task.task_id}")
    
    def _add_low_battery_alert(self, robot: Robot):
        """Add a low battery alert for a robot."""
        # Check if alert already exists for this robot (within last 5 minutes)
        recent_alert = any(
            alert['robot_id'] == robot.id and
            (datetime.now() - datetime.fromisoformat(alert['timestamp'])).seconds < 300
            for alert in self.low_battery_alerts[-10:]  # Check last 10 alerts
        )
        
        if not recent_alert:
            alert = {
                "robot_id": robot.id,
                "battery": robot.battery,
                "position": {"x": robot.x, "y": robot.y},
                "timestamp": datetime.now().isoformat()
            }
            self.low_battery_alerts.append(alert)
            print(f"⚠️  Low battery alert: Robot {robot.id} at {robot.battery}%")
    
    def _send_robot_to_charge(self, robot: Robot, charging_station: Tuple[int, int]):
        """
        Send a robot to a charging station.
        
        Args:
            robot: Robot to send for charging
            charging_station: (x, y) position of charging station
        """
        # Create path to charging station
        occupied = {(r.x, r.y) for r in self.robots if r.id != robot.id}
        path = self.pathfinder.find_path((robot.x, robot.y), charging_station, occupied)
        
        if path:
            robot.path = path
            robot.status = RobotStatus.EN_ROUTE  # En route to charging
            print(f"→ Robot {robot.id} en route to charging station at {charging_station}")
        else:
            print(f"✗ Robot {robot.id} cannot find path to charging station")
    
    def _auto_assign_jobs(self):
        """Automatically assign pending jobs to idle robots"""
        # Get idle robots (not dead, not charging, not with job/task)
        idle_robots = [r for r in self.robots if r.status == RobotStatus.IDLE and 
                      not r.has_job() and not r.has_task() and not r.is_dead()]
        
        # Assign jobs to idle robots
        for robot in idle_robots:
            next_job = self.job_manager.get_next_job()
            if next_job:
                self.job_manager.assign_job(next_job, robot.id)
                robot.assign_job(next_job)
                # Create path to pickup location
                occupied = {(r.x, r.y) for r in self.robots if r.id != robot.id}
                path = self.pathfinder.find_path((robot.x, robot.y), next_job.pickup, occupied)
                if path:
                    robot.path = path
                    robot.status = RobotStatus.EN_ROUTE
                    next_job.start_pickup()
                else:
                    # Cannot reach pickup, fail job
                    self.job_manager.fail_job(next_job, "Cannot reach pickup location")
                    robot.current_job = None
                    robot.status = RobotStatus.ERROR
                    robot.last_error = "Cannot reach pickup location"
    
    def _update_robot_with_job(self, robot: Robot, occupied_positions: Set[Tuple[int, int]]):
        """
        Update robot that has an assigned job.
        Handles pickup → transit → dropoff → return to start flow.
        
        Args:
            robot: Robot to update
            occupied_positions: Set of occupied grid positions
        """
        job = robot.current_job
        
        # Handle returning to start
        if robot.status == RobotStatus.RETURNING_TO_START:
            if robot.path:
                reached = robot.move_along_path()
                if reached:
                    # Reached starting station
                    robot.complete_job()
                    self.job_manager.complete_job(job)
                    print(f"✓ Robot {robot.id} returned to starting station, job complete")
            else:
                # Generate path to starting station
                starting_station = self.warehouse_grid.get_starting_station()
                if starting_station:
                    occupied = occupied_positions - {(robot.x, robot.y)}
                    path = self.pathfinder.find_path((robot.x, robot.y), starting_station, occupied)
                    if path:
                        robot.path = path
            return
        
        # Handle pickup action
        if robot.status == RobotStatus.PICKING_UP:
            if robot.action_start_time is None:
                robot.action_start_time = time.time()
            # Simulate 1-2 second pickup delay
            if time.time() - robot.action_start_time >= 1.5:
                robot.complete_pickup()
                job.start_transit()
                # Generate path to delivery location
                occupied = occupied_positions - {(robot.x, robot.y)}
                path = self.pathfinder.find_path((robot.x, robot.y), job.delivery, occupied)
                if path:
                    robot.path = path
                    robot.status = RobotStatus.EN_ROUTE
                else:
                    self.job_manager.fail_job(job, "Cannot reach delivery location")
                    robot.current_job = None
                    robot.status = RobotStatus.ERROR
            return
        
        # Handle dropoff action
        if robot.status == RobotStatus.DROPPING_OFF:
            if robot.action_start_time is None:
                robot.action_start_time = time.time()
            # Simulate 1-2 second dropoff delay
            if time.time() - robot.action_start_time >= 1.5:
                robot.complete_dropoff()
                job.start_dropoff()
                # Generate path back to starting station
                starting_station = self.warehouse_grid.get_starting_station()
                if starting_station:
                    occupied = occupied_positions - {(robot.x, robot.y)}
                    path = self.pathfinder.find_path((robot.x, robot.y), starting_station, occupied)
                    if path:
                        robot.path = path
                        robot.status = RobotStatus.RETURNING_TO_START
            return
        
        # Handle movement along path
        if robot.path:
            reached = robot.move_along_path()
            if reached:
                # Reached destination
                if not robot.pickup_complete:
                    # Reached pickup location
                    robot.start_pickup()
                    job.start_pickup()
                elif not robot.dropoff_complete:
                    # Reached delivery location
                    robot.start_dropoff()
                    job.start_dropoff()
        else:
            # No path, generate one
            if not robot.pickup_complete:
                # Going to pickup
                occupied = occupied_positions - {(robot.x, robot.y)}
                path = self.pathfinder.find_path((robot.x, robot.y), job.pickup, occupied)
                if path:
                    robot.path = path
                else:
                    self.job_manager.fail_job(job, "Lost path to pickup")
                    robot.current_job = None
                    robot.status = RobotStatus.ERROR
            elif not robot.dropoff_complete:
                # Going to delivery
                occupied = occupied_positions - {(robot.x, robot.y)}
                path = self.pathfinder.find_path((robot.x, robot.y), job.delivery, occupied)
                if path:
                    robot.path = path
                else:
                    self.job_manager.fail_job(job, "Lost path to delivery")
                    robot.current_job = None
                    robot.status = RobotStatus.ERROR
    
    def reset_fleet(self):
        """Reset all robots to starting station and clear all tasks/jobs."""
        starting_station = self.warehouse_grid.get_starting_station()
        for robot in self.robots:
            if starting_station:
                robot.reset(starting_station[0], starting_station[1])
            else:
                robot.reset()
        # Clear all tasks and jobs
        self.active_tasks.clear()
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        self.low_battery_alerts.clear()
        self.job_manager.reset()
        print("✓ Fleet reset: All robots returned to starting station, tasks and jobs cleared")
    
    def assign_task(
        self,
        robot_id: int,
        task_type: str,
        target_x: int,
        target_y: int,
        priority: int = 5
    ) -> Optional[Dict]:
        """
        Assign a task to a specific robot.
        
        Args:
            robot_id: ID of the robot to assign the task to
            task_type: Type of task ('pickup', 'dropoff', 'charge', 'move')
            target_x: Target x-coordinate
            target_y: Target y-coordinate
            priority: Task priority (1-10)
        
        Returns:
            Dictionary with task info and robot status, or None if failed
        """
        # Find the robot
        robot = self.get_robot_by_id(robot_id)
        if not robot:
            return None
        
        # Check if robot already has a task
        if robot.has_task():
            return {
                "success": False,
                "error": f"Robot {robot_id} already has an active task"
            }
        
        # Check if robot is in error state
        if robot.status == RobotStatus.ERROR:
            return {
                "success": False,
                "error": f"Robot {robot_id} is in error state"
            }
        
        # Validate target coordinates
        if not (0 <= target_x < self.grid_size and 0 <= target_y < self.grid_size):
            return {
                "success": False,
                "error": f"Invalid target coordinates: ({target_x}, {target_y})"
            }
        
        # Convert task_type string to TaskType enum
        try:
            task_type_enum = TaskType[task_type.upper()]
        except KeyError:
            return {
                "success": False,
                "error": f"Invalid task type: {task_type}"
            }
        
        # Create and assign task
        task = Task(robot_id, task_type_enum, target_x, target_y, priority)
        robot.assign_task(task)
        self.active_tasks.append(task)
        
        print(f"✓ Assigned {task_type} task {task.task_id} to Robot {robot_id} → ({target_x}, {target_y})")
        
        return {
            "success": True,
            "task": task.to_dict(),
            "robot": robot.to_dict()
        }
    
    def get_robot_by_id(self, robot_id: int) -> Optional[Robot]:
        """
        Get a robot by its ID.
        
        Args:
            robot_id: ID of the robot
        
        Returns:
            Robot object or None if not found
        """
        for robot in self.robots:
            if robot.id == robot_id:
                return robot
        return None
    
    def get_all_tasks(self) -> Dict:
        """
        Get all tasks (active, completed, failed).
        
        Returns:
            Dictionary with task lists
        """
        return {
            "active": [task.to_dict() for task in self.active_tasks],
            "completed": [task.to_dict() for task in self.completed_tasks[-50:]],  # Last 50
            "failed": [task.to_dict() for task in self.failed_tasks[-50:]]  # Last 50
        }
    
    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel an active task.
        
        Args:
            task_id: ID of the task to cancel
        
        Returns:
            True if task was cancelled, False otherwise
        """
        for task in self.active_tasks:
            if task.task_id == task_id:
                task.cancel()
                robot = self.get_robot_by_id(task.robot_id)
                if robot:
                    robot.current_task = None
                    robot.path = []
                    robot.status = RobotStatus.IDLE
                self.active_tasks.remove(task)
                print(f"✓ Cancelled task {task_id}")
                return True
        return False
    
    def get_fleet_status(self) -> List[Dict]:
        """
        Get current status of all robots.
        
        Returns:
            List of dictionaries containing robot data
        """
        return [robot.to_dict() for robot in self.robots]
    
    def get_fleet_summary(self) -> Dict:
        """
        Get summary statistics of the fleet.
        
        Returns:
            Dictionary with fleet statistics
        """
        total_battery = sum(robot.battery for robot in self.robots)
        avg_battery = total_battery / len(self.robots) if self.robots else 0
        
        status_counts = {}
        for robot in self.robots:
            status = robot.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count robots by task status
        idle_robots = len([r for r in self.robots if not r.has_task() and r.status == RobotStatus.IDLE])
        active_tasks_count = len(self.active_tasks)
        
        # Get errors
        errors = []
        for robot in self.robots:
            if robot.status == RobotStatus.ERROR or robot.last_error:
                errors.append({
                    "robot_id": robot.id,
                    "error": robot.last_error or "Unknown error",
                    "position": {"x": robot.x, "y": robot.y}
                })
        
        # Calculate uptime percentage
        total_robots = len(self.robots)
        operational_robots = len([r for r in self.robots if r.status != RobotStatus.ERROR])
        uptime_percent = (operational_robots / total_robots * 100) if total_robots > 0 else 0
        
        # Get recent low battery alerts (last 10)
        recent_alerts = self.low_battery_alerts[-10:] if self.low_battery_alerts else []
        
        # Get job statistics
        job_stats = self.job_manager.get_statistics()
        
        return {
            "total_robots": len(self.robots),
            "active_tasks": active_tasks_count,
            "idle_robots": idle_robots,
            "average_battery": round(avg_battery, 2),
            "status_distribution": status_counts,
            "grid_size": f"{self.grid_size}x{self.grid_size}",
            "errors": errors,
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "uptime_percent": round(uptime_percent, 1),
            "low_battery_alerts": recent_alerts,
            "total_distance_traveled": sum(r.total_distance_traveled for r in self.robots),
            "jobs": job_stats
        }
    
    def start_simulation(self):
        """Start the background simulation loop."""
        if self._simulation_thread is not None and self._simulation_thread.is_alive():
            print("⚠ Simulation already running")
            return
        
        self._stop_simulation = False
        self._simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._simulation_thread.start()
        print(f"✓ Simulation started (updating every {self.update_interval}s)")
    
    def stop_simulation(self):
        """Stop the background simulation loop."""
        if self._simulation_thread is None or not self._simulation_thread.is_alive():
            print("⚠ Simulation is not running")
            return
        
        self._stop_simulation = True
        if self._simulation_thread:
            self._simulation_thread.join(timeout=5)
        print("✓ Simulation stopped")
    
    def _simulation_loop(self):
        """Background loop that updates the fleet periodically."""
        print("🤖 Fleet simulation loop started")
        while not self._stop_simulation:
            time.sleep(self.update_interval)
            if not self._stop_simulation:
                self.update_fleet()
                # Optional: Print status for debugging
                # print(f"Fleet updated at {time.strftime('%H:%M:%S')}")
    
    def __repr__(self) -> str:
        """String representation of the fleet manager."""
        return (f"FleetManager(robots={self.num_robots}, "
                f"grid={self.grid_size}x{self.grid_size})")
