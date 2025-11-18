import React from 'react';
import { motion } from 'framer-motion';
import { Battery, BatteryWarning, Zap, Package, XCircle, Skull, MapPin, ShoppingCart, Flag } from 'lucide-react';
import './EnvironmentGrid.css';

/**
 * EnvironmentGrid Component
 * Renders the warehouse grid with environment features (obstacles, charging stations, delivery zones)
 * and overlays robots with battery indicators and animations.
 */
const EnvironmentGrid = ({ robots = [], environment = null, gridSize = 20 }) => {
  if (!environment) {
    return (
      <div className="environment-loading">
        <p>Loading environment...</p>
      </div>
    );
  }

  const { grid, width, height, charging_stations, delivery_zones, pickup_zones, starting_stations, obstacles } = environment;

  /**
   * Get cell type for a specific position
   */
  const getCellType = (x, y) => {
    if (!grid || y >= grid.length || x >= grid[y].length) {
      return 'empty';
    }
    return grid[y][x];
  };

  /**
   * Get CSS class for cell based on its type
   */
  const getCellClass = (cellType) => {
    switch (cellType) {
      case 'obstacle':
        return 'cell-obstacle';
      case 'charging_station':
        return 'cell-charging';
      case 'delivery_zone':
        return 'cell-delivery';
      case 'pickup_zone':
        return 'cell-pickup';
      case 'starting_station':
        return 'cell-starting';
      case 'empty':
      default:
        return 'cell-empty';
    }
  };

  /**
   * Get robot status color
   */
  const getRobotColor = (robot) => {
    if (robot.is_dead || robot.status === 'dead') {
      return '#dc2626'; // Red for dead
    }
    
    switch (robot.status) {
      case 'moving':
      case 'en_route':
        return '#10b981'; // Green
      case 'idle':
        return '#3b82f6'; // Blue
      case 'charging':
        return '#f59e0b'; // Amber/Yellow
      case 'delivering':
      case 'working':
        return '#8b5cf6'; // Purple
      case 'returning':
        return '#06b6d4'; // Cyan
      case 'error':
        return '#ef4444'; // Red
      default:
        return '#6b7280'; // Gray
    }
  };

  /**
   * Get battery icon based on level
   */
  const getBatteryIcon = (battery, isDead) => {
    if (isDead) {
      return <Skull size={16} className="battery-icon dead" />;
    }
    if (battery < 20) {
      return <BatteryWarning size={16} className="battery-icon critical" />;
    }
    if (battery < 50) {
      return <Battery size={16} className="battery-icon low" />;
    }
    return <Battery size={16} className="battery-icon normal" />;
  };

  /**
   * Render robot path if it exists
   */
  const renderPath = (robot) => {
    if (!robot.path || robot.path.length === 0) return null;

    return robot.path.map((pos, index) => {
      const [pathX, pathY] = pos;
      return (
        <motion.div
          key={`path-${robot.id}-${index}`}
          className="path-marker"
          style={{
            gridColumn: pathX + 1,
            gridRow: pathY + 1,
            opacity: 0.3 - (index * 0.02) // Fade out along path
          }}
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.2, delay: index * 0.05 }}
        />
      );
    });
  };

  /**
   * Render grid cells
   */
  const renderGrid = () => {
    const cells = [];
    
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const cellType = getCellType(x, y);
        const cellClass = getCellClass(cellType);
        
        cells.push(
          <div
            key={`cell-${x}-${y}`}
            className={`grid-cell ${cellClass}`}
            style={{
              gridColumn: x + 1,
              gridRow: y + 1
            }}
          >
            {/* Cell icon based on type */}
            {cellType === 'charging_station' && (
              <Zap size={14} className="cell-icon charging-icon" />
            )}
            {cellType === 'delivery_zone' && (
              <Package size={14} className="cell-icon delivery-icon" />
            )}
            {cellType === 'pickup_zone' && (
              <ShoppingCart size={14} className="cell-icon pickup-icon" />
            )}
            {cellType === 'starting_station' && (
              <Flag size={14} className="cell-icon starting-icon" />
            )}
            {cellType === 'obstacle' && (
              <XCircle size={14} className="cell-icon obstacle-icon" />
            )}
          </div>
        );
      }
    }
    
    return cells;
  };

  /**
   * Render robots with animations
   */
  const renderRobots = () => {
    return robots.map((robot) => {
      const color = getRobotColor(robot);
      const isDead = robot.is_dead || robot.status === 'dead';
      
      return (
        <React.Fragment key={`robot-fragment-${robot.id}`}>
          {/* Render robot's path */}
          {renderPath(robot)}
          
          {/* Render robot */}
          <motion.div
            key={`robot-${robot.id}`}
            className={`robot ${isDead ? 'robot-dead' : ''}`}
            style={{
              gridColumn: robot.x + 1,
              gridRow: robot.y + 1,
              backgroundColor: color,
              borderColor: color
            }}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ 
              scale: 1, 
              opacity: isDead ? 0.5 : 1,
              rotate: isDead ? 180 : 0
            }}
            transition={{
              type: 'spring',
              stiffness: 300,
              damping: 20
            }}
            layout
            layoutId={`robot-${robot.id}`}
          >
            {/* Robot ID */}
            <span className="robot-id">{robot.id}</span>
            
            {/* Battery indicator */}
            <div 
              className={`robot-battery ${isDead ? 'dead' : robot.battery < 20 ? 'critical' : robot.battery < 50 ? 'low' : ''}`}
              title={`Battery: ${robot.battery}%`}
            >
              {getBatteryIcon(robot.battery, isDead)}
              <span className="battery-text">{robot.battery}%</span>
            </div>
            
            {/* Status indicator dot */}
            <div className="robot-status-dot" style={{ backgroundColor: color }} />
          </motion.div>
        </React.Fragment>
      );
    });
  };

  return (
    <div className="environment-grid-wrapper">
      {/* Legend */}
      <div className="environment-legend">
        <div className="legend-item">
          <div className="legend-box cell-empty" />
          <span>Empty</span>
        </div>
        <div className="legend-item">
          <div className="legend-box cell-obstacle" />
          <span>Obstacle</span>
        </div>
        <div className="legend-item">
          <div className="legend-box cell-charging" />
          <Zap size={12} style={{ marginLeft: '4px' }} />
          <span>Charging Station</span>
        </div>
        <div className="legend-item">
          <div className="legend-box cell-delivery" />
          <Package size={12} style={{ marginLeft: '4px' }} />
          <span>Delivery Zone</span>
        </div>
        <div className="legend-item">
          <div className="legend-box cell-pickup" />
          <ShoppingCart size={12} style={{ marginLeft: '4px' }} />
          <span>Pickup Zone</span>
        </div>
        <div className="legend-item">
          <div className="legend-box cell-starting" />
          <Flag size={12} style={{ marginLeft: '4px' }} />
          <span>Starting Station</span>
        </div>
      </div>

      {/* Environment Info */}
      <div className="environment-info">
        <div className="info-item">
          <Flag size={16} />
          <span>{starting_stations?.length || 0} Starting Stations</span>
        </div>
        <div className="info-item">
          <Zap size={16} />
          <span>{charging_stations?.length || 0} Charging Stations</span>
        </div>
        <div className="info-item">
          <ShoppingCart size={16} />
          <span>{pickup_zones?.length || 0} Pickup Zones</span>
        </div>
        <div className="info-item">
          <Package size={16} />
          <span>{delivery_zones?.length || 0} Delivery Zones</span>
        </div>
        <div className="info-item">
          <XCircle size={16} />
          <span>{obstacles?.length || 0} Obstacles</span>
        </div>
      </div>

      {/* Grid */}
      <div
        className="environment-grid"
        style={{
          gridTemplateColumns: `repeat(${width}, 1fr)`,
          gridTemplateRows: `repeat(${height}, 1fr)`
        }}
      >
        {/* Render grid cells */}
        {renderGrid()}
        
        {/* Render robots with paths */}
        {renderRobots()}
      </div>
    </div>
  );
};

export default EnvironmentGrid;
