import { Battery, MapPin, Activity, TrendingUp } from 'lucide-react';
import './RobotSidebar.css';

const STATUS_COLORS = {
  moving: '#10b981',
  idle: '#3b82f6',
  charging: '#f59e0b',
  delivering: '#8b5cf6',
  returning: '#06b6d4',
  error: '#ef4444'
};

function RobotSidebar({ robots, fleetSummary }) {
  const getBatteryIcon = (battery) => {
    if (battery > 75) return '🔋';
    if (battery > 50) return '🔋';
    if (battery > 25) return '⚠️';
    return '🪫';
  };

  return (
    <div className="robot-sidebar">
      {/* Fleet Summary Card */}
      {fleetSummary && (
        <div className="summary-card">
          <h2 className="sidebar-title">
            <TrendingUp size={20} />
            Fleet Summary
          </h2>
          
          <div className="summary-stats">
            <div className="stat-item">
              <span className="stat-label">Total Robots</span>
              <span className="stat-value">{fleetSummary.total_robots}</span>
            </div>
            
            <div className="stat-item">
              <span className="stat-label">Average Battery</span>
              <span className="stat-value">
                {fleetSummary.average_battery.toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Status Distribution */}
          <div className="status-distribution">
            <h3>Status Distribution</h3>
            <div className="status-bars">
              {Object.entries(fleetSummary.status_distribution).map(([status, count]) => (
                <div key={status} className="status-bar-item">
                  <div className="status-bar-header">
                    <span className="status-name" style={{ color: STATUS_COLORS[status] }}>
                      ● {status}
                    </span>
                    <span className="status-count">{count}</span>
                  </div>
                  <div className="status-bar-bg">
                    <div 
                      className="status-bar-fill"
                      style={{
                        width: `${(count / fleetSummary.total_robots) * 100}%`,
                        backgroundColor: STATUS_COLORS[status],
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Robots List */}
      <div className="robots-list">
        <h2 className="sidebar-title">
          <Activity size={20} />
          Robot Details ({robots.length})
        </h2>

        <div className="robot-cards">
          {robots.length === 0 ? (
            <div className="empty-state">
              <p>No robots available</p>
            </div>
          ) : (
            robots
              .sort((a, b) => a.id - b.id)
              .map((robot) => (
                <div 
                  key={robot.id} 
                  className="robot-card"
                  style={{
                    borderLeft: `4px solid ${STATUS_COLORS[robot.status] || STATUS_COLORS.error}`
                  }}
                >
                  <div className="robot-card-header">
                    <div className="robot-info">
                      <span className="robot-card-id">Robot #{robot.id}</span>
                      <span 
                        className="robot-card-status"
                        style={{ color: STATUS_COLORS[robot.status] }}
                      >
                        ● {robot.status}
                      </span>
                    </div>
                  </div>

                  <div className="robot-card-body">
                    {/* Position */}
                    <div className="robot-detail">
                      <MapPin size={16} className="detail-icon" />
                      <span className="detail-label">Position:</span>
                      <span className="detail-value">({robot.x}, {robot.y})</span>
                    </div>

                    {/* Battery */}
                    <div className="robot-detail">
                      <Battery size={16} className="detail-icon" />
                      <span className="detail-label">Battery:</span>
                      <span className="detail-value">
                        {getBatteryIcon(robot.battery)} {robot.battery}%
                      </span>
                    </div>

                    {/* Battery Progress Bar */}
                    <div className="battery-progress">
                      <div 
                        className="battery-progress-fill"
                        style={{
                          width: `${robot.battery}%`,
                          backgroundColor: 
                            robot.battery > 50 ? '#10b981' :
                            robot.battery > 20 ? '#f59e0b' : '#ef4444',
                        }}
                      />
                    </div>
                  </div>
                </div>
              ))
          )}
        </div>
      </div>
    </div>
  );
}

export default RobotSidebar;
