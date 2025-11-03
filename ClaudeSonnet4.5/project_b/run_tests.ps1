# PowerShell test runner for Project B
$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectDir

Write-Host "Running Project B tests..." -ForegroundColor Cyan

# Run setup first
& .\setup_optimized.ps1

# Activate virtual environment
if (Test-Path ".venv\Scripts\Activate.ps1") {
    & ".venv\Scripts\Activate.ps1"
} else {
    Write-Error "Virtual environment not found. Run setup_optimized.ps1 first."
    exit 1
}

# Create output directories
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "performance" | Out-Null

# Clear previous logs
"" | Out-File -FilePath "logs\log_optimized.txt" -Encoding utf8
"" | Out-File -FilePath "performance\time_optimized.txt" -Encoding utf8

# Set PYTHONPATH and run tests
$env:PYTHONPATH = "$ProjectDir\src"
pytest --disable-warnings --maxfail=1 -q | Tee-Object -FilePath "logs\log_optimized.txt"

# Run performance profiling
python -m src.profile_runner | Tee-Object -Append -FilePath "performance\time_optimized.txt"

Write-Host "Project B tests complete!" -ForegroundColor Green
