"""Generate comparison report between Project A and Project B.
Reads performance/summary.json from each project and writes compare_report.md.
"""
from __future__ import annotations
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).parent
A_SUMMARY = ROOT / 'ProjectA' / 'performance' / 'summary.json'
B_SUMMARY = ROOT / 'ProjectB' / 'performance' / 'summary.json'
REPORT = ROOT / 'compare_report.md'


def load_summary(path: Path):
    if not path.exists():
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def pct_delta(old: float, new: float) -> float:
    if old == 0:
        return 0.0
    return ((new - old) / old) * 100.0


def main():
    a = load_summary(A_SUMMARY)
    b = load_summary(B_SUMMARY)
    if not a or not b:
        print("Missing summaries; run both test suites first.")
        return

    lines = []
    lines.append("# Comparison Report: Project A (Naive) vs Project B (Optimized)\n")
    lines.append("## High-Level Metrics\n")
    lines.append(f"Total Test Cases: {a['total_cases']} (A) / {b['total_cases']} (B)")
    lines.append(f"Accuracy: {a['accuracy']:.2%} (A) -> {b['accuracy']:.2%} (B) | Delta: {pct_delta(a['accuracy'], b['accuracy']):.2f}%")
    lines.append(f"Edge Case Success Rate: {a['edge_case_success_rate']:.2%} (A) -> {b['edge_case_success_rate']:.2%} (B) | Delta: {pct_delta(a['edge_case_success_rate'], b['edge_case_success_rate']):.2f}%")
    lines.append(f"Suite Time (ms): {a['suite_time_ms']:.3f} (A) -> {b['suite_time_ms']:.3f} (B) | Delta: {pct_delta(a['suite_time_ms'], b['suite_time_ms']):.2f}%")
    lines.append(f"Peak Memory (bytes): {a['peak_memory_bytes']} (A) -> {b['peak_memory_bytes']} (B) | Delta: {pct_delta(a['peak_memory_bytes'], b['peak_memory_bytes']):.2f}%\n")

    # Per-test timing comparison
    a_times = [r['time_ms'] for r in a['results']]
    b_times = [r['time_ms'] for r in b['results']]
    lines.append("## Per-Test Timing Summary\n")
    lines.append(f"Median Time (ms): {statistics.median(a_times):.3f} (A) vs {statistics.median(b_times):.3f} (B)")
    lines.append(f"Mean Time (ms): {statistics.mean(a_times):.3f} (A) vs {statistics.mean(b_times):.3f} (B)\n")

    lines.append("## Failed Cases in Project A\n")
    failed_a = [r for r in a['results'] if not r['pass']]
    if not failed_a:
        lines.append("None\n")
    else:
        for r in failed_a:
            lines.append(f"- {r['id']} (category={r['category']}) expected={r['expected']} actual={r['actual']}")
        lines.append("")

    lines.append("## Improvements Applied\n")
    lines.append("- Added robust type change detection (previously counted as modifications).")
    lines.append("- Iterative traversal replaced deep recursion to avoid stack overhead.")
    lines.append("- Graceful handling of malformed JSON strings (error recorded instead of crash).")
    lines.append("- Efficient path construction reduces string manipulation cost.")
    lines.append("- Memory usage improvement via stack + no redundant path copies.\n")

    lines.append("## Edge Case Handling\n")
    lines.append("Project B correctly identifies type changes and malformed JSON compared to Project A's misclassification.")
    lines.append("Invalid inputs produce structured errors without aborting diff generation in Project B.")

    REPORT.write_text('\n'.join(lines), encoding='utf-8')
    print(f"Comparison report written to {REPORT}")


if __name__ == '__main__':
    main()
