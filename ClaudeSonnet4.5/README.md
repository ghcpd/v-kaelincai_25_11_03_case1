# Evaluation of GPT-5-Codex, GPT-5, Claude Sonnet 4.5, S100, and S40 on Feature & Improvement (New Feature)

This workspace captures two implementations of a new feature that computes constrained fastest routes across directed graphs. Project A contains the initial table-based Dijkstra implementation, whereas Project B introduces an optimized heap-backed solution. Both projects share the same functional contract and test corpus so their behaviour can be compared directly.

## Scenario Overview

- **Feature under test**: `compute_fastest_route(payload: dict) -> dict`
- **Inputs**: JSON/Python dictionary describing graph nodes, weighted edges, optional blocked nodes/edges, source, and target identifiers.
- **Outputs**: Dictionary containing the optimal path, overall cost, number of visited nodes, warnings, and algorithm metadata.
- **Edge coverage**: Tests include happy-path traversal, blocked node/edge detours, unreachable targets, malformed graphs, and degenerate source/target equality.

## Project Layout

```
project_a/              # Initial implementation (less optimized)
project_b/              # Optimized implementation
run_all.ps1             # PowerShell master script for Windows
run_all.sh              # Bash master script for Unix/Linux/Git Bash
generate_compare_report.py
compare_report.md
README.md
```

Each project maintains the following structure:

```
src/                    # Feature implementation and profiling helper
setup.ps1, setup.sh     # Environment setup scripts (PowerShell & Bash)
run_tests.ps1, run_tests.sh  # Test execution scripts
tests/                  # Pytest suites with metric collectors
data/                   # Shared structured test corpus
logs/                   # Execution and metric logs
performance/            # Performance measurements from profile runs
requirements*.txt       # Python dependencies
```

## Reproducible Environment

Both projects rely solely on the Python standard library plus `pytest`. The setup scripts create a dedicated virtual environment at `.venv/` and install dependencies. Platform-specific scripts are provided:
- **Windows**: Use `.ps1` PowerShell scripts
- **Unix/Linux/macOS/Git Bash**: Use `.sh` Bash scripts

## Running the Experiments

### Prerequisites
- Python 3.10 or newer must be on the PATH
- For Windows: PowerShell 5.1 or newer
- For Unix/Linux/macOS or Git Bash on Windows: Bash shell

### On Windows PowerShell

Execute the master script from the repository root:
```powershell
.\run_all.ps1
```

Or run individual project suites:
```powershell
cd project_a; .\run_tests.ps1
cd project_b; .\run_tests.ps1
```

### On Unix/Linux/macOS or Git Bash

Execute the master script from the repository root:
```bash
./run_all.sh
```

Or run individual project suites:
```bash
cd project_a && ./run_tests.sh
cd project_b && ./run_tests.sh
```

### What the Scripts Do
- Creates isolated environments for Project A and Project B.
- Runs all automated tests and records metrics.
- Profiles both implementations under synthetic load.
- Regenerates `compare_report.md` with the latest metrics and performance deltas.

## Outputs and Metrics

- `project_a/logs/metrics_original.json`: Accuracy, coverage, and per-case telemetry for the initial solution.
- `project_b/logs/metrics_optimized.json`: Corresponding metrics for the optimized solution, including average visited node counts.
- `project_a/performance/time_original.txt` and `project_b/performance/time_optimized.txt`: Batch runtime statistics collected via dedicated profile runners.
- `compare_report.md`: Markdown summary highlighting performance gains, correctness parity, and implementation notes.

## Test Coverage

The test corpus includes:
1. **Normal cases**: Valid graphs with straightforward shortest paths
2. **Edge cases**: Blocked nodes forcing alternate routes, blocked edges requiring detours, unreachable targets
3. **Invalid cases**: Missing nodes, malformed edge structures, negative weights
4. **Boundary cases**: Source equals target (trivial path), isolated graph components
5. **Stress cases**: Synthetic dense graphs with 100-200+ nodes for performance profiling

## Key Optimizations in Project B

- **Algorithm**: Heap-based priority queue (O((E + V) log V)) vs. dense table scan (O(V²))
- **Validation**: Upfront graph model construction with frozen dataclasses
- **Edge filtering**: Pre-filters blocked nodes/edges during adjacency list construction
- **Early termination**: Stops search immediately when target is visited
- **Telemetry**: Tracks relaxation count for debugging and optimization analysis

## Known Limitations

- Bash scripts require POSIX shell; on Windows, use PowerShell scripts or Git Bash/WSL
- Performance sampling runs within a single process and does not capture system-level noise; rerun the suite for averaged trends
- The synthetic stress cases emphasise algorithmic differences rather than absolute throughput on production-scale datasets

## Next Steps

- Integrate these pipelines into CI for automated regression detection
- Extend the corpus with probabilistic fuzzing to uncover corner-case regressions
- Track long-term performance by persisting profiler outputs across commits
- Add memory profiling to complement runtime measurements
