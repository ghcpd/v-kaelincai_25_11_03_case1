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
run_all.sh              # Runs both projects, then regenerates compare_report.md
generate_compare_report.py
compare_report.md
README.md
```

Each project maintains the following structure:

```
src/                    # Feature implementation and profiling helper
scripts/*.sh            # Environment setup and test execution
tests/                  # Pytest suites with metric collectors
data/                   # Shared structured test corpus
logs/                   # Execution and metric logs
performance/            # Performance measurements from profile runs
```

## Reproducible Environment

Both projects rely solely on the Python standard library plus `pytest`. The `setup.sh`/`setup_optimized.sh` scripts create a dedicated virtual environment at `.venv/` and install dependencies from the respective requirements file. The scripts are POSIX shell compatible and work with Git Bash, WSL, or any Unix-like shell available on Windows.

## Running the Experiments

1. Ensure Python 3.10 or newer is on the PATH within your shell.
2. Execute the master script from the repository root:
   ```bash
   ./run_all.sh
   ```
   - Creates isolated environments for Project A and Project B.
   - Runs all automated tests and records metrics.
   - Profiles both implementations under synthetic load.
   - Regenerates `compare_report.md` with the latest metrics and performance deltas.

You can also run individual project suites:

```bash
cd project_a && ./run_tests.sh
cd project_b && ./run_tests.sh
```

## Outputs and Metrics

- `project_a/logs/metrics_original.json`: Accuracy, coverage, and per-case telemetry for the initial solution.
- `project_b/logs/metrics_optimized.json`: Corresponding metrics for the optimized solution, including average visited node counts.
- `project_a/performance/time_original.txt` and `project_b/performance/time_optimized.txt`: Batch runtime statistics collected via dedicated profile runners.
- `compare_report.md`: Markdown summary highlighting performance gains, correctness parity, and implementation notes.

## Known Limitations

- Scripts are authored for POSIX shells; invoke them via Git Bash or WSL on Windows PowerShell hosts.
- Performance sampling runs within a single process and does not capture system-level noise; rerun the suite for averaged trends.
- The synthetic stress cases emphasise algorithmic differences rather than absolute throughput on production-scale datasets.

## Next Steps

- Integrate these pipelines into CI for automated regression detection.
- Extend the corpus with probabilistic fuzzing to uncover corner-case regressions.
- Track long-term performance by persisting profiler outputs across commits.
