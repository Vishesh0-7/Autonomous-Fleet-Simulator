"""
Job Manager
Manages delivery jobs including job queue, assignment, and completion tracking.
"""

from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum
import uuid


class JobStatus(str, Enum):
    """Status of a delivery job"""
    PENDING = "pending"           # Waiting to be assigned
    ASSIGNED = "assigned"         # Assigned to a robot
    PICKING_UP = "picking_up"     # Robot at pickup location
    IN_TRANSIT = "in_transit"     # Robot moving to delivery
    DROPPING_OFF = "dropping_off" # Robot at delivery location
    COMPLETED = "completed"       # Job finished
    FAILED = "failed"             # Job failed (robot died, path blocked, etc.)
    CANCELLED = "cancelled"       # Job manually cancelled


class Job:
    """
    Represents a delivery job with pickup and delivery locations.
    
    Attributes:
        job_id (str): Unique identifier for the job
        pickup (Tuple[int, int]): Pickup location (x, y)
        delivery (Tuple[int, int]): Delivery location (x, y)
        status (JobStatus): Current status of the job
        assigned_robot_id (int): ID of robot assigned to this job
        created_at (datetime): When the job was created
        started_at (datetime): When the job was started
        completed_at (datetime): When the job was completed
        priority (int): Job priority (1-10, higher = more important)
    """
    
    def __init__(self, pickup: Tuple[int, int], delivery: Tuple[int, int], priority: int = 5):
        """
        Initialize a new job.
        
        Args:
            pickup: Pickup location (x, y)
            delivery: Delivery location (x, y)
            priority: Job priority (1-10, default: 5)
        """
        self.job_id = str(uuid.uuid4())[:8]
        self.pickup = pickup
        self.delivery = delivery
        self.status = JobStatus.PENDING
        self.assigned_robot_id: Optional[int] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.priority = max(1, min(10, priority))  # Clamp to 1-10
        self.pickup_time: Optional[datetime] = None
        self.delivery_time: Optional[datetime] = None
    
    def assign_to_robot(self, robot_id: int):
        """Assign this job to a robot"""
        self.assigned_robot_id = robot_id
        self.status = JobStatus.ASSIGNED
        self.started_at = datetime.now()
    
    def start_pickup(self):
        """Mark job as being picked up"""
        self.status = JobStatus.PICKING_UP
        self.pickup_time = datetime.now()
    
    def start_transit(self):
        """Mark job as in transit to delivery"""
        self.status = JobStatus.IN_TRANSIT
    
    def start_dropoff(self):
        """Mark job as being dropped off"""
        self.status = JobStatus.DROPPING_OFF
        self.delivery_time = datetime.now()
    
    def complete(self):
        """Mark job as completed"""
        self.status = JobStatus.COMPLETED
        self.completed_at = datetime.now()
    
    def fail(self, reason: str = "Unknown"):
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.completed_at = datetime.now()
        print(f"✗ Job {self.job_id} failed: {reason}")
    
    def cancel(self):
        """Cancel the job"""
        self.status = JobStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def get_duration(self) -> Optional[float]:
        """Get job duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def to_dict(self) -> Dict:
        """Convert job to dictionary for JSON serialization"""
        return {
            "job_id": self.job_id,
            "pickup": {"x": self.pickup[0], "y": self.pickup[1]},
            "delivery": {"x": self.delivery[0], "y": self.delivery[1]},
            "status": self.status.value,
            "assigned_robot_id": self.assigned_robot_id,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration": self.get_duration()
        }


class JobManager:
    """
    Manages the job queue and assignment logic.
    
    Attributes:
        pending_jobs (List[Job]): Jobs waiting to be assigned
        active_jobs (List[Job]): Jobs currently being executed
        completed_jobs (List[Job]): Jobs that have been completed
        failed_jobs (List[Job]): Jobs that failed
        environment: Reference to warehouse environment for finding delivery zones
    """
    
    def __init__(self, environment=None):
        """Initialize the job manager"""
        self.pending_jobs: List[Job] = []
        self.active_jobs: List[Job] = []
        self.completed_jobs: List[Job] = []
        self.failed_jobs: List[Job] = []
        self.cancelled_jobs: List[Job] = []
        self.environment = environment
    
    def add_job(self, pickup: Tuple[int, int], delivery: Optional[Tuple[int, int]] = None, priority: int = 5) -> Job:
        """
        Add a new job to the queue. If no delivery location is provided,
        automatically finds the nearest delivery zone.
        
        Args:
            pickup: Pickup location (x, y)
            delivery: Delivery location (x, y) - if None, finds nearest delivery zone
            priority: Job priority (1-10)
        
        Returns:
            The created Job object
        """
        # Auto-find nearest delivery zone if not provided
        if delivery is None and self.environment:
            delivery = self.environment.find_nearest_delivery_zone(pickup[0], pickup[1])
            if delivery is None:
                raise ValueError("No delivery zones available in the environment")
        elif delivery is None:
            raise ValueError("No delivery location provided and no environment set")
        
        job = Job(pickup, delivery, priority)
        self.pending_jobs.append(job)
        # Sort by priority (higher priority first)
        self.pending_jobs.sort(key=lambda j: j.priority, reverse=True)
        print(f"✓ Added job {job.job_id}: Pickup {pickup} → Auto-delivery {delivery} (Priority: {priority})")
        return job
    
    def add_job_pickup_only(self, pickup: Tuple[int, int], priority: int = 5) -> Job:
        """
        Add a new job with only pickup location - automatically finds nearest delivery zone.
        
        Args:
            pickup: Pickup location (x, y)
            priority: Job priority (1-10)
        
        Returns:
            The created Job object
        """
        return self.add_job(pickup, None, priority)
    
    def set_environment(self, environment):
        """Set the environment reference for automatic delivery zone finding"""
        self.environment = environment
    
    def get_next_job(self) -> Optional[Job]:
        """
        Get the next highest-priority pending job.
        
        Returns:
            The next Job or None if no jobs available
        """
        if self.pending_jobs:
            return self.pending_jobs[0]
        return None
        """
        Get the next highest-priority pending job.
        
        Returns:
            The next Job or None if no jobs available
        """
        if self.pending_jobs:
            return self.pending_jobs[0]
        return None
    
    def assign_job(self, job: Job, robot_id: int):
        """
        Assign a job to a robot.
        
        Args:
            job: Job to assign
            robot_id: ID of robot to assign to
        """
        if job in self.pending_jobs:
            job.assign_to_robot(robot_id)
            self.pending_jobs.remove(job)
            self.active_jobs.append(job)
            print(f"→ Job {job.job_id} assigned to Robot {robot_id}")
    
    def complete_job(self, job: Job):
        """
        Mark a job as completed.
        
        Args:
            job: Job to complete
        """
        job.complete()
        if job in self.active_jobs:
            self.active_jobs.remove(job)
            self.completed_jobs.append(job)
            print(f"✓ Job {job.job_id} completed by Robot {job.assigned_robot_id} "
                  f"(Duration: {job.get_duration():.1f}s)")
    
    def fail_job(self, job: Job, reason: str = "Unknown"):
        """
        Mark a job as failed.
        
        Args:
            job: Job that failed
            reason: Reason for failure
        """
        job.fail(reason)
        if job in self.active_jobs:
            self.active_jobs.remove(job)
            self.failed_jobs.append(job)
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a job by ID.
        
        Args:
            job_id: ID of job to cancel
        
        Returns:
            True if job was cancelled, False if not found
        """
        # Check pending jobs
        for job in self.pending_jobs:
            if job.job_id == job_id:
                job.cancel()
                self.pending_jobs.remove(job)
                self.cancelled_jobs.append(job)
                print(f"✗ Job {job_id} cancelled (was pending)")
                return True
        
        # Check active jobs
        for job in self.active_jobs:
            if job.job_id == job_id:
                job.cancel()
                self.active_jobs.remove(job)
                self.cancelled_jobs.append(job)
                print(f"✗ Job {job_id} cancelled (was active on Robot {job.assigned_robot_id})")
                return True
        
        return False
    
    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Find a job by its ID across all lists"""
        for job in self.pending_jobs + self.active_jobs + self.completed_jobs + self.failed_jobs:
            if job.job_id == job_id:
                return job
        return None
    
    def get_robot_job(self, robot_id: int) -> Optional[Job]:
        """Get the active job for a specific robot"""
        for job in self.active_jobs:
            if job.assigned_robot_id == robot_id:
                return job
        return None
    
    def get_all_jobs(self) -> Dict:
        """Get all jobs organized by status"""
        return {
            "pending": [job.to_dict() for job in self.pending_jobs],
            "active": [job.to_dict() for job in self.active_jobs],
            "completed": [job.to_dict() for job in self.completed_jobs],
            "failed": [job.to_dict() for job in self.failed_jobs],
            "cancelled": [job.to_dict() for job in self.cancelled_jobs]
        }
    
    def get_statistics(self) -> Dict:
        """Get job statistics"""
        total_jobs = (len(self.pending_jobs) + len(self.active_jobs) + 
                     len(self.completed_jobs) + len(self.failed_jobs))
        
        avg_duration = None
        if self.completed_jobs:
            durations = [job.get_duration() for job in self.completed_jobs if job.get_duration()]
            avg_duration = sum(durations) / len(durations) if durations else None
        
        return {
            "total_jobs": total_jobs,
            "pending": len(self.pending_jobs),
            "active": len(self.active_jobs),
            "completed": len(self.completed_jobs),
            "failed": len(self.failed_jobs),
            "cancelled": len(self.cancelled_jobs),
            "success_rate": (len(self.completed_jobs) / total_jobs * 100) if total_jobs > 0 else 0,
            "average_duration": avg_duration
        }
    
    def clear_completed_jobs(self, keep_last: int = 10):
        """Clear old completed jobs, keeping only the most recent ones"""
        if len(self.completed_jobs) > keep_last:
            self.completed_jobs = self.completed_jobs[-keep_last:]
    
    def reset(self):
        """Reset all job queues"""
        self.pending_jobs.clear()
        self.active_jobs.clear()
        self.completed_jobs.clear()
        self.failed_jobs.clear()
        self.cancelled_jobs.clear()
        print("✓ Job manager reset: All job queues cleared")
