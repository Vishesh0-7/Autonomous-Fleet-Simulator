import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Pause, 
  Plus, 
  Trash2, 
  RefreshCw, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Package,
  MapPin,
  Settings
} from 'lucide-react';
import './JobManager.css';

/**
 * JobManager Component
 * Manages job creation, continuous operation mode, and job queue visualization
 */
const JobManager = ({ 
  jobs = { pending: [], active: [], completed: [], failed: [], cancelled: [] },
  continuousStatus = { enabled: false, max_jobs: 3, interval: 5 },
  onAddJob,
  onStartContinuous,
  onStopContinuous,
  onDeleteJob,
  gridSize = 20
}) => {
  const [newJob, setNewJob] = useState({ pickup_x: '', pickup_y: '', priority: 5 });
  const [continuousConfig, setContinuousConfig] = useState({
    max_jobs: continuousStatus.max_jobs || 3,
    interval: continuousStatus.interval || 5
  });
  const [showSettings, setShowSettings] = useState(false);

  // Update continuous config when status changes
  useEffect(() => {
    setContinuousConfig({
      max_jobs: continuousStatus.max_jobs || 3,
      interval: continuousStatus.interval || 5
    });
  }, [continuousStatus]);

  /**
   * Handle manual job creation
   */
  const handleAddJob = async (e) => {
    e.preventDefault();
    
    if (!newJob.pickup_x || !newJob.pickup_y) {
      alert('Please provide pickup coordinates');
      return;
    }

    const pickup_x = parseInt(newJob.pickup_x);
    const pickup_y = parseInt(newJob.pickup_y);

    if (pickup_x < 0 || pickup_x >= gridSize || pickup_y < 0 || pickup_y >= gridSize) {
      alert(`Coordinates must be between 0 and ${gridSize - 1}`);
      return;
    }

    if (onAddJob) {
      await onAddJob(pickup_x, pickup_y, newJob.priority);
      setNewJob({ pickup_x: '', pickup_y: '', priority: 5 });
    }
  };

  /**
   * Handle continuous mode toggle
   */
  const handleToggleContinuous = async () => {
    if (continuousStatus.enabled) {
      if (onStopContinuous) {
        await onStopContinuous();
      }
    } else {
      if (onStartContinuous) {
        await onStartContinuous(continuousConfig.max_jobs, continuousConfig.interval);
      }
    }
  };

  /**
   * Get status color for job
   */
  const getJobStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return '#6b7280';
      case 'assigned':
      case 'picking_up':
      case 'in_transit':
      case 'dropping_off':
        return '#3b82f6';
      case 'completed':
        return '#10b981';
      case 'failed':
        return '#ef4444';
      case 'cancelled':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  /**
   * Get status icon for job
   */
  const getJobStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock size={16} />;
      case 'assigned':
      case 'picking_up':
      case 'in_transit':
      case 'dropping_off':
        return <RefreshCw size={16} className="animate-spin" />;
      case 'completed':
        return <CheckCircle size={16} />;
      case 'failed':
        return <XCircle size={16} />;
      case 'cancelled':
        return <AlertCircle size={16} />;
      default:
        return <Clock size={16} />;
    }
  };

  /**
   * Render job list
   */
  const renderJobList = (jobList, title, bgColor) => {
    if (!jobList || jobList.length === 0) return null;

    return (
      <div className="job-list">
        <h4 className="job-list-title" style={{ color: bgColor }}>
          {title} ({jobList.length})
        </h4>
        <div className="job-items">
          {jobList.map((job) => (
            <motion.div
              key={job.job_id}
              className="job-item"
              style={{ borderLeftColor: getJobStatusColor(job.status) }}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="job-header">
                <div className="job-status">
                  {getJobStatusIcon(job.status)}
                  <span className="job-id">Job {job.job_id}</span>
                </div>
                <div className="job-priority">
                  Priority: {job.priority}
                </div>
              </div>
              
              <div className="job-details">
                <div className="job-location">
                  <MapPin size={14} />
                  <span>Pickup: ({job.pickup?.x}, {job.pickup?.y})</span>
                </div>
                <div className="job-location">
                  <Package size={14} />
                  <span>Delivery: ({job.delivery?.x}, {job.delivery?.y})</span>
                </div>
                {job.assigned_robot_id && (
                  <div className="job-robot">
                    Robot: {job.assigned_robot_id}
                  </div>
                )}
              </div>

              {job.status === 'pending' && onDeleteJob && (
                <button
                  className="job-delete-btn"
                  onClick={() => onDeleteJob(job.job_id)}
                  title="Cancel job"
                >
                  <Trash2 size={14} />
                </button>
              )}
            </motion.div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="job-manager">
      <div className="job-manager-header">
        <h3>Job Management</h3>
        <button
          className="settings-btn"
          onClick={() => setShowSettings(!showSettings)}
        >
          <Settings size={16} />
        </button>
      </div>

      {/* Continuous Operation Panel */}
      <div className="continuous-panel">
        <div className="continuous-header">
          <h4>Continuous Operation</h4>
          <div className={`continuous-status ${continuousStatus.enabled ? 'enabled' : 'disabled'}`}>
            {continuousStatus.enabled ? 'ACTIVE' : 'INACTIVE'}
          </div>
        </div>

        {showSettings && (
          <motion.div
            className="continuous-settings"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            transition={{ duration: 0.3 }}
          >
            <div className="setting-row">
              <label>Max Active Jobs:</label>
              <input
                type="number"
                min="1"
                max="20"
                value={continuousConfig.max_jobs}
                onChange={(e) => setContinuousConfig(prev => ({
                  ...prev,
                  max_jobs: parseInt(e.target.value)
                }))}
                disabled={continuousStatus.enabled}
              />
            </div>
            <div className="setting-row">
              <label>Generation Interval (s):</label>
              <input
                type="number"
                min="1"
                max="60"
                value={continuousConfig.interval}
                onChange={(e) => setContinuousConfig(prev => ({
                  ...prev,
                  interval: parseInt(e.target.value)
                }))}
                disabled={continuousStatus.enabled}
              />
            </div>
          </motion.div>
        )}

        <button
          className={`continuous-toggle ${continuousStatus.enabled ? 'enabled' : 'disabled'}`}
          onClick={handleToggleContinuous}
        >
          {continuousStatus.enabled ? (
            <>
              <Pause size={16} />
              Stop Continuous Mode
            </>
          ) : (
            <>
              <Play size={16} />
              Start Continuous Mode
            </>
          )}
        </button>

        {continuousStatus.enabled && (
          <div className="continuous-info">
            <div className="info-item">
              <span>Max Jobs: {continuousStatus.max_jobs}</span>
            </div>
            <div className="info-item">
              <span>Interval: {continuousStatus.interval}s</span>
            </div>
            <div className="info-item">
              <span>Pickup Zones: {continuousStatus.pickup_zones || 0}</span>
            </div>
          </div>
        )}
      </div>

      {/* Manual Job Creation */}
      {!continuousStatus.enabled && (
        <div className="manual-job-panel">
          <h4>Add Manual Job</h4>
          <form onSubmit={handleAddJob} className="job-form">
            <div className="form-row">
              <div className="input-group">
                <label>Pickup X:</label>
                <input
                  type="number"
                  min="0"
                  max={gridSize - 1}
                  value={newJob.pickup_x}
                  onChange={(e) => setNewJob(prev => ({ ...prev, pickup_x: e.target.value }))}
                  placeholder="0"
                  required
                />
              </div>
              <div className="input-group">
                <label>Pickup Y:</label>
                <input
                  type="number"
                  min="0"
                  max={gridSize - 1}
                  value={newJob.pickup_y}
                  onChange={(e) => setNewJob(prev => ({ ...prev, pickup_y: e.target.value }))}
                  placeholder="0"
                  required
                />
              </div>
            </div>
            <div className="form-row">
              <div className="input-group">
                <label>Priority:</label>
                <select
                  value={newJob.priority}
                  onChange={(e) => setNewJob(prev => ({ ...prev, priority: parseInt(e.target.value) }))}
                >
                  {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map(p => (
                    <option key={p} value={p}>Priority {p}</option>
                  ))}
                </select>
              </div>
            </div>
            <button type="submit" className="add-job-btn">
              <Plus size={16} />
              Add Job
            </button>
          </form>
          <p className="auto-delivery-note">
            * Delivery location will be automatically assigned to the nearest delivery zone
          </p>
        </div>
      )}

      {/* Job Queue */}
      <div className="job-queue">
        <h4>Job Queue</h4>
        <div className="job-lists">
          {renderJobList(jobs.pending, 'Pending', '#6b7280')}
          {renderJobList(jobs.active, 'Active', '#3b82f6')}
          {renderJobList(jobs.completed?.slice(-5), 'Recent Completed', '#10b981')}
          {renderJobList(jobs.failed?.slice(-3), 'Recent Failed', '#ef4444')}
        </div>
      </div>
    </div>
  );
};

export default JobManager;