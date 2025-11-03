from __future__ import annotations

import json
import statistics
import time
from pathlib import Path
from typing import Dict, List

from .optimized_code import compute_fastest_route, RouteComputationError, RouteValidationError


def _load_cases() -> List[Dict[str, object]]:
    base_path = Path(__file__).resolve().parents[1]
    data_path = base_path / "data" / "test_data.json"
    with data_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["test_cases"]


def _stress_case(nodes: int = 200, fan_out: int = 6) -> Dict[str, object]:
    node_names = [f"N{i}" for i in range(nodes)]
    edges = []
    for idx, start in enumerate(node_names):
        for offset in range(1, fan_out + 1):
            end = node_names[(idx + offset) % nodes]
            weight = 1.0 + ((idx + offset) % 11)
            edges.append({"from": start, "to": end, "weight": weight})
    return {
        "input": {
            "nodes": node_names,
            "edges": edges,
            "source": node_names[0],
            "target": node_names[nodes // 2],
            "blocked_nodes": node_names[::51],
            "blocked_edges": [],
        },
        "expect_error": False,
        "name": "stress_dense",
        "category": "performance"
    }


def _time_execution(cases: List[Dict[str, object]], repeats: int = 10) -> List[float]:
    measurements: List[float] = []
    executable = [case for case in cases if not case.get("expect_error")]
    for _ in range(repeats):
        start = time.perf_counter()
        for case in executable:
            compute_fastest_route(case["input"])
        measurements.append(time.perf_counter() - start)
    return measurements


def main() -> None:
    cases = _load_cases()
    cases.append(_stress_case())
    samples = _time_execution(cases, repeats=10)

    avg_ms = statistics.mean(samples) * 1000
    min_ms = min(samples) * 1000
    max_ms = max(samples) * 1000
    stdev_ms = statistics.pstdev(samples) * 1000 if len(samples) > 1 else 0.0

    print(f"executions={len(samples)}")
    print(f"avg_runtime_ms={avg_ms:.3f}")
    print(f"min_runtime_ms={min_ms:.3f}")
    print(f"max_runtime_ms={max_ms:.3f}")
    print(f"stdev_runtime_ms={stdev_ms:.3f}")

    try:
        result = compute_fastest_route(cases[-1]["input"])
        print(f"stress_cost={result['cost']:.3f}")
        print(f"stress_path_length={len(result['path'])}")
    except (RouteValidationError, RouteComputationError) as exc:
        print(f"stress_error={type(exc).__name__}:{exc}")


if __name__ == "__main__":
    main()
