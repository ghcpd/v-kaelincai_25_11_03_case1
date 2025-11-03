# Feature Evaluation Comparison

This report is generated automatically by `run_all.sh` and captures the latest 
results after executing the validation suites for both projects.

| Metric | Project A | Project B | Difference (B - A) |
|---|---|---|---|
| Accuracy | 1.000000 | 1.000000 | +0.000000 |
| Edge Case Success | 1.000000 | 1.000000 | +0.000000 |
| Total Runtime (s) | 0.000370 | 0.000189 | -0.000181 |

## Detailed Case Outcomes

### Project A

- ✅ **simple_chain** (normal) — 0.19 ms
- ✅ **branching_dependencies** (normal) — 0.05 ms
- ✅ **padded_durations** (edge) — 0.03 ms
- ✅ **missing_dependency** (invalid) — 0.02 ms
- ✅ **cyclic_dependency** (invalid) — 0.01 ms
- ✅ **malformed_payload** (invalid) — 0.00 ms

### Project B

- ✅ **simple_chain** (normal) — 0.09 ms
- ✅ **branching_dependencies** (normal) — 0.04 ms
- ✅ **padded_durations** (edge) — 0.03 ms
- ✅ **missing_dependency** (invalid) — 0.01 ms
- ✅ **cyclic_dependency** (invalid) — 0.01 ms
- ✅ **malformed_payload** (invalid) — 0.02 ms

## Notes

- **Accuracy** reflects the fraction of all cases that passed.
- **Edge Case Success** covers both `edge` and `invalid` scenarios.
- **Total Runtime** includes the entire suite duration (lower is better).
- Any ❌ entries above highlight scenarios that require additional investigation.
