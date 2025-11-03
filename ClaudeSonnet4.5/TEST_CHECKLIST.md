# TEST EXECUTION CHECKLIST

Use this checklist to verify successful test execution and result validation.

## Pre-Execution Checklist

- [ ] Python 3.10+ installed and accessible via `python --version`
- [ ] PowerShell 5.1+ (Windows) or Bash shell (Unix/Git Bash) available
- [ ] Current directory is `c:\chatWorkspace` (or your workspace root)
- [ ] All project files present (verify with `Get-ChildItem -Recurse -Filter "*.py"`)

## Execution Steps

### Step 1: Run Master Script
```powershell
.\run_all.ps1
```

**Expected Output**:
- "Setting up Project A environment..." → "Project A environment setup complete!"
- "Running Project A tests..." → Pytest output showing 6 passed tests
- "Setting up Project B environment..." → "Project B environment setup complete!"
- "Running Project B tests..." → Pytest output showing 6 passed tests
- "Generating Comparison Report..." → "Comparison report generated successfully!"

**Time Estimate**: First run 30-60s, subsequent runs 5-15s

### Step 2: Verify Outputs

#### Check Test Results
- [ ] `project_a/logs/log_original.txt` exists and shows "6 passed"
- [ ] `project_b/logs/log_optimized.txt` exists and shows "6 passed"

#### Check Metrics Files
- [ ] `project_a/logs/metrics_original.json` exists
  - [ ] `"total_cases": 6`
  - [ ] `"success_cases": 4`
  - [ ] `"error_cases": 2`
  - [ ] `"accuracy": 1.0` (or close to 1.0)

- [ ] `project_b/logs/metrics_optimized.json` exists
  - [ ] `"total_cases": 6`
  - [ ] `"success_cases": 4`
  - [ ] `"error_cases": 2`
  - [ ] `"accuracy": 1.0` (or close to 1.0)
  - [ ] Contains `"average_visited_nodes"` field

#### Check Performance Files
- [ ] `project_a/performance/time_original.txt` exists
  - [ ] Contains `executions=5`
  - [ ] Contains `avg_runtime_ms=...`
  - [ ] Contains `synthetic_cost=...`

- [ ] `project_b/performance/time_optimized.txt` exists
  - [ ] Contains `executions=10`
  - [ ] Contains `avg_runtime_ms=...`
  - [ ] Contains `stress_cost=...`

#### Check Comparison Report
- [ ] `compare_report.md` exists
- [ ] Contains comparison table with metrics for both projects
- [ ] Shows accuracy percentages
- [ ] Shows runtime improvements (or notes if no improvement)

### Step 3: Validate Test Case Results

Open `project_a/logs/metrics_original.json` and verify individual test cases:

- [ ] **simple_direct**: `"status": "success"`, path should be `["A", "B", "E"]`, cost `7.0`
- [ ] **blocked_primary_node**: `"status": "success"`, path `["A", "C", "D", "E"]`, cost `4.2`
- [ ] **blocked_edge_requires_detour**: `"status": "success"`, path `["S", "T", "V", "W"]`, cost `2.0`
- [ ] **degenerate_same_node**: `"status": "success"`, path `["X"]`, cost `0.0`
- [ ] **unreachable_target**: `"status": "error_expected"`, error contains "RouteComputationError"
- [ ] **invalid_missing_nodes**: `"status": "error_expected"`, error contains "RouteValidationError"

Repeat verification for `project_b/logs/metrics_optimized.json` - results should match!

### Step 4: Performance Comparison

Open `compare_report.md` and verify:

- [ ] Accuracy is 100% (or 66.67% if counting expected errors differently) for both projects
- [ ] Edge-case success rate is 100% for both projects
- [ ] Project B shows equal or better runtime than Project A
- [ ] No unexpected errors in either project

### Step 5: Algorithm Verification

Check algorithm metadata in metrics files:

**Project A (`metrics_original.json`)**:
- [ ] Successful cases contain `"metadata": {"algorithm": "dijkstra_table", ...}`

**Project B (`metrics_optimized.json`)**:
- [ ] Successful cases contain `"metadata": {"algorithm": "dijkstra_heap", ...}`
- [ ] Metadata includes `"relaxations"` count

## Common Issues and Resolutions

### Issue: Test failures
**Resolution**: 
1. Check error message in logs
2. Verify test data JSON files are valid
3. Re-run individual tests: `cd project_a; pytest -v`

### Issue: Import errors
**Resolution**:
1. Ensure virtual environment was activated
2. Re-run setup: `cd project_a; .\setup.ps1`
3. Verify `PYTHONPATH` includes `src` directory

### Issue: Performance metrics missing
**Resolution**:
1. Check if `profile_runner.py` executed without errors
2. Manually run: `cd project_a; python -m src.profile_runner`

### Issue: Comparison report empty or incorrect
**Resolution**:
1. Ensure both projects ran successfully first
2. Manually regenerate: `python generate_compare_report.py`
3. Check for metrics JSON files in project_*/logs/

## Success Criteria Summary

✅ **Minimum Success**: 
- 6/6 tests passing in both projects
- All expected errors raised correctly
- Comparison report generated

✅ **Full Success**:
- All of the above
- Performance metrics showing Project B ≤ Project A runtime
- No syntax/import errors
- All metadata fields populated correctly

✅ **Optimal Success**:
- All of the above
- Project B shows measurable performance improvement (>10% faster)
- Edge-case success rate = 100%
- Stress test cases execute without timeout

## Final Verification Command

```powershell
# Quick check for all expected output files
$files = @(
    "compare_report.md",
    "project_a\logs\metrics_original.json",
    "project_a\logs\log_original.txt",
    "project_a\performance\time_original.txt",
    "project_b\logs\metrics_optimized.json",
    "project_b\logs\log_optimized.txt",
    "project_b\performance\time_optimized.txt"
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✓ $file" -ForegroundColor Green
    } else {
        Write-Host "✗ $file MISSING" -ForegroundColor Red
    }
}
```

If all files show ✓, the test execution was successful!

---

**Last Updated**: November 3, 2025
