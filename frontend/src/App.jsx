import { useState, useEffect, useCallback } from 'react';
import { Play, Pause, RotateCcw, Activity, LayoutGrid, ClipboardList, Briefcase } from 'lucide-react';
import FleetGrid from './components/FleetGrid';
import EnvironmentGrid from './components/EnvironmentGrid';
import RobotSidebar from './components/RobotSidebar';
import ControlPanel from './components/ControlPanel';
import ManagementDashboard from './components/ManagementDashboard';
import JobManager from './components/JobManager';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [robots, setRobots] = useState([]);
  const [environment, setEnvironment] = useState(null);
  const [isSimulationRunning, setIsSimulationRunning] = useState(true);
  const [fleetSummary, setFleetSummary] = useState(null);
  const [gridSize, setGridSize] = useState(20);
  const [updateInterval, setUpdateInterval] = useState(2000);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [activeTab, setActiveTab] = useState('grid'); // 'grid', 'management', or 'jobs'
  const [useEnvironmentView, setUseEnvironmentView] = useState(true); // Toggle between old and new grid
  const [jobs, setJobs] = useState({ pending: [], active: [], completed: [], failed: [], cancelled: [] });
  const [continuousStatus, setContinuousStatus] = useState({ enabled: false, max_jobs: 3, interval: 5 });

  // Fetch robots from backend
  const fetchRobots = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/robots`);
      if (!response.ok) throw new Error('Failed to fetch robots');
      const data = await response.json();
      setRobots(data);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching robots:', err);
    }
  }, []);

  // Fetch fleet summary
  const fetchFleetSummary = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/fleet/summary`);
      if (!response.ok) throw new Error('Failed to fetch fleet summary');
      const data = await response.json();
      setFleetSummary(data);
    } catch (err) {
      console.error('Error fetching fleet summary:', err);
    }
  }, []);

  // Fetch environment data
  const fetchEnvironment = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/environment`);
      if (!response.ok) throw new Error('Failed to fetch environment');
      const data = await response.json();
      setEnvironment(data);
      setGridSize(data.width); // Update grid size from environment
    } catch (err) {
      console.error('Error fetching environment:', err);
    }
  }, []);

  // Fetch jobs
  const fetchJobs = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs`);
      if (!response.ok) throw new Error('Failed to fetch jobs');
      const data = await response.json();
      setJobs(data);
    } catch (err) {
      console.error('Error fetching jobs:', err);
    }
  }, []);

  // Fetch continuous status
  const fetchContinuousStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/continuous/status`);
      if (!response.ok) throw new Error('Failed to fetch continuous status');
      const data = await response.json();
      setContinuousStatus(data);
    } catch (err) {
      console.error('Error fetching continuous status:', err);
    }
  }, []);

  // Add manual job
  const handleAddJob = async (pickup_x, pickup_y, priority) => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/add?pickup_x=${pickup_x}&pickup_y=${pickup_y}&priority=${priority}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to add job');
      await fetchJobs(); // Refresh jobs
    } catch (err) {
      console.error('Error adding job:', err);
      alert('Failed to add job: ' + err.message);
    }
  };

  // Start continuous mode
  const handleStartContinuous = async (max_jobs, interval) => {
    try {
      const response = await fetch(`${API_BASE_URL}/continuous/start?max_jobs=${max_jobs}&interval=${interval}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to start continuous mode');
      await fetchContinuousStatus(); // Refresh status
    } catch (err) {
      console.error('Error starting continuous mode:', err);
      alert('Failed to start continuous mode: ' + err.message);
    }
  };

  // Stop continuous mode
  const handleStopContinuous = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/continuous/stop`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to stop continuous mode');
      await fetchContinuousStatus(); // Refresh status
    } catch (err) {
      console.error('Error stopping continuous mode:', err);
      alert('Failed to stop continuous mode: ' + err.message);
    }
  };

  // Delete job
  const handleDeleteJob = async (jobId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete job');
      await fetchJobs(); // Refresh jobs
    } catch (err) {
      console.error('Error deleting job:', err);
      alert('Failed to delete job: ' + err.message);
    }
  };

  // Reset fleet
  const handleReset = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reset`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to reset fleet');
      const data = await response.json();
      setRobots(data.robots);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error resetting fleet:', err);
    }
  };

  // Toggle simulation
  const toggleSimulation = () => {
    setIsSimulationRunning(prev => !prev);
  };

  // Initial fetch
  useEffect(() => {
    fetchRobots();
    fetchFleetSummary();
    fetchEnvironment();
    fetchJobs();
    fetchContinuousStatus();
  }, [fetchRobots, fetchFleetSummary, fetchEnvironment, fetchJobs, fetchContinuousStatus]);

  // Polling effect
  useEffect(() => {
    if (!isSimulationRunning) return;

    const interval = setInterval(() => {
      fetchRobots();
      fetchFleetSummary();
      fetchJobs();
      fetchContinuousStatus();
    }, updateInterval);

    return () => clearInterval(interval);
  }, [isSimulationRunning, updateInterval, fetchRobots, fetchFleetSummary, fetchJobs, fetchContinuousStatus]);

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-title">
            <Activity size={32} className="header-icon" />
            <div>
              <h1>Warehouse Fleet Management System</h1>
              <p className="header-subtitle">
                Real-time robot monitoring, task assignment & fleet control
              </p>
            </div>
          </div>
          
          <div className="header-controls">
            <button
              className={`btn ${isSimulationRunning ? 'btn-pause' : 'btn-play'}`}
              onClick={toggleSimulation}
              title={isSimulationRunning ? 'Pause Updates' : 'Resume Updates'}
            >
              {isSimulationRunning ? (
                <>
                  <Pause size={20} />
                  <span>Pause</span>
                </>
              ) : (
                <>
                  <Play size={20} />
                  <span>Resume</span>
                </>
              )}
            </button>
            
            <button
              className="btn btn-reset"
              onClick={handleReset}
              title="Reset All Robots"
            >
              <RotateCcw size={20} />
              <span>Reset Fleet</span>
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="tab-navigation">
          <button
            className={`tab-btn ${activeTab === 'grid' ? 'active' : ''}`}
            onClick={() => setActiveTab('grid')}
          >
            <LayoutGrid size={20} />
            <span>Grid View</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'management' ? 'active' : ''}`}
            onClick={() => setActiveTab('management')}
          >
            <ClipboardList size={20} />
            <span>Fleet Management</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveTab('jobs')}
          >
            <Briefcase size={20} />
            <span>Job Management</span>
          </button>
        </div>

        {/* Status Bar */}
        <div className="status-bar">
          <div className="status-item">
            <span className="status-label">Total Robots:</span>
            <span className="status-value">{robots.length}</span>
          </div>
          
          {fleetSummary && (
            <>
              <div className="status-item">
                <span className="status-label">Active Tasks:</span>
                <span className="status-value">{fleetSummary.active_tasks}</span>
              </div>

              <div className="status-item">
                <span className="status-label">Idle:</span>
                <span className="status-value">{fleetSummary.idle_robots}</span>
              </div>
              
              <div className="status-item">
                <span className="status-label">Avg Battery:</span>
                <span className="status-value">
                  {fleetSummary.average_battery.toFixed(1)}%
                </span>
              </div>
              
              <div className="status-item">
                <span className="status-label">Completed:</span>
                <span className="status-value">{fleetSummary.completed_tasks}</span>
              </div>

              <div className="status-item">
                <span className="status-label">Uptime:</span>
                <span className="status-value">{fleetSummary.uptime_percent}%</span>
              </div>
            </>
          )}
          
          <div className="status-item">
            <span className="status-label">Status:</span>
            <span className={`status-indicator ${isSimulationRunning ? 'active' : 'paused'}`}>
              {isSimulationRunning ? '● Running' : '■ Paused'}
            </span>
          </div>

          {lastUpdate && (
            <div className="status-item">
              <span className="status-label">Last Update:</span>
              <span className="status-value">
                {lastUpdate.toLocaleTimeString()}
              </span>
            </div>
          )}
        </div>

        {error && (
          <div className="error-banner">
            ⚠️ {error}
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="app-main">
        {activeTab === 'grid' ? (
          <>
            {/* Grid Visualization with Environment */}
            <div className="grid-container">
              {useEnvironmentView ? (
                <EnvironmentGrid 
                  robots={robots} 
                  environment={environment}
                  gridSize={gridSize}
                />
              ) : (
                <FleetGrid 
                  robots={robots} 
                  gridSize={gridSize}
                />
              )}
            </div>

            {/* Robot Info Sidebar */}
            <aside className="sidebar">
              <RobotSidebar robots={robots} fleetSummary={fleetSummary} />
            </aside>
          </>
        ) : activeTab === 'management' ? (
          /* Management Dashboard */
          <div className="management-container">
            <ManagementDashboard 
              robots={robots}
              fleetSummary={fleetSummary}
              onRefresh={() => {
                fetchRobots();
                fetchFleetSummary();
                fetchEnvironment();
              }}
            />
          </div>
        ) : (
          /* Job Management */
          <div className="jobs-container">
            <JobManager
              jobs={jobs}
              continuousStatus={continuousStatus}
              onAddJob={handleAddJob}
              onStartContinuous={handleStartContinuous}
              onStopContinuous={handleStopContinuous}
              onDeleteJob={handleDeleteJob}
              gridSize={gridSize}
            />
          </div>
        )}
      </main>

      {/* Control Panel (Optional Configuration) */}
      <ControlPanel
        gridSize={gridSize}
        setGridSize={setGridSize}
        updateInterval={updateInterval}
        setUpdateInterval={setUpdateInterval}
      />
    </div>
  );
}

export default App;
