from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import math


class RouteValidationError(ValueError):
    """Raised when the incoming payload cannot be validated."""


class RouteComputationError(RuntimeError):
    """Raised when a route cannot be computed for a valid payload."""


@dataclass
class ValidatedPayload:
    nodes: Tuple[str, ...]
    edges: Tuple[Tuple[str, str, float], ...]
    source: str
    target: str
    blocked_nodes: Set[str]
    blocked_edges: Set[Tuple[str, str]]
    warnings: Tuple[str, ...]


def _ensure_iterable(value: Any, *, name: str) -> Iterable[Any]:
    if isinstance(value, (list, tuple, set)):
        return value
    raise RouteValidationError(f"Expected '{name}' to be an iterable; received {type(value)!r}.")


def _validate_payload(payload: Dict[str, Any]) -> ValidatedPayload:
    if not isinstance(payload, dict):
        raise RouteValidationError("Payload must be a dictionary.")

    nodes_raw = payload.get("nodes")
    edges_raw = payload.get("edges")
    source = payload.get("source")
    target = payload.get("target")
    blocked_nodes_raw = payload.get("blocked_nodes", [])
    blocked_edges_raw = payload.get("blocked_edges", [])

    if not isinstance(source, str) or not source:
        raise RouteValidationError("Source node must be a non-empty string.")
    if not isinstance(target, str) or not target:
        raise RouteValidationError("Target node must be a non-empty string.")

    nodes_list = list(_ensure_iterable(nodes_raw, name="nodes"))
    if not nodes_list:
        raise RouteValidationError("Node list cannot be empty.")
    if len({node for node in nodes_list if isinstance(node, str)}) != len(nodes_list):
        raise RouteValidationError("All nodes must be unique strings.")
    if source not in nodes_list or target not in nodes_list:
        raise RouteValidationError("Source and target must be present in the node list.")

    edges: List[Tuple[str, str, float]] = []
    if edges_raw is None:
        raise RouteValidationError("Edges collection is required.")
    for raw_edge in _ensure_iterable(edges_raw, name="edges"):
        if not isinstance(raw_edge, dict):
            raise RouteValidationError("Each edge must be a dictionary.")
        start = raw_edge.get("from")
        end = raw_edge.get("to")
        weight = raw_edge.get("weight")
        if not isinstance(start, str) or not isinstance(end, str):
            raise RouteValidationError("Edge endpoints must be strings.")
        if start not in nodes_list or end not in nodes_list:
            raise RouteValidationError("Edge endpoints must exist in the node list.")
        if not isinstance(weight, (int, float)):
            raise RouteValidationError("Edge weight must be numeric.")
        if weight < 0:
            raise RouteValidationError("Edge weights must be non-negative.")
        edges.append((start, end, float(weight)))

    blocked_nodes = {node for node in _ensure_iterable(blocked_nodes_raw, name="blocked_nodes")}
    if not all(isinstance(node, str) for node in blocked_nodes):
        raise RouteValidationError("Blocked nodes must be strings.")

    blocked_edges: Set[Tuple[str, str]] = set()
    for blocked in _ensure_iterable(blocked_edges_raw, name="blocked_edges"):
        if not isinstance(blocked, dict):
            raise RouteValidationError("Blocked edges must be dictionaries.")
        start = blocked.get("from")
        end = blocked.get("to")
        if not isinstance(start, str) or not isinstance(end, str):
            raise RouteValidationError("Blocked edge endpoints must be strings.")
        blocked_edges.add((start, end))

    warnings: List[str] = []
    inaccessible_nodes = blocked_nodes.intersection({source, target})
    if inaccessible_nodes:
        warnings.append(
            "Requested route touches blocked nodes; algorithm will still attempt alternative traversal."
        )
    if source == target:
        warnings.append("Source and target are identical; returning zero-length path.")

    return ValidatedPayload(
        nodes=tuple(nodes_list),
        edges=tuple(edges),
        source=source,
        target=target,
        blocked_nodes=blocked_nodes,
        blocked_edges=blocked_edges,
        warnings=tuple(warnings),
    )


def _build_graph(payload: ValidatedPayload) -> Dict[str, Dict[str, float]]:
    adjacency: Dict[str, Dict[str, float]] = {node: {} for node in payload.nodes}
    for start, end, weight in payload.edges:
        if start in payload.blocked_nodes or end in payload.blocked_nodes:
            continue
        if (start, end) in payload.blocked_edges:
            continue
        # Keep the lightest edge when duplicates are supplied.
        existing = adjacency[start].get(end)
        if existing is None or weight < existing:
            adjacency[start][end] = weight
    return adjacency


def _reconstruct_path(
    parents: Dict[str, Optional[str]], source: str, target: str
) -> List[str]:
    current = target
    path: List[str] = []
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = parents.get(current)
        if current is None and path[-1] != source:
            raise RouteComputationError("No route to reconstruct for the provided target.")
    path.reverse()
    return path


def compute_fastest_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    validated = _validate_payload(payload)
    adjacency = _build_graph(validated)

    source = validated.source
    target = validated.target

    if source == target:
        return {
            "path": [source],
            "cost": 0.0,
            "visited_nodes": 1,
            "warnings": list(validated.warnings),
            "metadata": {"algorithm": "dijkstra_table", "blocked": sorted(validated.blocked_nodes)},
        }

    nodes = list(validated.nodes)
    distances: Dict[str, float] = {node: math.inf for node in nodes}
    parents: Dict[str, Optional[str]] = {node: None for node in nodes}
    visited: Set[str] = set()

    distances[source] = 0.0

    # Classic O(V^2) Dijkstra variant using a dense scan.
    for _ in nodes:
        current: Optional[str] = None
        current_distance = math.inf
        for node in nodes:
            if node in visited:
                continue
            if distances[node] < current_distance:
                current = node
                current_distance = distances[node]
        if current is None or current_distance is math.inf:
            break
        visited.add(current)
        for neighbor, weight in adjacency[current].items():
            if neighbor in visited:
                continue
            candidate = distances[current] + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                parents[neighbor] = current

    if distances[target] is math.inf:
        raise RouteComputationError("Target is unreachable with the provided constraints.")

    path = _reconstruct_path(parents, source, target)
    return {
        "path": path,
        "cost": round(distances[target], 6),
        "visited_nodes": len(visited),
        "warnings": list(validated.warnings),
        "metadata": {
            "algorithm": "dijkstra_table",
            "explored": sorted(visited),
            "blocked": sorted(validated.blocked_nodes),
        },
    }


__all__ = [
    "compute_fastest_route",
    "RouteValidationError",
    "RouteComputationError",
]
