"""Validation harness for the optimised scheduling implementation."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, Iterable, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from optimized_code import ScheduleValidationError, compute_schedule  # type: ignore  # pylint: disable=wrong-import-position


def _close(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(a, b, rel_tol=tol, abs_tol=tol)


def _compare_schedule(expected: Dict[str, Dict[str, float]], received: Dict[str, Dict[str, float]]) -> bool:
    if expected.keys() != received.keys():
        return False
    for task_id, expectations in expected.items():
        actual = received.get(task_id)
        if not actual:
            return False
        if not _close(expectations["start"], float(actual["start"])):
            return False
        if not _close(expectations["finish"], float(actual["finish"])):
            return False
        if float(actual.get("slack", 0.0)) < -1e-9:
            return False
    return True


def load_cases(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise RuntimeError("Test data must be a list of cases.")
    return data


def run_suite(cases: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    total = 0
    passed = 0
    edge_total = 0
    edge_passed = 0
    total_runtime = 0.0

    for case in cases:
        total += 1
        category = case.get("category", "normal")
        start = time.perf_counter()
        success = False
        failure_reason = None
        try:
            payload = case["input"]
            if "expect_error" in case:
                try:
                    compute_schedule(payload)
                except ScheduleValidationError as err:
                    expected_substring = case["expect_error"].lower()
                    success = expected_substring in str(err).lower()
                    if not success:
                        failure_reason = f"Error message mismatch: {err}"
                else:
                    failure_reason = "Expected ScheduleValidationError but computation succeeded."
            else:
                output = compute_schedule(payload)
                schedule_match = _compare_schedule(case["expected"]["schedule"], output["schedule"])
                duration_match = _close(float(case["expected"]["total_duration"]), float(output["total_duration"]))
                success = schedule_match and duration_match
                if not schedule_match:
                    failure_reason = "Schedule mismatch"
                elif not duration_match:
                    failure_reason = "Total duration mismatch"
        except ScheduleValidationError as err:
            failure_reason = f"Unexpected validation error: {err}"
        except Exception as err:  # pragma: no cover - defensive
            failure_reason = f"Unexpected exception: {err}"  # type: ignore[str-bytes-safe]
        elapsed = time.perf_counter() - start
        total_runtime += elapsed

        if category in {"edge", "invalid"}:
            edge_total += 1
            if success:
                edge_passed += 1
        if success:
            passed += 1

        results.append(
            {
                "name": case.get("name", f"case_{total}"),
                "category": category,
                "passed": success,
                "elapsed_sec": elapsed,
                "failure_reason": failure_reason,
            }
        )

    accuracy = passed / total if total else 0.0
    edge_rate = edge_passed / edge_total if edge_total else 0.0
    return {
        "total_cases": total,
        "passed": passed,
        "accuracy": accuracy,
        "edge_cases_total": edge_total,
        "edge_cases_passed": edge_passed,
        "edge_case_success_rate": edge_rate,
        "total_runtime_sec": total_runtime,
        "cases": results,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute Project B validation suite.")
    parser.add_argument(
        "--data-file",
        default=str(ROOT / "data" / "test_data.json"),
        help="JSON file containing structured test cases.",
    )
    parser.add_argument("--log-file", help="Path to append execution logs.")
    parser.add_argument("--metrics-file", help="Path to write metrics JSON.")
    parser.add_argument("--perf-file", help="Path to persist total execution time.")
    args = parser.parse_args(argv)

    cases = load_cases(Path(args.data_file))
    suite_results = run_suite(cases)

    summary = (
        f"Executed {suite_results['total_cases']} cases | Passed: {suite_results['passed']} | "
        f"Accuracy: {suite_results['accuracy']:.3f} | Edge success: {suite_results['edge_case_success_rate']:.3f}"
    )
    print(summary)
    for case in suite_results["cases"]:
        indicator = "PASS" if case["passed"] else "FAIL"
        print(f"[{indicator}] {case['name']} ({case['category']}) took {case['elapsed_sec']*1000:.2f} ms")
        if case["failure_reason"]:
            print(f"    Reason: {case['failure_reason']}")

    if args.log_file:
        log_path = Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(summary + "\n")
            for case in suite_results["cases"]:
                handle.write(json.dumps(case, ensure_ascii=False) + "\n")

    if args.metrics_file:
        metrics_path = Path(args.metrics_file)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with metrics_path.open("w", encoding="utf-8") as handle:
            json.dump(suite_results, handle, indent=2)

    if args.perf_file:
        perf_path = Path(args.perf_file)
        perf_path.parent.mkdir(parents=True, exist_ok=True)
        with perf_path.open("w", encoding="utf-8") as handle:
            handle.write(f"{suite_results['total_runtime_sec']:.6f}\n")

    return 0 if suite_results["passed"] == suite_results["total_cases"] else 1


if __name__ == "__main__":
    sys.exit(main())
