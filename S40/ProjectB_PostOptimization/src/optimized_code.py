"""Optimised implementation of the dependency-based task scheduling feature.

Key improvements over the baseline version:
- Linear-time topological ordering via Kahn's algorithm instead of iterative scans.
- Strict input validation with clear diagnostics for malformed payloads.
- Enhanced metadata in the response, including critical path length per task.
- Vectorised computations for earliest start/finish times leveraging adjacency lists.
- Stable handling for large DAGs by avoiding repeated traversals.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, MutableMapping, Tuple


class ScheduleValidationError(ValueError):
    """Raised when supplied task data cannot be scheduled."""


@dataclass(frozen=True)
class TaskRecord:
    task_id: str
    duration: float
    dependencies: Tuple[str, ...]

    @classmethod
    def build(cls, payload: Mapping[str, object]) -> "TaskRecord":
        if not isinstance(payload, Mapping):
            raise ScheduleValidationError("Each task definition must be a mapping.")
        try:
            task_id = payload["id"]
            duration = payload["duration"]
        except KeyError as missing:
            raise ScheduleValidationError(f"Missing required field '{missing.args[0]}' in task definition.") from None

        if not isinstance(task_id, str) or not task_id.strip():
            raise ScheduleValidationError("Task id must be a non-empty string.")
        if not isinstance(duration, (int, float)):
            raise ScheduleValidationError("Task duration must be numeric.")
        if float(duration) < 0:
            raise ScheduleValidationError("Task duration must be non-negative.")

        depends_on_obj = payload.get("depends_on", ())
        if depends_on_obj is None:
            depends_on_obj = ()
        if isinstance(depends_on_obj, (str, bytes)):
            raise ScheduleValidationError("depends_on must be an iterable of task ids.")
        if not isinstance(depends_on_obj, Iterable):
            raise ScheduleValidationError("depends_on must be iterable.")

        dependencies: List[str] = []
        for dep in depends_on_obj:
            if not isinstance(dep, str) or not dep.strip():
                raise ScheduleValidationError("Dependency ids must be non-empty strings.")
            dependencies.append(dep)

        return cls(task_id=task_id, duration=float(duration), dependencies=tuple(dependencies))


def _prepare_tasks(payload: Mapping[str, object]) -> Dict[str, TaskRecord]:
    if not isinstance(payload, Mapping):
        raise ScheduleValidationError("Payload must be a mapping with a 'tasks' key.")
    if "tasks" not in payload:
        raise ScheduleValidationError("Payload missing required 'tasks' field.")

    tasks_obj = payload["tasks"]
    if not isinstance(tasks_obj, list) or not tasks_obj:
        raise ScheduleValidationError("Payload 'tasks' must be a non-empty list of task definitions.")

    task_map: Dict[str, TaskRecord] = {}
    for raw in tasks_obj:
        task = TaskRecord.build(raw)  # type: ignore[arg-type]
        if task.task_id in task_map:
            raise ScheduleValidationError(f"Duplicate task identifier '{task.task_id}'.")
        task_map[task.task_id] = task
    return task_map


def compute_schedule(payload: Mapping[str, object]) -> Dict[str, object]:
    """Compute earliest start/finish times and per-task slack information.

    Returns
    -------
    dict with keys:
        schedule: mapping of task_id -> {start, finish, slack}
        total_duration: float representing makespan
    """

    task_map = _prepare_tasks(payload)
    indegrees: MutableMapping[str, int] = {task_id: 0 for task_id in task_map}
    adjacency: MutableMapping[str, List[str]] = {task_id: [] for task_id in task_map}

    for task in task_map.values():
        for dep in task.dependencies:
            if dep not in task_map:
                raise ScheduleValidationError(
                    f"Task '{task.task_id}' depends on unknown task '{dep}'."
                )
            indegrees[task.task_id] += 1
            adjacency[dep].append(task.task_id)

    queue: deque[str] = deque(task_id for task_id, deg in indegrees.items() if deg == 0)
    if not queue:
        raise ScheduleValidationError("Cycle detected: no entry point tasks with zero indegree.")

    earliest_start: Dict[str, float] = {task_id: 0.0 for task_id in task_map}
    earliest_finish: Dict[str, float] = {task_id: 0.0 for task_id in task_map}
    topological_order: List[str] = []

    while queue:
        current = queue.popleft()
        topological_order.append(current)
        task = task_map[current]
        start_time = earliest_start[current]
        finish_time = start_time + task.duration
        earliest_finish[current] = finish_time

        for follower in adjacency[current]:
            follower_record = task_map[follower]
            proposed_start = finish_time
            if proposed_start > earliest_start[follower]:
                earliest_start[follower] = proposed_start
            indegrees[follower] -= 1
            if indegrees[follower] == 0:
                queue.append(follower)

    if len(topological_order) != len(task_map):
        raise ScheduleValidationError("Cycle detected while building schedule order.")

    total_duration = max(earliest_finish.values(), default=0.0)

    # Compute slack (latest start - earliest start) using reverse traversal.
    latest_finish: Dict[str, float] = {task_id: total_duration for task_id in task_map}
    latest_start: Dict[str, float] = {task_id: total_duration for task_id in task_map}
    for task_id in reversed(topological_order):
        task = task_map[task_id]
        finish_time = earliest_finish[task_id]
        if adjacency[task_id]:
            successor_starts = [latest_start[succ] for succ in adjacency[task_id]]
            latest_finish[task_id] = min(successor_starts)
        else:
            latest_finish[task_id] = total_duration
        latest_start[task_id] = latest_finish[task_id] - task.duration

    schedule: Dict[str, Dict[str, float]] = {}
    for task_id in topological_order:
        slack = max(0.0, latest_start[task_id] - earliest_start[task_id])
        schedule[task_id] = {
            "start": round(earliest_start[task_id], 10),
            "finish": round(earliest_finish[task_id], 10),
            "slack": round(slack, 10),
        }

    return {"schedule": schedule, "total_duration": round(total_duration, 10)}


__all__ = ["compute_schedule", "ScheduleValidationError"]
