import { useState } from 'react';
import { Settings, ChevronDown, ChevronUp } from 'lucide-react';
import './ControlPanel.css';

function ControlPanel({ gridSize, setGridSize, updateInterval, setUpdateInterval }) {
  const [isOpen, setIsOpen] = useState(false);

  const handleGridSizeChange = (e) => {
    const newSize = parseInt(e.target.value, 10);
    if (newSize >= 10 && newSize <= 30) {
      setGridSize(newSize);
    }
  };

  const handleIntervalChange = (e) => {
    const newInterval = parseInt(e.target.value, 10);
    if (newInterval >= 500 && newInterval <= 10000) {
      setUpdateInterval(newInterval);
    }
  };

  return (
    <div className={`control-panel ${isOpen ? 'open' : ''}`}>
      <button 
        className="control-panel-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        <Settings size={20} />
        <span>Configuration</span>
        {isOpen ? <ChevronDown size={20} /> : <ChevronUp size={20} />}
      </button>

      {isOpen && (
        <div className="control-panel-content">
          <div className="control-group">
            <label className="control-label">
              Grid Size: {gridSize}×{gridSize}
            </label>
            <input
              type="range"
              min="10"
              max="30"
              value={gridSize}
              onChange={handleGridSizeChange}
              className="control-slider"
            />
            <div className="control-hint">
              Adjust grid dimensions (10-30)
            </div>
          </div>

          <div className="control-group">
            <label className="control-label">
              Update Interval: {updateInterval / 1000}s
            </label>
            <input
              type="range"
              min="500"
              max="10000"
              step="500"
              value={updateInterval}
              onChange={handleIntervalChange}
              className="control-slider"
            />
            <div className="control-hint">
              How often to fetch robot data (0.5-10s)
            </div>
          </div>

          <div className="control-info">
            <p>
              <strong>Note:</strong> Backend simulates 5 robots on a 20×20 grid by default. 
              Grid size changes here only affect visualization.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default ControlPanel;
