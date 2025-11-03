from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent


def _load_metrics(path: Path) -> Dict[str, float | int | str]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_performance(path: Path) -> Dict[str, float]:
    results: Dict[str, float] = {}
    if not path.exists():
        return results
    pattern = re.compile(r"(?P<key>[a-zA-Z0-9_]+)=(?P<value>[0-9.]+)")
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            match = pattern.search(line.strip())
            if not match:
                continue
            key = match.group("key")
            value = float(match.group("value"))
            results[key] = value
    return results


def _format_percentage(value: float) -> str:
    return f"{value * 100:.2f}%"


def _render_markdown(project_a: Dict[str, object], project_b: Dict[str, object]) -> str:
    perf_a = project_a.get("performance", {})
    perf_b = project_b.get("performance", {})
    metrics_a = project_a.get("metrics", {})
    metrics_b = project_b.get("metrics", {})

    accuracy_a = metrics_a.get("accuracy", 0.0)
    accuracy_b = metrics_b.get("accuracy", 0.0)
    edge_a = metrics_a.get("edge_case_success_rate", 0.0)
    edge_b = metrics_b.get("edge_case_success_rate", 0.0)
    avg_case_duration_a = metrics_a.get("average_duration_ms", 0.0)
    avg_case_duration_b = metrics_b.get("average_duration_ms", 0.0)
    runtime_a = perf_a.get("avg_runtime_ms", 0.0)
    runtime_b = perf_b.get("avg_runtime_ms", 0.0)

    runtime_delta = runtime_a - runtime_b
    runtime_improvement = (runtime_delta / runtime_a) if runtime_a else 0.0

    lines = [
        "# Route Computation Feature Comparison",
        "",
        "| Metric | Project A (Initial) | Project B (Optimized) |",
        "| --- | --- | --- |",
        f"| Accuracy | {_format_percentage(accuracy_a)} | {_format_percentage(accuracy_b)} |",
        f"| Edge-case success | {_format_percentage(edge_a)} | {_format_percentage(edge_b)} |",
        f"| Avg case duration (ms) | {avg_case_duration_a:.3f} | {avg_case_duration_b:.3f} |",
        f"| Batch avg runtime (ms) | {runtime_a:.3f} | {runtime_b:.3f} |",
        "",
        "## Key Takeaways",
    ]

    if runtime_improvement > 0:
        lines.append(
            f"- Optimized implementation reduces batch runtime by {_format_percentage(runtime_improvement)} compared to the baseline."
        )
    else:
        lines.append("- No measurable runtime improvement detected; investigate profiling data.")

    if accuracy_b >= accuracy_a:
        lines.append("- Optimized implementation preserves or improves correctness across supplied cases.")
    else:
        lines.append("- Optimized implementation regressed accuracy; review failing cases.")

    lines.extend(
        [
            "",
            "## Project A (Initial)",
            f"- Total cases: {metrics_a.get('total_cases', 'n/a')}"
            f" | Success: {metrics_a.get('success_cases', 'n/a')}"
            f" | Errors: {metrics_a.get('error_cases', 'n/a')}",
            f"- Average runtime per batch (ms): {runtime_a:.3f}",
            f"- Notes: Utilizes table-based Dijkstra without heap optimizations.",
            "",
            "## Project B (Optimized)",
            f"- Total cases: {metrics_b.get('total_cases', 'n/a')}"
            f" | Success: {metrics_b.get('success_cases', 'n/a')}"
            f" | Errors: {metrics_b.get('error_cases', 'n/a')}",
            f"- Average runtime per batch (ms): {runtime_b:.3f}",
            "- Notes: Employs heap-backed Dijkstra, aggressive validation, and stress-tested performance.",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    project_a = {
        "metrics": _load_metrics(ROOT / "project_a" / "logs" / "metrics_original.json"),
        "performance": _load_performance(ROOT / "project_a" / "performance" / "time_original.txt"),
    }
    project_b = {
        "metrics": _load_metrics(ROOT / "project_b" / "logs" / "metrics_optimized.json"),
        "performance": _load_performance(ROOT / "project_b" / "performance" / "time_optimized.txt"),
    }

    markdown = _render_markdown(project_a, project_b)
    output_path = ROOT / "compare_report.md"
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write(markdown)
    
    print(f"Comparison report generated at: {output_path}")


if __name__ == "__main__":
    main()
