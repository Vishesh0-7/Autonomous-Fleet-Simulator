import { motion } from 'framer-motion';
import './FleetGrid.css';

const STATUS_COLORS = {
  moving: '#10b981',      // Green
  idle: '#3b82f6',        // Blue
  charging: '#f59e0b',    // Yellow/Orange
  delivering: '#8b5cf6',  // Purple
  returning: '#06b6d4',   // Cyan
  error: '#ef4444'        // Red
};

function FleetGrid({ robots, gridSize = 20 }) {
  // Calculate cell size based on available space (max 600px grid)
  const maxGridSize = 600;
  const cellSize = Math.floor(maxGridSize / gridSize);
  const actualGridSize = cellSize * gridSize;

  return (
    <div className="fleet-grid-wrapper">
      <div 
        className="fleet-grid"
        style={{
          gridTemplateColumns: `repeat(${gridSize}, ${cellSize}px)`,
          gridTemplateRows: `repeat(${gridSize}, ${cellSize}px)`,
          width: `${actualGridSize}px`,
          height: `${actualGridSize}px`,
        }}
      >
        {/* Grid cells */}
        {Array.from({ length: gridSize * gridSize }).map((_, index) => {
          const x = index % gridSize;
          const y = Math.floor(index / gridSize);
          
          return (
            <div
              key={`cell-${x}-${y}`}
              className="grid-cell"
              style={{
                gridColumn: x + 1,
                gridRow: y + 1,
              }}
            />
          );
        })}

        {/* Robots */}
        {robots.map((robot) => {
          const color = STATUS_COLORS[robot.status] || STATUS_COLORS.error;
          const robotSize = cellSize * 0.7;
          
          return (
            <motion.div
              key={robot.id}
              className="robot"
              initial={false}
              animate={{
                gridColumn: robot.x + 1,
                gridRow: robot.y + 1,
              }}
              transition={{
                type: 'spring',
                stiffness: 300,
                damping: 30,
              }}
              style={{
                width: `${robotSize}px`,
                height: `${robotSize}px`,
              }}
            >
              <motion.div
                className="robot-circle"
                style={{
                  backgroundColor: color,
                  boxShadow: `0 0 20px ${color}`,
                }}
                animate={{
                  scale: [1, 1.1, 1],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              >
                <span className="robot-id">{robot.id}</span>
              </motion.div>
              
              {/* Battery indicator */}
              <div className="battery-indicator">
                <div 
                  className="battery-bar"
                  style={{
                    width: `${robot.battery}%`,
                    backgroundColor: robot.battery > 50 ? '#10b981' : 
                                   robot.battery > 20 ? '#f59e0b' : '#ef4444',
                  }}
                />
              </div>
              
              {/* Status badge */}
              <div 
                className="status-badge"
                style={{ borderColor: color }}
              >
                {robot.status}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="grid-legend">
        <h3>Status Legend</h3>
        <div className="legend-items">
          {Object.entries(STATUS_COLORS).map(([status, color]) => (
            <div key={status} className="legend-item">
              <span 
                className="legend-dot"
                style={{ backgroundColor: color }}
              />
              <span className="legend-label">
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default FleetGrid;
