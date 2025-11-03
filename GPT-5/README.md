# New Feature Evaluation: JSON Diff Summarizer

## Overview
This workspace evaluates a *New Feature* implementation: a JSON diff summarizer that produces structured change metadata between two JSON-like inputs. Two projects demonstrate pre-optimization (Project A: naive) and post-optimization (Project B: improved) states.

## Feature Definition
Inputs: Python objects (dict, list, primitives) or JSON strings.
Output (Python dict / JSON serializable):
```
{
  "changes": {
    "added": {"path": value},
    "removed": {"path": value},
    "modified": {"path": {"old": old, "new": new}},
    "type_changed": {"path": {"old_type": str, "new_type": str, "old_value": repr, "new_value": repr}}
  },
  "stats": {
    "total_paths_compared": int,
    "num_added": int,
    "num_removed": int,
    "num_modified": int,
    "num_type_changed": int
  },
  "errors": ["..."]
}
```

## Projects
### Project A (Naive)
- Recursive diff
- Limited error handling (malformed JSON can raise)
- Type changes misclassified as modifications
- Higher memory/time overhead

### Project B (Optimized)
- Iterative traversal
- Robust malformed JSON handling
- Accurate type change detection
- Efficient path construction
- Lower memory/time usage

## Test Cases
Located in `ProjectA/data/input_data.json` and `ProjectB/data/test_data.json`:
1. TC1: Simple flat diff (normal)
2. TC2: Nested structures with list changes (normal)
3. TC3: Large generated stress case (edge)
4. TC4: Malformed JSON string (invalid)
5. TC5: Root type change int->list (edge)
6. TC6: Nested type change int->list (edge)

Project B expected counts include `num_type_changed` where appropriate; Project A does not.

## Metrics Collected
- Accuracy (passed / total)
- Edge case success rate
- Suite execution time (ms)
- Peak memory bytes (tracemalloc)
- Per-case timing

## Running (Bash)
```bash
bash run_all.sh
```

## Running (PowerShell on Windows)
Requires Git Bash for `.sh` scripts or use PowerShell script:
```powershell
./run_all.ps1
```

## Individual Project Execution
```bash
bash ProjectA/run_tests.sh
bash ProjectB/run_tests.sh
python generate_comparison.py
```

## Generated Artifacts
- `ProjectA/logs/log_original.txt` / `ProjectB/logs/log_optimized.txt`
- `ProjectA/performance/summary.json` / `ProjectB/performance/summary.json`
- `compare_report.md` (after running comparison)

## Edge Case Handling Notes
- Malformed JSON strings: Project B records an error and preserves original string; Project A may misclassify modification.
- Type changes: Project B isolates in `type_changed`; Project A lumps into `modified`.
- Large structures: Project B avoids recursion depth limits.

## Limitations
- Requirements are minimal (only `psutil`); deeper profiling (CPU, memory graphs) omitted for simplicity.
- No concurrency tests; single-thread performance only.
- Coverage metric is functional pass rate, not line coverage.

## Extending
Potential next steps:
- Add diff compression for repeated patterns.
- Add ignore/include path filtering.
- Integrate JSON schema validation pre-diff.
- Add line coverage via `coverage.py`.

## One-Click Outcome
After `run_all.sh` or `run_all.ps1`, review:
- `compare_report.md` for quantitative improvements.
- Performance JSONs for raw metrics.

## Security & Robustness Considerations
- Malformed JSON handled gracefully (Project B).
- No external I/O besides provided data files.
- Safe representation limiting large value repr length.

---
Generated automatically as part of AI model feature evaluation.
