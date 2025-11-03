import json
import statistics
import time
from pathlib import Path

import pytest

from ProjectB.src.optimized_code import (
    OptimizedPermissionEvaluator,
    evaluate_permissions,
    load_cases,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "test_data.json"
LOG_PATH = BASE_DIR / "logs" / "log_optimized.txt"
PERF_PATH = BASE_DIR / "performance" / "time_optimized.txt"

RUN_METRICS = []


def _payload_copy(case_input):
    return json.loads(json.dumps(case_input))


def _record(case_name, category, success, elapsed, extras):
    RUN_METRICS.append(
        {
            "case": case_name,
            "category": category,
            "success": success,
            "duration": elapsed,
            "extras": extras,
        }
    )


@pytest.fixture(scope="module", autouse=True)
def _write_reports():
    yield
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    PERF_PATH.parent.mkdir(parents=True, exist_ok=True)

    total_cases = len(RUN_METRICS)
    successes = sum(1 for m in RUN_METRICS if m["success"])
    durations = [m["duration"] for m in RUN_METRICS]
    stress_runs = [m for m in RUN_METRICS if m["category"] == "stress"]
    mean_duration = statistics.mean(durations) if durations else 0.0
    p95_duration = statistics.quantiles(durations, n=20)[-1] if len(durations) >= 20 else max(durations) if durations else 0.0
    stress_mean = (
        statistics.mean(item["duration"] for item in stress_runs)
        if stress_runs
        else 0.0
    )

    log_lines = [
        f"Total cases: {total_cases}",
        f"Accuracy: {successes / total_cases if total_cases else 0.0:.3f}",
        f"Mean duration: {mean_duration:.6f}",
        f"95th percentile duration (approx): {p95_duration:.6f}",
        f"Stress mean duration: {stress_mean:.6f}",
    ]
    LOG_PATH.write_text("\n".join(log_lines), encoding="utf-8")

    perf_lines = ["case,duration_seconds,throughput_ops"]
    for metric in RUN_METRICS:
        perf_lines.append(
            f"{metric['case']},{metric['duration']:.8f},{metric['extras'].get('throughput_ops', 'n/a')}"
        )
    PERF_PATH.write_text("\n".join(perf_lines), encoding="utf-8")


@pytest.mark.parametrize("case", load_cases(DATA_PATH), ids=lambda c: c["name"])  # type: ignore[arg-type]
def test_permission_evaluator(case):
    evaluator = OptimizedPermissionEvaluator()
    payload = _payload_copy(case["input"])
    expected = case["expected"]
    category = case.get("category", "normal")

    start = time.perf_counter()
    if "error" in expected:
        with pytest.raises(ValueError) as exc:
            evaluator.evaluate(payload)
        duration = time.perf_counter() - start
        assert expected["error"] in str(exc.value)
        _record(case["name"], category, True, duration, {"mode": "error"})
        return

    result = evaluator.evaluate(payload)
    duration = time.perf_counter() - start

    if "allowed" in expected:
        assert set(result["allowed"]) == set(expected["allowed"])
    if "denied" in expected:
        assert set(result["denied"]) == set(expected["denied"])
    if "decision_map_subset" in expected:
        for action, decision in expected["decision_map_subset"].items():
            assert action in result["decision_map"]
            assert result["decision_map"][action]["status"] == decision["status"]
            assert result["decision_map"][action]["source"] == decision["source"]
    if "allowed_count" in expected:
        assert len(result["allowed"]) == expected["allowed_count"]
    if "denied_count" in expected:
        assert len(result["denied"]) == expected["denied_count"]
    if "must_contain_allowed" in expected:
        for action in expected["must_contain_allowed"]:
            assert action in result["allowed"]
    if "must_contain_denied" in expected:
        for action in expected["must_contain_denied"]:
            assert action in result["denied"]

    metadata = result["metadata"]
    assert metadata["evaluation_time_seconds"] <= duration + 1e-6
    coverage = metadata["coverage"]
    assert coverage["total_actions"] >= len(set(result["allowed"]) | set(result["denied"]))
    assert 0.0 <= coverage["denied_fraction"] <= 1.0
    assert metadata["quality"]["edge_case_success_rate"] >= 0.33

    throughput_ops = 0
    if category == "stress":
        payload_heavy = _payload_copy(case["input"])
        start_burst = time.perf_counter()
        iterations = 25
        for _ in range(iterations):
            evaluator.evaluate(payload_heavy)
        burst_duration = time.perf_counter() - start_burst
        throughput_ops = int(iterations / burst_duration) if burst_duration else iterations
        assert throughput_ops >= 80  # ensures optimization delivers throughput without flakiness

    _record(
        case["name"],
        category,
        True,
        duration,
        {
            "reported_time": metadata["evaluation_time_seconds"],
            "throughput_ops": throughput_ops,
        },
    )


def test_functional_wrapper_keeps_optimizations():
    payload = load_cases(DATA_PATH)[0]["input"]
    via_fn = evaluate_permissions(payload)
    via_class = OptimizedPermissionEvaluator().evaluate(payload)
    via_fn_meta = dict(via_fn)
    via_class_meta = dict(via_class)
    via_fn_meta["metadata"] = dict(via_fn_meta["metadata"])
    via_class_meta["metadata"] = dict(via_class_meta["metadata"])
    via_fn_meta["metadata"]["evaluation_time_seconds"] = 0.0
    via_class_meta["metadata"]["evaluation_time_seconds"] = 0.0
    assert via_fn_meta == via_class_meta
