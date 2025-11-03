Param()
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $root
Write-Host 'Running ProjectA tests'
if (!(Test-Path "$root/ProjectA/.venv")) { bash ProjectA/setup.sh }
bash ProjectA/run_tests.sh
Write-Host 'Running ProjectB tests'
if (!(Test-Path "$root/ProjectB/.venv")) { bash ProjectB/setup_optimized.sh }
bash ProjectB/run_tests.sh
python generate_comparison.py
Write-Host 'All test suites executed. See compare_report.md'
Pop-Location