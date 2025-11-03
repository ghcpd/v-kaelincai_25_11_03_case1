# 📊 Comparative Report: Project A vs. Project B

## 🔍 Scenario
The assessment targets the **Smart Permission Aggregation** feature: calculating the effective allow/deny decisions for enterprise support engineers across direct grants, group memberships, role templates, and environment constraints. Five shared test cases cover normal, conflict, stress, and malformed payload situations.

## ✅ Correctness Summary
| Metric | Project A (Pre-Optimization) | Project B (Post-Optimization) |
| --- | --- | --- |
| Total automated cases | 5 | 5 |
| Functional accuracy | 100% | 100% |
| Invalid-case handling success | 100% | 100% |
| Edge coverage (stress/invalid cases) | 60% of suite | 60% of suite |
| Metadata richness | Basic coverage counts | Adds source counts, edge rate & timings |

## 🚀 Performance Comparison
| Scenario | Project A duration (s) | Project B duration (s) | Improvement |
| --- | --- | --- | --- |
| Mean per-case runtime | 0.000356 (derived) | 0.000217 | **1.6× faster** |
| Stress case runtime | 0.001629 | 0.000851 | **1.9× faster** |
| Stress throughput (25 eval burst) | — | 1408 ops/sec | New capability |
| Total suite runtime | 0.7654 | 0.7709 | Similar (dominated by setup) |

**Source:** Aggregated automatically by `run_all.py` via the contents of `ProjectA/logs/log_original.txt`, `ProjectA/performance/time_original.txt`, `ProjectB/logs/log_optimized.txt`, and `ProjectB/performance/time_optimized.txt`.

## 🧠 Key Optimizations
1. **Set-based aggregation:** Project B replaces repeated list scans with normalized `GrantSection` sets, eliminating quadratic behaviour on replicated groups.
2. **Template caching:** Role descriptors are serialized and cached, avoiding redundant parsing for identical templates.
3. **Constraint folding:** Suspended actions are pre-normalized once, producing consistent provenance (`constraint`) while skipping no-op sections.
4. **Enhanced analytics:** Project B records evaluation time, per-source counts, edge-case success rate, and throughput—extending observability for downstream analytics.

## ⚠️ Observed Limitations
- Both projects rely on deterministic test data; stochastic permission sources require additional fuzzing.
- Project A lacks throughput verification and omits latency metadata.
- Project B’s throughput benchmark runs in-process; distributed environments should remeasure under production loads.
- Neither project persists cache entries across processes—clustered deployments would need shared stores.

## 📁 Generated Artifacts
| Artifact | Project A | Project B | Purpose |
| --- | --- | --- | --- |
| Source implementation | `ProjectA/src/original_code.py` | `ProjectB/src/optimized_code.py` | Baseline vs. optimized evaluator |
| Automated tests | `ProjectA/tests/test_original.py` | `ProjectB/tests/test_optimized.py` | Validates functionality, edge handling, performance metrics |
| Data | `ProjectA/data/input_data.json` | `ProjectB/data/test_data.json` | Shared structured cases with expected outputs |
| Logs | `ProjectA/logs/log_original.txt` | `ProjectB/logs/log_optimized.txt` | Aggregated accuracy and duration stats |
| Performance traces | `ProjectA/performance/time_original.txt` | `ProjectB/performance/time_optimized.txt` | Raw timing samples |

## 🏁 Conclusion
Project B retains perfect correctness while delivering markedly faster stress-case execution, richer diagnostics, and higher observable throughput. The automation pipeline (`run_all.py` / `run_all.sh`) reproducibly validates both codebases and captures the quantitative evidence needed for go/no-go decisions on the new feature roll-out.
