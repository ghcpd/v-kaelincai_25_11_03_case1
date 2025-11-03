# Evaluation of Scheduling Feature Implementations

This workspace evaluates how two AI-driven implementations deliver a new scheduling
feature for an existing task management system. The feature computes earliest start
and finish times for tasks with explicit dependencies, handles malformed inputs, and
captures runtime metrics for regression analysis.

## 📌 Scenario
- **Feature tested:** Dependency-aware task scheduling with critical path insight.
- **Input format (JSON/Python dict):**
  ```json
  {
    "tasks": [
      {"id": "design", "duration": 2, "depends_on": []},
      {"id": "build", "duration": 3, "depends_on": ["design"]}
    ]
  }
  ```
- **Output format:**
  ```json
  {
    "schedule": {
      "design": {"start": 0.0, "finish": 2.0},
      "build": {"start": 2.0, "finish": 5.0}
    },
    "total_duration": 5.0
  }
  ```
  Project B additionally reports a non-negative `slack` metric for each task.

## 🗂️ Directory Structure
```
ProjectA_PreOptimization/   # Baseline implementation
ProjectB_PostOptimization/  # Optimised implementation
report_tools/               # Utilities for comparison reporting
compare_report.md           # Auto-generated comparison (after running the suites)
run_all.sh                  # Master script to run both projects and rebuild the report
```

### Project A — Pre-Optimisation
- `src/original_code.py`: Naïve iterative scheduler (O(n²) scanning)
- `tests/test_original.py`: Harness evaluating 6 structured cases
- `data/input_data.json`: Normal, edge, and malformed payloads with expected outputs
- `requirements.txt`: Minimal dependencies (`pytest` for parity)
- `setup.sh`: Creates `.venv` and installs dependencies
- `run_tests.sh`: Runs setup, executes tests, and records logs/metrics/performance

### Project B — Post-Optimisation
- `src/optimized_code.py`: Linear-time scheduler using Kahn's algorithm + slack
- `tests/test_optimized.py`: Same dataset plus slack validation & runtime capture
- `data/test_data.json`: Identical to Project A for apples-to-apples comparison
- `requirements_optimized.txt`, `setup_optimized.sh`, `run_tests.sh`: Environment and execution tooling

## 🧪 Test Coverage
Each project exercises at least five structured cases:
1. **Normal flow** — Linear dependency chain
2. **Branching dependencies** — Fan-in/fan-out scenarios
3. **Large durations** — Stress timing accumulation
4. **Missing dependency** — Referencing an unknown task id
5. **Cycle detection** — Ensures cycles are rejected
6. **Malformed input** — Non-dict payload handling

The harness computes:
- Total tests executed vs. passed
- Accuracy across all categories
- Edge/invalid-case success rate
- Per-case latency
- Aggregate runtime (seconds)

## ⚙️ Environment Setup
Use Bash (macOS/Linux/Git Bash/WSL on Windows).

### Project A
```bash
cd ProjectA_PreOptimization
./setup.sh           # creates .venv + installs requirements
./run_tests.sh       # runs harness, writes logs & performance metrics
```

### Project B
```bash
cd ProjectB_PostOptimization
./setup_optimized.sh
./run_tests.sh
```

## 🚀 One-Click Execution
From repository root:
```bash
./run_all.sh
```
This will:
1. Run both project test suites.
2. Capture logs under each project's `logs/` directory.
3. Save runtime stats under `performance/`.
4. (Re)generate `compare_report.md` summarising metrics and improvements.

## 📈 Output Artifacts
- `logs/log_*.txt`: Human-readable per-case logs with pass/fail + timing
- `logs/metrics_*.json`: Machine-readable metrics for automation
- `performance/time_*.txt`: Aggregate runtime in seconds
- `compare_report.md`: Markdown comparison generated from metrics

## ⚠️ Notes & Limitations
- Scripts assume Python 3.10+ is available on PATH.
- `.sh` scripts target Bash; adapt for PowerShell if Bash isn’t available.
- The optimised implementation reports per-task slack; Project A ignores it, but
  their shared tests validate start/finish parity for fair comparison.

## 📚 Further Work
- Extend datasets with thousands of tasks to stress-test runtime scaling.
- Plot schedule Gantt charts from metric files for visual regression tracking.
- Integrate with CI to archive logs and report deltas automatically.

Happy scheduling!
