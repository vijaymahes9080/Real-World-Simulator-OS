# Windows Launch Script for Real-World Simulator OS
# Run this from the root of the workspace directory.

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Starting Real-World Simulator OS Service Suite" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# Check if environment setup exists
if (-not (Test-Path "backend/venv")) {
    Write-Warning "Environment not found. Running setup first..."
    & powershell scripts/setup_windows.ps1
}

# 1. Start FastAPI Backend
Write-Host "`nLaunching Python FastAPI backend (Port 8000)..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "backend/venv/Scripts/python.exe" -ArgumentList "-m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload" -WorkingDirectory "backend"

# 2. Start Vite Frontend Client
Write-Host "Launching React Vite UI client (Port 3000)..." -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "npm.cmd" -ArgumentList "run dev" -WorkingDirectory "frontend"

Write-Host "`nBoth processes launched!" -ForegroundColor Green
Write-Host "----------------------------------------------" -ForegroundColor Cyan
Write-Host "Access Console: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Backend Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "----------------------------------------------" -ForegroundColor Cyan
Write-Host "Press Ctrl+C in this terminal window to stop." -ForegroundColor Gray

# Keep running to prevent immediate script exit
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
}
finally {
    Write-Host "`nStopping server processes..." -ForegroundColor Yellow
    # Clean up uvicorn and node processes spawned in background
    Get-Process | Where-Object { $_.ProcessName -eq "python" -and $_.Path -like "*backend/venv*" } | Stop-Process -Force
    Get-Process | Where-Object { $_.ProcessName -eq "node" } | Stop-Process -Force
}
