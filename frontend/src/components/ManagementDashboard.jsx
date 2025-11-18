import { useState, useEffect } from 'react';
import { 
  ClipboardList, 
  PlayCircle, 
  XCircle, 
  AlertTriangle,
  TrendingUp,
  CheckCircle2,
  Clock,
  Battery
} from 'lucide-react';
import './ManagementDashboard.css';

const API_BASE_URL = 'http://localhost:8000';

const TASK_TYPES = [
  { value: 'pickup', label: 'Pickup', icon: '📦' },
  { value: 'dropoff', label: 'Drop-off', icon: '📍' },
  { value: 'charge', label: 'Charge', icon: '🔋' },
  { value: 'move', label: 'Move', icon: '🚶' },
  { value: 'patrol', label: 'Patrol', icon: '👁️' },
];

function ManagementDashboard({ robots, fleetSummary, onRefresh }) {
  const [selectedRobot, setSelectedRobot] = useState('');
  const [taskType, setTaskType] = useState('pickup');
  const [targetX, setTargetX] = useState('');
  const [targetY, setTargetY] = useState('');
  const [priority, setPriority] = useState(5);
  const [activeTasks, setActiveTasks] = useState([]);
  const [completedTasks, setCompletedTasks] = useState([]);
  const [failedTasks, setFailedTasks] = useState([]);
  const [assignmentStatus, setAssignmentStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch tasks
  const fetchTasks = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`);
      if (!response.ok) throw new Error('Failed to fetch tasks');
      const data = await response.json();
      setActiveTasks(data.active || []);
      setCompletedTasks(data.completed || []);
      setFailedTasks(data.failed || []);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  // Initial fetch and polling
  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 2000);
    return () => clearInterval(interval);
  }, []);

  // Handle task assignment
  const handleAssignTask = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setAssignmentStatus(null);

    try {
      const response = await fetch(`${API_BASE_URL}/assign_task`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          robot_id: parseInt(selectedRobot),
          task_type: taskType,
          target_x: parseInt(targetX),
          target_y: parseInt(targetY),
          priority: priority,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setAssignmentStatus({ success: true, message: `Task assigned successfully to Robot #${selectedRobot}` });
        // Reset form
        setTargetX('');
        setTargetY('');
        // Refresh data
        fetchTasks();
        if (onRefresh) onRefresh();
      } else {
        setAssignmentStatus({ success: false, message: data.detail || data.error || 'Failed to assign task' });
      }
    } catch (error) {
      setAssignmentStatus({ success: false, message: `Error: ${error.message}` });
    } finally {
      setIsSubmitting(false);
      // Clear status after 5 seconds
      setTimeout(() => setAssignmentStatus(null), 5000);
    }
  };

  // Cancel task
  const handleCancelTask = async (taskId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${taskId}/cancel`, {
        method: 'POST',
      });

      if (response.ok) {
        fetchTasks();
        if (onRefresh) onRefresh();
      }
    } catch (error) {
      console.error('Error cancelling task:', error);
    }
  };

  // Get available robots (idle or with low priority tasks)
  const availableRobots = robots.filter(r => 
    r.status === 'idle' || (r.status !== 'error' && r.battery > 20)
  );

  // Get low battery robots
  const lowBatteryRobots = robots.filter(r => r.battery < 30);

  return (
    <div className="management-dashboard">
      {/* Fleet Metrics Overview */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon total">
            <TrendingUp size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Total Robots</div>
            <div className="metric-value">{fleetSummary?.total_robots || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon active">
            <PlayCircle size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Active Tasks</div>
            <div className="metric-value">{fleetSummary?.active_tasks || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon idle">
            <Clock size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Idle Robots</div>
            <div className="metric-value">{fleetSummary?.idle_robots || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon completed">
            <CheckCircle2 size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Completed Tasks</div>
            <div className="metric-value">{fleetSummary?.completed_tasks || 0}</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon battery">
            <Battery size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Avg Battery</div>
            <div className="metric-value">{fleetSummary?.average_battery?.toFixed(1) || 0}%</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon uptime">
            <TrendingUp size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Uptime</div>
            <div className="metric-value">{fleetSummary?.uptime_percent?.toFixed(1) || 100}%</div>
          </div>
        </div>
      </div>

      {/* Low Battery Alerts */}
      {lowBatteryRobots.length > 0 && (
        <div className="alert-banner low-battery">
          <AlertTriangle size={20} />
          <span>
            <strong>Low Battery Alert:</strong> {lowBatteryRobots.length} robot(s) need charging -{' '}
            {lowBatteryRobots.map(r => `Robot #${r.id} (${r.battery}%)`).join(', ')}
          </span>
        </div>
      )}

      {/* Error Alerts */}
      {fleetSummary?.errors && fleetSummary.errors.length > 0 && (
        <div className="alert-banner error">
          <XCircle size={20} />
          <span>
            <strong>Errors:</strong> {fleetSummary.errors.length} robot(s) in error state
          </span>
        </div>
      )}

      <div className="dashboard-content">
        {/* Task Assignment Form */}
        <div className="task-assignment-card">
          <h2 className="card-title">
            <ClipboardList size={20} />
            Assign New Task
          </h2>

          <form onSubmit={handleAssignTask} className="task-form">
            <div className="form-group">
              <label>Select Robot</label>
              <select
                value={selectedRobot}
                onChange={(e) => setSelectedRobot(e.target.value)}
                required
                className="form-select"
              >
                <option value="">Choose a robot...</option>
                {availableRobots.map(robot => (
                  <option key={robot.id} value={robot.id}>
                    Robot #{robot.id} - {robot.status} - Battery: {robot.battery}%
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Task Type</label>
              <div className="task-type-grid">
                {TASK_TYPES.map(type => (
                  <button
                    key={type.value}
                    type="button"
                    className={`task-type-btn ${taskType === type.value ? 'active' : ''}`}
                    onClick={() => setTaskType(type.value)}
                  >
                    <span className="task-icon">{type.icon}</span>
                    <span>{type.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Target X (0-19)</label>
                <input
                  type="number"
                  min="0"
                  max="19"
                  value={targetX}
                  onChange={(e) => setTargetX(e.target.value)}
                  required
                  className="form-input"
                  placeholder="0-19"
                />
              </div>

              <div className="form-group">
                <label>Target Y (0-19)</label>
                <input
                  type="number"
                  min="0"
                  max="19"
                  value={targetY}
                  onChange={(e) => setTargetY(e.target.value)}
                  required
                  className="form-input"
                  placeholder="0-19"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Priority: {priority}</label>
              <input
                type="range"
                min="1"
                max="10"
                value={priority}
                onChange={(e) => setPriority(parseInt(e.target.value))}
                className="form-slider"
              />
              <div className="priority-labels">
                <span>Low (1)</span>
                <span>High (10)</span>
              </div>
            </div>

            <button
              type="submit"
              className="btn-assign"
              disabled={isSubmitting || !selectedRobot}
            >
              {isSubmitting ? 'Assigning...' : 'Assign Task'}
            </button>

            {assignmentStatus && (
              <div className={`assignment-status ${assignmentStatus.success ? 'success' : 'error'}`}>
                {assignmentStatus.message}
              </div>
            )}
          </form>
        </div>

        {/* Active Tasks List */}
        <div className="tasks-list-card">
          <h2 className="card-title">
            <PlayCircle size={20} />
            Active Tasks ({activeTasks.length})
          </h2>

          <div className="tasks-list">
            {activeTasks.length === 0 ? (
              <div className="empty-state">No active tasks</div>
            ) : (
              activeTasks.map(task => (
                <div key={task.task_id} className="task-item active">
                  <div className="task-header">
                    <div className="task-id">{task.task_id}</div>
                    <button
                      className="btn-cancel-task"
                      onClick={() => handleCancelTask(task.task_id)}
                      title="Cancel Task"
                    >
                      <XCircle size={16} />
                    </button>
                  </div>
                  <div className="task-details">
                    <span className="task-robot">Robot #{task.robot_id}</span>
                    <span className="task-type">{task.task_type}</span>
                    <span className="task-target">→ ({task.target.x}, {task.target.y})</span>
                  </div>
                  <div className="task-progress">
                    <span>Status: {task.status}</span>
                    <span>Steps: {task.actual_steps}/{task.estimated_steps || '?'}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Recent Completed Tasks */}
      {completedTasks.length > 0 && (
        <div className="completed-tasks-card">
          <h3 className="card-title">
            <CheckCircle2 size={18} />
            Recent Completed Tasks ({completedTasks.length})
          </h3>
          <div className="tasks-list horizontal">
            {completedTasks.slice(0, 10).map(task => (
              <div key={task.task_id} className="task-item completed">
                <div className="task-id">{task.task_id}</div>
                <div className="task-summary">
                  Robot #{task.robot_id} • {task.task_type}
                </div>
                <div className="task-duration">
                  {task.duration ? `${task.duration.toFixed(1)}s` : 'N/A'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default ManagementDashboard;
