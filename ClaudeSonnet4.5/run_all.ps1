# PowerShell master script to run all tests and generate comparison report
$ErrorActionPreference = "Stop"
$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "Running All Tests and Generating Report" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Run Project A tests
Write-Host "=== Project A (Initial Implementation) ===" -ForegroundColor Cyan
Set-Location "$RootDir\project_a"
& .\run_tests.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Project A tests encountered issues, but continuing..."
}
Write-Host ""

# Run Project B tests
Write-Host "=== Project B (Optimized Implementation) ===" -ForegroundColor Cyan
Set-Location "$RootDir\project_b"
& .\run_tests.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Project B tests encountered issues, but continuing..."
}
Write-Host ""

# Generate comparison report
Write-Host "=== Generating Comparison Report ===" -ForegroundColor Cyan
Set-Location $RootDir
python generate_compare_report.py

if (Test-Path "compare_report.md") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Comparison report generated successfully!" -ForegroundColor Green
    Write-Host "Location: $RootDir\compare_report.md" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
} else {
    Write-Error "Failed to generate comparison report"
    exit 1
}
