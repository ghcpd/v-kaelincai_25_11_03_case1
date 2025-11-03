from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, Generator, List

import pytest

from src.optimized_code import compute_fastest_route, RouteComputationError, RouteValidationError

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_PATH = BASE_DIR / "data" / "test_data.json"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

with DATA_PATH.open("r", encoding="utf-8") as handle:
    TEST_DATA = json.load(handle)

TEST_CASES: List[Dict[str, object]] = TEST_DATA["test_cases"]
RESULTS: List[Dict[str, object]] = []


@pytest.fixture(scope="session", autouse=True)
def _prepare_directories() -> None:
    (BASE_DIR / "performance").mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)


@pytest.mark.parametrize("case", TEST_CASES, ids=lambda c: c["name"])
def test_compute_fastest_route(case: Dict[str, object]) -> None:
    start = time.perf_counter()
    expect_error = bool(case.get("expect_error"))
    name = str(case.get("name"))
    category = str(case.get("category", "unspecified"))
    try:
        result = compute_fastest_route(case["input"])
    except (RouteValidationError, RouteComputationError) as exc:
        duration = time.perf_counter() - start
        RESULTS.append(
            {
                "name": name,
                "category": category,
                "status": "error_expected" if expect_error else "unexpected_error",
                "duration": duration,
                "visited": 0,
                "error": f"{type(exc).__name__}:{exc}",
            }
        )
        if expect_error:
            assert True
        else:
            pytest.fail(f"Unexpected error for case '{name}': {exc}")
    else:
        duration = time.perf_counter() - start
        status = "success" if not expect_error else "unexpected_success"
        visited = result["visited_nodes"]
        RESULTS.append(
            {
                "name": name,
                "category": category,
                "status": status,
                "duration": duration,
                "visited": visited,
                "error": None,
            }
        )
        if expect_error:
            pytest.fail(f"Expected error for case '{name}' but computation succeeded.")
        expected = case.get("expected", {})
        assert result["path"] == expected["path"], "Route path mismatch"
        assert result["cost"] == pytest.approx(expected["cost"], rel=1e-6, abs=1e-6)
        assert visited <= len(case["input"]["nodes"])
        assert isinstance(result["warnings"], list)
        assert result["metadata"]["algorithm"] == "dijkstra_heap"


@pytest.fixture(scope="session", autouse=True)
def _metrics_writer() -> Generator[None, None, None]:
    yield
    total_cases = len(RESULTS)
    success_cases = sum(1 for entry in RESULTS if entry["status"] == "success")
    error_cases = sum(1 for entry in RESULTS if entry["status"].startswith("error"))
    unexpected_success = sum(1 for entry in RESULTS if entry["status"] == "unexpected_success")
    unexpected_error = sum(1 for entry in RESULTS if entry["status"] == "unexpected_error")
    categories = {entry["category"] for entry in RESULTS}
    covered_categories = {entry["category"] for entry in RESULTS if entry["status"] == "success"}
    edge_results = [entry for entry in RESULTS if entry["category"] == "edge"]
    edge_success = sum(1 for entry in edge_results if entry["status"] == "success")
    avg_duration = sum(entry["duration"] for entry in RESULTS) / total_cases if total_cases else 0.0
    avg_visited = (
        sum(entry["visited"] for entry in RESULTS if entry["status"] == "success")
        / success_cases
        if success_cases
        else 0.0
    )

    metrics = {
        "total_cases": total_cases,
        "success_cases": success_cases,
        "error_cases": error_cases,
        "unexpected_success": unexpected_success,
        "unexpected_error": unexpected_error,
        "accuracy": round(success_cases / total_cases, 4) if total_cases else 0.0,
        "category_coverage": round(len(covered_categories) / len(categories), 4) if categories else 0.0,
        "edge_case_success_rate": round(edge_success / len(edge_results), 4) if edge_results else 0.0,
        "average_duration_ms": round(avg_duration * 1000, 4),
        "average_visited_nodes": round(avg_visited, 4),
        "cases": RESULTS,
    }

    metrics_path = LOG_DIR / "metrics_optimized.json"
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
