# Fleet Simulator Startup Script
# This script starts both backend and frontend servers

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Warehouse Fleet Simulator - Starting Services" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "app.py")) {
    Write-Host "❌ Error: Please run this script from the Fleet_management directory" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "🚀 Starting Backend (Python FastAPI)..." -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Gray
Write-Host ""

Start-Process powershell -ArgumentList "-NoExit", "-Command", "python app.py"
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "🚀 Starting Frontend (React + Vite)..." -ForegroundColor Green
Write-Host "   URL: http://localhost:3000" -ForegroundColor Gray
Write-Host ""

if (!(Test-Path "frontend\node_modules")) {
    Write-Host "📦 Installing frontend dependencies first..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  ✅ Both servers are starting!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "📍 Frontend:     http://localhost:3000" -ForegroundColor White
Write-Host "📚 API Docs:     http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop the servers" -ForegroundColor Gray
Write-Host ""
