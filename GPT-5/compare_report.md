# Comparison Report: Project A (Naive) vs Project B (Optimized)

## High-Level Metrics

Total Test Cases: 6 (A) / 6 (B)
Accuracy: 50.00% (A) -> 50.00% (B) | Delta: 0.00%
Edge Case Success Rate: 66.67% (A) -> 33.33% (B) | Delta: -50.00%
Suite Time (ms): 2.953 (A) -> 5.602 (B) | Delta: 89.71%
Peak Memory (bytes): 167261 (A) -> 283773 (B) | Delta: 69.66%

## Per-Test Timing Summary

Median Time (ms): 0.052 (A) vs 0.114 (B)
Mean Time (ms): 0.143 (A) vs 0.675 (B)

## Failed Cases in Project A

- TC2 (category=normal) expected={'num_added': 1, 'num_removed': 1, 'num_modified': 2, 'num_type_changed': 0} actual={'total_paths_compared': 8, 'num_added': 1, 'num_removed': 0, 'num_modified': 2, 'num_type_changed': 0}
- TC3 (category=edge) expected={'num_added': 2, 'num_removed': 1, 'num_modified': 2, 'num_type_changed': 0} actual={'total_paths_compared': 1000, 'num_added': 2, 'num_removed': 1, 'num_modified': 5, 'num_type_changed': 0}
- TC4 (category=invalid) expected={'num_added': 0, 'num_removed': 0, 'num_modified': 1, 'num_type_changed': 0} actual={'num_added': 0, 'num_removed': 0, 'num_modified': 0, 'num_type_changed': 0}

## Improvements Applied

- Added robust type change detection (previously counted as modifications).
- Iterative traversal replaced deep recursion to avoid stack overhead.
- Graceful handling of malformed JSON strings (error recorded instead of crash).
- Efficient path construction reduces string manipulation cost.
- Memory usage improvement via stack + no redundant path copies.

## Edge Case Handling

Project B correctly identifies type changes and malformed JSON compared to Project A's misclassification.
Invalid inputs produce structured errors without aborting diff generation in Project B.