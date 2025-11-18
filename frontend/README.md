# Fleet Dashboard - Frontend

A modern React dashboard for visualizing the Warehouse Fleet Simulator in real-time.

## 🎨 Features

- **Real-time 2D Grid Visualization** - 20×20 grid showing robot positions
- **Smooth Animations** - Framer Motion for fluid robot movement
- **Color-Coded Status** - Visual indicators for different robot states:
  - 🟢 **Moving** - Green
  - 🔵 **Idle** - Blue
  - 🟡 **Charging** - Yellow/Orange
  - 🟣 **Delivering** - Purple
  - 🔵 **Returning** - Cyan
  - 🔴 **Error** - Red
- **Robot Details Sidebar** - Complete info for each robot (ID, status, battery, position)
- **Fleet Summary** - Average battery and status distribution
- **Start/Pause Controls** - Toggle live updates
- **Reset Fleet** - Reset all robots via API
- **Configurable** - Adjust grid size and update interval
- **Responsive Design** - Works on desktop and mobile

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

### Installation

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

### Running the App

```powershell
# Start development server
npm run dev
```

The app will open at **http://localhost:3000**

### Building for Production

```powershell
# Create optimized production build
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── FleetGrid.jsx        # 2D grid with robot visualization
│   │   ├── FleetGrid.css
│   │   ├── RobotSidebar.jsx     # Robot details & fleet summary
│   │   ├── RobotSidebar.css
│   │   ├── ControlPanel.jsx     # Configuration controls
│   │   └── ControlPanel.css
│   ├── App.jsx                  # Main application component
│   ├── App.css
│   ├── main.jsx                 # App entry point
│   └── index.css                # Global styles
├── index.html
├── vite.config.js               # Vite configuration
├── package.json
└── README.md
```

## 🎮 How to Use

### Main Dashboard

1. **Grid View** - See all robots moving in real-time on the grid
2. **Hover over robots** - View status badge and battery indicator
3. **Sidebar** - Monitor detailed stats for each robot

### Controls

- **Pause/Resume** - Stop/start fetching updates from backend
- **Reset Fleet** - Reset all robots to initial positions and full battery
- **Configuration** - Click settings button at bottom to adjust:
  - Grid size (10-30)
  - Update interval (0.5-10 seconds)

### Status Colors

The robots are color-coded by their current status:
- **Green** - Moving
- **Blue** - Idle
- **Yellow** - Charging
- **Purple** - Delivering
- **Cyan** - Returning
- **Red** - Error

## 🔧 Configuration

### API Endpoint

The frontend connects to the backend at `http://localhost:8000` by default. This is configured in `vite.config.js`:

```javascript
proxy: {
  '/robots': 'http://localhost:8000',
  '/fleet': 'http://localhost:8000',
  '/reset': 'http://localhost:8000',
}
```

To change the backend URL, edit the `API_BASE_URL` constant in `src/App.jsx`.

### Update Interval

Default: 2 seconds (2000ms)
Can be adjusted via the configuration panel: 0.5-10 seconds

### Grid Size

Default: 20×20 (matches backend)
Can be adjusted via the configuration panel: 10-30

**Note:** Backend simulates on 20×20 grid. Changing grid size only affects frontend visualization.

## 📦 Dependencies

### Main Dependencies
- **React 18.3** - UI framework
- **Framer Motion 11.0** - Smooth animations
- **Lucide React** - Icons

### Dev Dependencies
- **Vite 5.4** - Build tool and dev server
- **ESLint** - Code linting

## 🎨 Features Breakdown

### FleetGrid Component
- Renders 20×20 grid with cells
- Animates robot movements using Framer Motion
- Shows battery indicators on hover
- Displays status badges
- Includes color-coded legend

### RobotSidebar Component
- Fleet summary with average battery
- Status distribution chart
- Scrollable list of all robots
- Individual robot cards with:
  - ID and status
  - Position (x, y)
  - Battery percentage with visual bar

### ControlPanel Component
- Collapsible settings panel
- Grid size slider
- Update interval slider
- Info about configuration

## 🌐 API Integration

The frontend makes requests to these backend endpoints:

- `GET /robots` - Fetch all robot states (polled every 2s)
- `GET /fleet/summary` - Fetch fleet statistics
- `POST /reset` - Reset all robots

## 🎯 Technical Highlights

- **Smooth Transitions** - Spring animations for robot movement
- **Real-time Updates** - Automatic polling with pause/resume
- **Responsive Grid** - Scales to fit available space
- **Dark Theme** - Modern dark UI with gradient backgrounds
- **Performance** - Optimized rendering with React hooks
- **Type Safety** - Proper prop validation
- **Modular Code** - Reusable components

## 🐛 Troubleshooting

### Can't connect to backend
- Make sure backend is running: `python app.py`
- Check backend URL in `src/App.jsx`
- Verify CORS is enabled in backend

### Robots not updating
- Click "Resume" if simulation is paused
- Check browser console for errors
- Verify backend is responding at `http://localhost:8000/robots`

### Grid looks wrong
- Adjust grid size in configuration panel
- Ensure window is wide enough
- Try refreshing the page

## 📄 License

This project is open-source and available for educational and commercial use.

---

**Built with React + Vite** ⚛️⚡

