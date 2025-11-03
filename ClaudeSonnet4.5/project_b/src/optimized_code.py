from __future__ import annotations

import heapq
import math
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


class RouteValidationError(ValueError):
    """Raised when payload validation fails."""


class RouteComputationError(RuntimeError):
    """Raised when a valid payload cannot produce a route."""


@dataclass(frozen=True)
class GraphModel:
    nodes: Tuple[str, ...]
    adjacency: Dict[str, Dict[str, float]]
    source: str
    target: str
    blocked_nodes: Set[str]
    blocked_edges: Set[Tuple[str, str]]
    warnings: Tuple[str, ...]


_ALLOWED_EDGE_KEYS = {"from", "to", "weight"}
_BLOCKED_EDGE_KEYS = {"from", "to"}


def _as_iterable(value: Any, *, label: str) -> Iterable[Any]:
    if isinstance(value, (list, tuple, set)):
        return value
    raise RouteValidationError(f"Field '{label}' must be an iterable; got {type(value).__name__}.")


def _validate_nodes(nodes_raw: Any) -> Tuple[str, ...]:
    nodes_candidate = list(_as_iterable(nodes_raw, label="nodes"))
    if not nodes_candidate:
        raise RouteValidationError("At least one node must be supplied.")
    for node in nodes_candidate:
        if not isinstance(node, str) or not node:
            raise RouteValidationError("Nodes must be non-empty strings.")
    if len(set(nodes_candidate)) != len(nodes_candidate):
        raise RouteValidationError("Node identifiers must be unique.")
    return tuple(nodes_candidate)


def _validate_edges(
    edges_raw: Any,
    nodes: Tuple[str, ...],
    blocked_nodes: Set[str],
    blocked_edges: Set[Tuple[str, str]],
) -> Dict[str, Dict[str, float]]:
    adjacency: Dict[str, Dict[str, float]] = {node: {} for node in nodes}
    if edges_raw is None:
        raise RouteValidationError("Edges collection is required.")

    for edge in _as_iterable(edges_raw, label="edges"):
        if not isinstance(edge, dict):
            raise RouteValidationError("Edge entries must be dictionaries.")
        if not _ALLOWED_EDGE_KEYS.issuperset(edge.keys()):
            raise RouteValidationError("Edge dictionaries contain unsupported keys.")
        start = edge.get("from")
        end = edge.get("to")
        weight = edge.get("weight")
        if not isinstance(start, str) or not isinstance(end, str):
            raise RouteValidationError("Edge endpoints must be strings.")
        if start not in adjacency or end not in adjacency:
            raise RouteValidationError("Edge endpoints must exist in the node set.")
        if not isinstance(weight, (int, float)) or math.isnan(weight) or math.isinf(weight):
            raise RouteValidationError("Edge weights must be finite numbers.")
        if weight < 0:
            raise RouteValidationError("Edge weights must be non-negative.")
        if start in blocked_nodes or end in blocked_nodes:
            continue
        if (start, end) in blocked_edges:
            continue
        current = adjacency[start].get(end)
        weight = float(weight)
        if current is None or weight < current:
            adjacency[start][end] = weight
    return adjacency


def _validate_payload(payload: Dict[str, Any]) -> GraphModel:
    if not isinstance(payload, dict):
        raise RouteValidationError("Payload must be a dictionary.")

    source = payload.get("source")
    target = payload.get("target")
    if not isinstance(source, str) or not source:
        raise RouteValidationError("Source must be a non-empty string.")
    if not isinstance(target, str) or not target:
        raise RouteValidationError("Target must be a non-empty string.")

    nodes = _validate_nodes(payload.get("nodes"))
    if source not in nodes or target not in nodes:
        raise RouteValidationError("Source and target must exist in the node set.")

    blocked_nodes = {
        node for node in _as_iterable(payload.get("blocked_nodes", []), label="blocked_nodes")
    }
    if not all(isinstance(node, str) for node in blocked_nodes):
        raise RouteValidationError("Blocked node identifiers must be strings.")

    blocked_edges: Set[Tuple[str, str]] = set()
    for blocked in _as_iterable(payload.get("blocked_edges", []), label="blocked_edges"):
        if not isinstance(blocked, dict):
            raise RouteValidationError("Blocked edges must be dictionaries.")
        if not _BLOCKED_EDGE_KEYS.issuperset(blocked.keys()):
            raise RouteValidationError("Blocked edge dictionaries contain unsupported keys.")
        start = blocked.get("from")
        end = blocked.get("to")
        if not isinstance(start, str) or not isinstance(end, str):
            raise RouteValidationError("Blocked edge endpoints must be strings.")
        blocked_edges.add((start, end))

    warnings: List[str] = []
    if source == target:
        warnings.append("Source equals target; returning trivial route.")
    intersect = blocked_nodes.intersection({source, target})
    if intersect:
        warnings.append(
            "Route end-points intersect with blocked nodes; attempting alternate resolution."
        )

    adjacency = _validate_edges(
        edges_raw=payload.get("edges"),
        nodes=nodes,
        blocked_nodes=blocked_nodes,
        blocked_edges=blocked_edges,
    )

    return GraphModel(
        nodes=nodes,
        adjacency=adjacency,
        source=source,
        target=target,
        blocked_nodes=blocked_nodes,
        blocked_edges=blocked_edges,
        warnings=tuple(warnings),
    )


def _reconstruct_path(parents: Dict[str, Optional[str]], source: str, target: str) -> List[str]:
    current = target
    path: List[str] = []
    while current is not None:
        path.append(current)
        if current == source:
            break
        current = parents[current]
    if not path or path[-1] != source:
        raise RouteComputationError("Unable to reconstruct route to source.")
    path.reverse()
    return path


def compute_fastest_route(payload: Dict[str, Any]) -> Dict[str, Any]:
    model = _validate_payload(payload)

    if model.source == model.target:
        return {
            "path": [model.source],
            "cost": 0.0,
            "visited_nodes": 1,
            "warnings": list(model.warnings),
            "metadata": {
                "algorithm": "dijkstra_heap",
                "relaxations": 0,
                "blocked": sorted(model.blocked_nodes),
            },
        }

    distances: Dict[str, float] = {node: math.inf for node in model.nodes}
    parents: Dict[str, Optional[str]] = {node: None for node in model.nodes}
    visited: Set[str] = set()
    relaxations = 0
    queue: List[Tuple[float, str]] = [(0.0, model.source)]
    distances[model.source] = 0.0

    while queue:
        current_distance, node = heapq.heappop(queue)
        if node in visited:
            continue
        visited.add(node)
        if node == model.target:
            break
        neighbors = model.adjacency.get(node)
        if not neighbors:
            continue
        for neighbor, weight in neighbors.items():
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                parents[neighbor] = node
                relaxations += 1
                heapq.heappush(queue, (new_distance, neighbor))

    if distances[model.target] is math.inf:
        raise RouteComputationError("Target is unreachable under current constraints.")

    path = _reconstruct_path(parents, model.source, model.target)

    return {
        "path": path,
        "cost": round(distances[model.target], 6),
        "visited_nodes": len(visited),
        "warnings": list(model.warnings),
        "metadata": {
            "algorithm": "dijkstra_heap",
            "relaxations": relaxations,
            "explored": sorted(visited),
            "blocked": sorted(model.blocked_nodes),
        },
    }


__all__ = [
    "compute_fastest_route",
    "RouteValidationError",
    "RouteComputationError",
]
