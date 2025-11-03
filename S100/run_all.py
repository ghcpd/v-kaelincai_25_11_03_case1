#!/usr/bin/env python
"""Master orchestration script for running both Project A and Project B test suites."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
PROJECTS = [
    {
        "name": "ProjectA",
        "requirements": ROOT / "ProjectA" / "requirements.txt",
        "tests": ROOT / "ProjectA" / "tests",
        "log_file": ROOT / "ProjectA" / "logs" / "log_original.txt",
        "perf_file": ROOT / "ProjectA" / "performance" / "time_original.txt",
    },
    {
        "name": "ProjectB",
        "requirements": ROOT / "ProjectB" / "requirements_optimized.txt",
        "tests": ROOT / "ProjectB" / "tests",
        "log_file": ROOT / "ProjectB" / "logs" / "log_optimized.txt",
        "perf_file": ROOT / "ProjectB" / "performance" / "time_optimized.txt",
    },
]


def _install_requirements(requirements: Path) -> None:
    if not requirements.exists():
        raise FileNotFoundError(f"Requirements file not found: {requirements}")
    print(f"\n[setup] Installing dependencies from {requirements}")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
        check=True,
    )


def _run_pytest(test_path: Path, project_dir: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(project_dir), pythonpath]))
    print(f"[tests] Running pytest for {project_dir.name}")
    return subprocess.run(
        [sys.executable, "-m", "pytest", str(test_path), "--disable-warnings", "-q"],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )


def _parse_log(log_path: Path) -> Dict[str, str]:
    if not log_path.exists():
        return {}
    content = log_path.read_text(encoding="utf-8").strip()
    lines = [line for line in content.splitlines() if line]
    return {f"line_{idx}": value for idx, value in enumerate(lines, start=1)}


def _parse_perf(perf_path: Path) -> Dict[str, str]:
    if not perf_path.exists():
        return {}
    rows = perf_path.read_text(encoding="utf-8").strip().splitlines()
    return {"rows": rows}


def main() -> None:
    summary: List[Dict[str, object]] = []
    started_at = time.time()

    for project in PROJECTS:
        project_dir = ROOT / project["name"]
        _install_requirements(project["requirements"])
        start = time.time()
        result = _run_pytest(project["tests"], project_dir)
        duration = time.time() - start
        print(result.stdout)
        summary.append(
            {
                "project": project["name"],
                "exit_code": result.returncode,
                "duration_seconds": round(duration, 4),
                "log_metrics": _parse_log(project["log_file"]),
                "performance_samples": _parse_perf(project["perf_file"]),
            }
        )

    total_time = time.time() - started_at
    aggregate = {
        "ran_projects": len(PROJECTS),
        "total_duration_seconds": round(total_time, 4),
        "project_summaries": summary,
    }
    (ROOT / "comparison_summary.json").write_text(
        json.dumps(aggregate, indent=2),
        encoding="utf-8",
    )
    print("\n[summary]")
    print(json.dumps(aggregate, indent=2))


if __name__ == "__main__":
    main()
