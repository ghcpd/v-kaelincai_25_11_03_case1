from __future__ import annotations

import json
import random
import statistics
import time
from pathlib import Path
from typing import Dict, List

from .original_code import compute_fastest_route, RouteComputationError, RouteValidationError


def _load_cases() -> List[Dict[str, object]]:
    base_path = Path(__file__).resolve().parents[1]
    data_path = base_path / "data" / "input_data.json"
    with data_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload["test_cases"]


def _synthetic_dense_case(nodes: int = 120) -> Dict[str, object]:
    node_names = [f"N{i}" for node in range(nodes)]
    edges = []
    for start in node_names:
        for end_offset in range(1, 4):
            end_index = (int(start[1:]) + end_offset) % nodes
            end = node_names[end_index]
            weight = 1.0 + (end_index % 7)
            edges.append({"from": start, "to": end, "weight": weight})
    return {
        "input": {
            "nodes": node_names,
            "edges": edges,
            "source": node_names[0],
            "target": node_names[nodes // 2],
            "blocked_nodes": [],
            "blocked_edges": [],
        },
        "expected": {},
        "name": "synthetic_dense",
        "category": "performance",
        "expect_error": False,
    }


def _run_single_iteration(cases: List[Dict[str, object]]) -> float:
    start = time.perf_counter()
    for case in cases:
        if case.get("expect_error"):
            continue
        compute_fastest_route(case["input"])
    return time.perf_counter() - start


def main() -> None:
    cases = _load_cases()
    synthetic = _synthetic_dense_case()
    execution_samples: List[float] = []
    extended_cases = cases + [synthetic]
    for _ in range(5):
        random.shuffle(extended_cases)
        duration = _run_single_iteration(extended_cases)
        execution_samples.append(duration)

    avg_ms = statistics.mean(execution_samples) * 1000
    p95_ms = statistics.median_high(sorted(execution_samples)) * 1000

    print(f"executions=5")
    print(f"avg_runtime_ms={avg_ms:.3f}")
    print(f"median_runtime_ms={statistics.median(execution_samples) * 1000:.3f}")
    print(f"p95_runtime_ms={p95_ms:.3f}")
    print(f"max_runtime_ms={max(execution_samples) * 1000:.3f}")

    try:
        result = compute_fastest_route(synthetic["input"])
        print(f"synthetic_cost={result['cost']:.3f}")
        print(f"synthetic_path_length={len(result['path'])}")
    except (RouteValidationError, RouteComputationError) as exc:
        print(f"synthetic_error={type(exc).__name__}:{exc}")


if __name__ == "__main__":
    main()
