"""Automated verification harness for the initial scheduling feature implementation."""

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

from original_code import ScheduleComputationError, compute_schedule  # type: ignore  # pylint: disable=wrong-import-position


def _float_equal(a: float, b: float, *, tolerance: float = 1e-9) -> bool:
    return math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)


def _compare_schedule(expected: Dict[str, Dict[str, float]], received: Dict[str, Dict[str, float]]) -> bool:
    if expected.keys() != received.keys():
        return False
    for task_id, expected_times in expected.items():
        actual_times = received.get(task_id)
        if actual_times is None:
            return False
        for key in ("start", "finish"):
            if key not in actual_times or not _float_equal(expected_times[key], float(actual_times[key])):
                return False
    return True


def load_cases(data_file: Path) -> List[Dict[str, Any]]:
    with data_file.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise RuntimeError("Test data must be a list of cases.")
    return data


def run_suite(cases: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    total = 0
    passed = 0
    edge_total = 0
    edge_passed = 0
    case_results: List[Dict[str, Any]] = []

    for case in cases:
        total += 1
        category = case.get("category", "normal")
        start_time = time.perf_counter()
        success = False
        failure_reason = None
        try:
            payload = case["input"]
            if "expect_error" in case:
                try:
                    compute_schedule(payload)
                except ScheduleComputationError as err:
                    success = case["expect_error"].lower() in str(err).lower()
                    if not success:
                        failure_reason = f"Error mismatch: got '{err}', wanted substring '{case['expect_error']}'."
                else:
                    failure_reason = "Expected ScheduleComputationError but none was raised."
            else:
                output = compute_schedule(payload)
                expected_output = case["expected"]
                schedule_ok = _compare_schedule(expected_output["schedule"], output["schedule"])
                total_ok = _float_equal(float(expected_output["total_duration"]), float(output["total_duration"]))
                success = schedule_ok and total_ok
                if not success:
                    failure_reason = (
                        "Schedule mismatch" if not schedule_ok else "Total duration mismatch"
                    )
        except ScheduleComputationError as err:
            failure_reason = f"Unexpected computation error: {err}"
        except Exception as unexpected:  # pragma: no cover - guard rail
            failure_reason = f"Unexpected exception: {unexpected}"  # type: ignore[str-bytes-safe]
        finally:
            elapsed = time.perf_counter() - start_time

        if category in {"edge", "invalid"}:
            edge_total += 1
            if success:
                edge_passed += 1

        if success:
            passed += 1

        case_results.append(
            {
                "name": case.get("name", f"case_{total}"),
                "category": category,
                "passed": success,
                "elapsed_sec": elapsed,
                "failure_reason": failure_reason,
            }
        )

    accuracy = passed / total if total else 0.0
    edge_success_rate = edge_passed / edge_total if edge_total else 0.0
    return {
        "total_cases": total,
        "passed": passed,
        "accuracy": accuracy,
        "edge_cases_total": edge_total,
        "edge_cases_passed": edge_passed,
        "edge_case_success_rate": edge_success_rate,
        "cases": case_results,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Execute the Project A validation suite.")
    parser.add_argument(
        "--data-file",
        default=str(ROOT / "data" / "input_data.json"),
        help="Path to JSON file containing structured test data.",
    )
    parser.add_argument("--log-file", help="Optional path to append a detailed execution log.")
    parser.add_argument("--metrics-file", help="Optional path to write metrics in JSON format.")
    parser.add_argument("--perf-file", help="Optional path to write run duration in seconds.")
    args = parser.parse_args(argv)

    data_path = Path(args.data_file)
    cases = load_cases(data_path)

    suite_start = time.perf_counter()
    results = run_suite(cases)
    total_elapsed = time.perf_counter() - suite_start
    results["total_runtime_sec"] = total_elapsed

    summary = (
        f"Executed {results['total_cases']} cases | Passed: {results['passed']} | "
        f"Accuracy: {results['accuracy']:.3f} | Edge success: {results['edge_case_success_rate']:.3f}"
    )
    print(summary)
    for case in results["cases"]:
        indicator = "PASS" if case["passed"] else "FAIL"
        print(f"[{indicator}] {case['name']} ({case['category']}) took {case['elapsed_sec']*1000:.2f} ms")
        if case["failure_reason"]:
            print(f"    Reason: {case['failure_reason']}")

    if args.log_file:
        log_path = Path(args.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as log_handle:
            log_handle.write(summary + "\n")
            for case in results["cases"]:
                line = json.dumps(case, ensure_ascii=False)
                log_handle.write(line + "\n")

    if args.metrics_file:
        metrics_path = Path(args.metrics_file)
        metrics_path.parent.mkdir(parents=True, exist_ok=True)
        with metrics_path.open("w", encoding="utf-8") as metrics_handle:
            json.dump(results, metrics_handle, indent=2)

    if args.perf_file:
        perf_path = Path(args.perf_file)
        perf_path.parent.mkdir(parents=True, exist_ok=True)
        with perf_path.open("w", encoding="utf-8") as perf_handle:
            perf_handle.write(f"{total_elapsed:.6f}\n")

    return 0 if results["passed"] == results["total_cases"] else 1


if __name__ == "__main__":
    sys.exit(main())
