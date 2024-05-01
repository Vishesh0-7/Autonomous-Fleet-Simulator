# Warehouse Fleet Simulator 🤖

A Python backend application for simulating warehouse robots on a grid using FastAPI.

## 📋 Features

- **Fleet Simulation**: Simulates 5 robots on a 20×20 grid
- **Real-time Updates**: Robots automatically update every 2 seconds
- **Robot Properties**: Each robot has:
  - `id`: Unique identifier
  - `x, y`: Position on the grid (0-19)
  - `status`: Operational status (idle, moving, charging, delivering, returning)
  - `battery`: Battery level (0-100%)
- **REST API**: Easy-to-use endpoints for fleet management
- **Modular Design**: Structured for easy extension with obstacles and pathfinding

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**:
   ```powershell
   cd c:\Users\vishe\OneDrive\Desktop\Project\Fleet_management
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Application

Start the backend server:

```powershell
python app.py
```

The server will start on `http://localhost:8000` and the simulation will begin automatically.

You should see output like:
```
🚀 Starting Warehouse Fleet Simulator...
============================================================
🚀 Warehouse Fleet Simulator is running!
============================================================
📍 API available at: http://localhost:8000
📚 API docs at: http://localhost:8000/docs
🤖 Simulating 5 robots
🔄 Update interval: 2 seconds
============================================================
```

## 📡 API Endpoints

### 1. Get All Robots
```
GET /robots
```
Returns the current state of all robots.

**Response Example**:
```json
[
  {
    "id": 1,
    "x": 15,
    "y": 8,
    "status": "moving",
    "battery": 87
  },
  {
    "id": 2,
    "x": 3,
    "y": 12,
    "status": "idle",
    "battery": 95
  }
]
```

### 2. Reset Fleet
```
POST /reset
```
Resets all robots to initial state (random positions, 100% battery).

**Response Example**:
```json
{
  "message": "Fleet reset successfully",
  "robots": [...]
}
```

### 3. Get Single Robot
```
GET /robots/{robot_id}
```
Returns the state of a specific robot.

### 4. Get Fleet Summary
```
GET /fleet/summary
```
Returns fleet statistics including average battery and status distribution.

**Response Example**:
```json
{
  "total_robots": 5,
  "average_battery": 78.4,
  "status_distribution": {
    "moving": 2,
    "idle": 1,
    "charging": 2
  },
  "grid_size": "20x20"
}
```

### 5. Root/Health Check
```
GET /
```
Returns API information and available endpoints.

## 🧪 Testing the API

### Using cURL (PowerShell)

**Get all robots**:
```powershell
curl http://localhost:8000/robots
```

**Reset fleet**:
```powershell
curl -X POST http://localhost:8000/reset
```

### Using Browser

1. Open `http://localhost:8000/docs` for interactive API documentation (Swagger UI)
2. Open `http://localhost:8000/robots` to see robot data in your browser

### Using Python

```python
import requests

# Get all robots
response = requests.get("http://localhost:8000/robots")
print(response.json())

# Reset fleet
response = requests.post("http://localhost:8000/reset")
print(response.json())
```

## 📁 Project Structure

```
Fleet_management/
├── app.py                      # Main application entry point
├── models/
│   └── robot.py               # Robot class definition
├── fleet/
│   └── fleet_manager.py       # Fleet management logic
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Configuration

You can modify simulation parameters in `app.py`:

```python
fleet_manager = FleetManager(
    num_robots=5,        # Number of robots (default: 5)
    grid_size=20,        # Grid dimensions (default: 20x20)
    update_interval=2    # Seconds between updates (default: 2)
)
```

## 🎯 How It Works

1. **Initialization**: When `app.py` starts, it creates a `FleetManager` instance with 5 robots
2. **Background Simulation**: A background thread updates robot positions, status, and battery every 2 seconds
3. **Robot Behavior**:
   - Robots move randomly on the grid (staying within bounds)
   - Status changes randomly between idle, moving, charging, delivering, and returning
   - Battery decreases during activity and increases while charging
   - Low battery (<20%) triggers automatic charging
4. **API Access**: REST endpoints provide real-time access to fleet data

## 🔮 Future Extensions

The modular structure allows for easy additions:

- **Obstacles**: Add obstacle detection in `robot.py`
- **Pathfinding**: Implement A* or Dijkstra algorithms in `fleet_manager.py`
- **Task Queue**: Add delivery tasks and task assignment logic
- **Database**: Replace in-memory storage with persistent database
- **WebSocket**: Add real-time updates for frontend clients
- **Collision Detection**: Prevent robots from occupying the same position

## 🛑 Stopping the Server

Press `CTRL+C` in the terminal to stop the server. The simulation will automatically stop and clean up.

## 📝 License

This project is open-source and available for educational and commercial use.

## 🤝 Contributing

Feel free to fork, modify, and extend this project!

---

**Built with FastAPI** ⚡ | **Python 3.8+** 🐍
