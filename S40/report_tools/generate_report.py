"""Generate a comparison report between Project A and Project B runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_perf(path: Path) -> float:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return float(handle.read().strip() or "0")
    except FileNotFoundError:
        return 0.0


def _render_table(metric: str, a_value: float, b_value: float, improvement: float) -> str:
    return f"| {metric} | {a_value:.6f} | {b_value:.6f} | {improvement:+.6f} |\n"


def generate_report(
    project_a_metrics: Path,
    project_b_metrics: Path,
    project_a_perf: Path,
    project_b_perf: Path,
    output: Path,
) -> None:
    metrics_a = _load_json(project_a_metrics)
    metrics_b = _load_json(project_b_metrics)

    runtime_a = _load_perf(project_a_perf) or float(metrics_a.get("total_runtime_sec", 0.0))
    runtime_b = _load_perf(project_b_perf) or float(metrics_b.get("total_runtime_sec", 0.0))

    accuracy_a = float(metrics_a.get("accuracy", 0.0))
    accuracy_b = float(metrics_b.get("accuracy", 0.0))
    edge_rate_a = float(metrics_a.get("edge_case_success_rate", 0.0))
    edge_rate_b = float(metrics_b.get("edge_case_success_rate", 0.0))

    improvement_runtime = runtime_a - runtime_b
    improvement_accuracy = accuracy_b - accuracy_a
    improvement_edge = edge_rate_b - edge_rate_a

    header = (
        "# Feature Evaluation Comparison\n\n"
        "This report is generated automatically by `run_all.sh` and captures the latest \n"
        "results after executing the validation suites for both projects.\n\n"
    )

    table_header = "| Metric | Project A | Project B | Difference (B - A) |\n|---|---|---|---|\n"
    table_rows = (
        _render_table("Accuracy", accuracy_a, accuracy_b, improvement_accuracy)
        + _render_table("Edge Case Success", edge_rate_a, edge_rate_b, improvement_edge)
        + _render_table("Total Runtime (s)", runtime_a, runtime_b, runtime_b - runtime_a)
    )

    case_summary = "\n## Detailed Case Outcomes\n\n"

    def _format_cases(label: str, metrics: Dict[str, Any]) -> str:
        lines = [f"### {label}\n"]
        for case in metrics.get("cases", []):
            state = "✅" if case.get("passed") else "❌"
            elapsed_ms = float(case.get("elapsed_sec", 0.0)) * 1000.0
            reason = case.get("failure_reason")
            reason_text = f" — {reason}" if reason else ""
            lines.append(f"- {state} **{case.get('name','case')}** ({case.get('category')}) — {elapsed_ms:.2f} ms{reason_text}")
        lines.append("\n")
        return "\n".join(lines)

    case_summary += _format_cases("Project A", metrics_a)
    case_summary += _format_cases("Project B", metrics_b)

    notes = (
        "## Notes\n\n"
        "- **Accuracy** reflects the fraction of all cases that passed.\n"
        "- **Edge Case Success** covers both `edge` and `invalid` scenarios.\n"
        "- **Total Runtime** includes the entire suite duration (lower is better).\n"
        "- Any ❌ entries above highlight scenarios that require additional investigation.\n"
    )

    content = header + table_header + table_rows + case_summary + notes
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate comparison markdown report.")
    parser.add_argument("--project-a-metrics", required=True, type=Path)
    parser.add_argument("--project-b-metrics", required=True, type=Path)
    parser.add_argument("--project-a-perf", required=True, type=Path)
    parser.add_argument("--project-b-perf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    generate_report(
        project_a_metrics=args.project_a_metrics,
        project_b_metrics=args.project_b_metrics,
        project_a_perf=args.project_a_perf,
        project_b_perf=args.project_b_perf,
        output=args.output,
    )


if __name__ == "__main__":
    main()
