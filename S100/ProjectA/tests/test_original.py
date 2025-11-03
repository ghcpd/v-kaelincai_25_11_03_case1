import json
import time
from pathlib import Path

import pytest

from ProjectA.src.original_code import PermissionEvaluator, evaluate_permissions, load_cases

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "input_data.json"
LOG_PATH = BASE_DIR / "logs" / "log_original.txt"
PERF_PATH = BASE_DIR / "performance" / "time_original.txt"

METRICS = []


def _expand_generated_input(case_input):
    """Return the evaluation payload while leaving generator instructions intact."""
    # The evaluator performs generator expansion internally; the helper simply
    # ensures the payload is a plain dictionary (pytest may freeze param values).
    return json.loads(json.dumps(case_input))


def _record(case_name, category, success, duration, notes):
    METRICS.append(
        {
            "case": case_name,
            "category": category,
            "success": success,
            "duration": duration,
            "notes": notes,
        }
    )


@pytest.fixture(scope="module", autouse=True)
def _write_reports():
    yield
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    PERF_PATH.parent.mkdir(parents=True, exist_ok=True)

    total_cases = len(METRICS)
    successes = sum(1 for m in METRICS if m["success"])
    invalid_cases = sum(1 for m in METRICS if m["category"] == "invalid")
    invalid_successes = sum(1 for m in METRICS if m["category"] == "invalid" and m["success"])
    stress_cases = sum(1 for m in METRICS if m["category"] == "stress")
    stress_durations = [m["duration"] for m in METRICS if m["category"] == "stress"]

    accuracy = successes / total_cases if total_cases else 0.0
    invalid_accuracy = invalid_successes / invalid_cases if invalid_cases else 0.0
    stress_time = max(stress_durations) if stress_durations else 0.0

    log_lines = [
        f"Total cases: {total_cases}",
        f"Accuracy: {accuracy:.3f}",
        f"Invalid-case success rate: {invalid_accuracy:.3f}",
        f"Stress-case max duration: {stress_time:.6f}"
    ]
    LOG_PATH.write_text("\n".join(log_lines), encoding="utf-8")

    perf_lines = [
        "case,duration_seconds",
    ]
    for metric in METRICS:
        perf_lines.append(f"{metric['case']},{metric['duration']:.8f}")
    PERF_PATH.write_text("\n".join(perf_lines), encoding="utf-8")


@pytest.mark.parametrize("case", load_cases(str(DATA_PATH)), ids=lambda c: c["name"])
def test_permission_aggregation(case):
    evaluator = PermissionEvaluator()
    payload = _expand_generated_input(case["input"])
    expected = case["expected"]
    category = case.get("category", "normal")

    start = time.perf_counter()
    if "error" in expected:
        with pytest.raises(ValueError) as exc:
            evaluator.evaluate(payload)
        duration = time.perf_counter() - start
        assert expected["error"] in str(exc.value)
        _record(case["name"], category, True, duration, "raised expected error")
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
    assert "coverage" in metadata
    assert metadata["coverage"]["total_actions"] >= len(result["allowed"]) + len(result["denied"]) - len(set(result["allowed"]) & set(result["denied"]))

    _record(case["name"], category, True, duration, "evaluated successfully")


def test_functional_wrapper_matches_class():
    payload = load_cases(str(DATA_PATH))[0]["input"]
    via_fn = evaluate_permissions(payload)
    via_class = PermissionEvaluator().evaluate(payload)
    assert via_fn == via_class
