# PowerShell setup script for Project B
$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

Write-Host "Setting up Project B environment..." -ForegroundColor Cyan

# Create virtual environment
python -m venv .venv

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Error "Failed to create virtual environment"
    exit 1
}

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install --no-cache-dir -r requirements_optimized.txt

Write-Host "Project B environment setup complete!" -ForegroundColor Green
