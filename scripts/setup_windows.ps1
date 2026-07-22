# Windows Setup Script for Real-World Simulator OS
# Run this from the root of the workspace directory.

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Setting up Real-World Simulator OS (No Docker)" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan

# 1. Check Requirements
$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonInstalled) {
    Write-Warning "Python 3 is required but was not found in your PATH. Please install Python and try again."
    Exit 1
}

$npmInstalled = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmInstalled) {
    Write-Warning "NodeJS (npm) is required but was not found in your PATH. Please install Node.js and try again."
    Exit 1
}

# 2. Configure Backend Virtual Environment
Write-Host "`n[1/4] Configuring Python Virtual Environment..." -ForegroundColor Green
if (-not (Test-Path "backend/venv")) {
    python -m venv backend/venv
}

# 3. Install Python Dependencies
Write-Host "`n[2/4] Installing Backend dependencies..." -ForegroundColor Green
& backend/venv/Scripts/pip install -r backend/requirements.txt

# 4. Configure Frontend Packages
Write-Host "`n[3/4] Installing Frontend npm dependencies..." -ForegroundColor Green
Push-Location frontend
npm install
Pop-Location

# 5. Success Confirmation
Write-Host "`n[4/4] Installation Complete!" -ForegroundColor Green
Write-Host "----------------------------------------------" -ForegroundColor Cyan
Write-Host "To start the application, execute:" -ForegroundColor Cyan
Write-Host "  powershell scripts/run_windows.ps1" -ForegroundColor Yellow
Write-Host "----------------------------------------------" -ForegroundColor Cyan
