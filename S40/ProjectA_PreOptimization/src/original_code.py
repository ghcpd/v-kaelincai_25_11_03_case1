"""Initial implementation of dependency-based task scheduling feature.

This module introduces a new feature for computing earliest start and finish times for
tasks with explicit dependency relationships. The implementation intentionally favors
clarity over efficiency, using a simple iterative approach to resolve dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple


class ScheduleComputationError(ValueError):
    """Raised when the schedule cannot be computed because of invalid input."""


@dataclass
class Task:
    task_id: str
    duration: float
    dependencies: Tuple[str, ...]

    @classmethod
    def from_payload(cls, payload: Dict[str, object]) -> "Task":
        if not isinstance(payload, dict):
            raise ScheduleComputationError("Each task must be a dictionary.")
        try:
            raw_id = payload["id"]
            raw_duration = payload["duration"]
        except KeyError as missing:
            raise ScheduleComputationError(f"Task missing required field: {missing.args[0]}") from None

        if not isinstance(raw_id, str) or not raw_id:
            raise ScheduleComputationError("Task id must be a non-empty string.")
        if not isinstance(raw_duration, (int, float)):
            raise ScheduleComputationError("Task duration must be numeric.")
        if raw_duration < 0:
            raise ScheduleComputationError("Task duration must be non-negative.")

        raw_dependencies: Iterable[object] = payload.get("depends_on", ())
        if raw_dependencies is None:
            raw_dependencies = ()
        if isinstance(raw_dependencies, (str, bytes)):
            raise ScheduleComputationError("Task depends_on must be a list of task ids.")
        if not isinstance(raw_dependencies, Iterable):
            raise ScheduleComputationError("Task depends_on must be an iterable of task ids.")

        deps: List[str] = []
        for value in raw_dependencies:
            if not isinstance(value, str) or not value:
                raise ScheduleComputationError("Dependency identifiers must be non-empty strings.")
            deps.append(value)

        return cls(task_id=raw_id, duration=float(raw_duration), dependencies=tuple(deps))


def _normalise_tasks(payload: Dict[str, object]) -> Dict[str, Task]:
    if not isinstance(payload, dict):
        raise ScheduleComputationError("Payload must be a dictionary.")
    try:
        raw_tasks = payload["tasks"]
    except KeyError as exc:
        raise ScheduleComputationError("Payload must contain a 'tasks' key.") from exc

    if not isinstance(raw_tasks, list) or not raw_tasks:
        raise ScheduleComputationError("Payload tasks must be a non-empty list.")

    task_map: Dict[str, Task] = {}
    for raw in raw_tasks:
        task = Task.from_payload(raw)
        if task.task_id in task_map:
            raise ScheduleComputationError(f"Duplicate task identifier: {task.task_id}")
        task_map[task.task_id] = task
    return task_map


def compute_schedule(payload: Dict[str, object]) -> Dict[str, object]:
    """Compute earliest start/finish times for all tasks.

    Parameters
    ----------
    payload: dict
        Expected structure: {"tasks": [{"id": str, "duration": number, "depends_on": [str, ...]}, ...]}

    Returns
    -------
    dict
        Schema: {
            "schedule": {task_id: {"start": float, "finish": float}},
            "total_duration": float,
        }
    """

    task_map = _normalise_tasks(payload)
    processed: Dict[str, Dict[str, float]] = {}
    remaining = set(task_map)

    # Naive iterative approach: repeatedly scan remaining tasks until none can be scheduled.
    max_iterations = len(task_map) * (len(task_map) + 1)
    iterations = 0
    while remaining:
        progressed = False
        for task_id in list(remaining):
            task = task_map[task_id]
            missing_dependency = next((dep for dep in task.dependencies if dep not in task_map), None)
            if missing_dependency is not None:
                raise ScheduleComputationError(
                    f"Task '{task_id}' depends on unknown task '{missing_dependency}'."
                )

            if all(dep in processed for dep in task.dependencies):
                start = 0.0
                if task.dependencies:
                    start = max(processed[dep]["finish"] for dep in task.dependencies)
                finish = start + task.duration
                processed[task_id] = {"start": start, "finish": finish}
                remaining.remove(task_id)
                progressed = True
        iterations += 1
        if not progressed:
            raise ScheduleComputationError("Cycle detected or dependencies unresolved; schedule cannot be computed.")
        if iterations > max_iterations:
            raise ScheduleComputationError("Exceeded iteration limit while computing schedule.")

    total_duration = max((info["finish"] for info in processed.values()), default=0.0)
    return {"schedule": processed, "total_duration": total_duration}


__all__ = ["compute_schedule", "ScheduleComputationError"]
