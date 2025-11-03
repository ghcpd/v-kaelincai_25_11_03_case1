"""Initial implementation of the Smart Permission Aggregation feature.

This module intentionally favours clarity over efficiency to serve as the
pre-optimization baseline in Project A. The evaluator performs multiple passes
across the same collections and stores intermediate results in Python lists,
which leads to quadratic behaviour for large permission sets.
"""
from __future__ import annotations

import itertools
import json
import time
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Tuple

ActionEvent = Tuple[str, str]


class PermissionEvaluator:
    """Naive permission aggregator used in Project A.

    The evaluator merges direct, group, and role grants while enforcing
    precedence rules (deny wins over allow). It favours straightforward loops
    and repeated scans, which become costly for large tenant configurations.
    """

    def __init__(self) -> None:
        self._last_timing: float | None = None

    def evaluate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        start = time.perf_counter()
        user = payload.get("user")
        constraints = payload.get("constraints", {})

        if not isinstance(user, dict):
            raise ValueError("Payload must include a 'user' object")
        if "roles" not in user:
            raise ValueError("Missing required key: user.roles")

        # Expand generator shorthand before traversing; this copies data for every call.
        expanded_groups = self._expand_groups(user.get("groups"))

        # Aggregate actions with source provenance using repeated list concatenations.
        action_events: List[ActionEvent] = []
        action_events.extend(self._collect_actions(user.get("direct"), source="direct"))
        for group in expanded_groups:
            action_events.extend(self._collect_actions(group, source="group"))
        for role in user.get("roles", []):
            action_events.extend(self._collect_actions(role, source="role"))

        # Apply constraints (suspended actions) as explicit denies at the end.
        suspended = constraints.get("suspended_actions", []) or []
        for raw_action in suspended:
            action = self._normalize_action(raw_action)
            action_events.append((action, "deny:constraint"))

        # Produce final decision map by replaying history in order.
        allowed: List[str] = []
        denied: List[str] = []
        decision_map: Dict[str, Dict[str, str]] = {}
        for action, marker in action_events:
            status, source = self._split_marker(marker)
            if status == "allow":
                if action not in allowed:
                    allowed.append(action)
                # Only set decision if action not explicitly denied yet.
                if action not in decision_map:
                    decision_map[action] = {"status": "allow", "source": source}
            else:  # deny
                if action not in denied:
                    denied.append(action)
                decision_map[action] = {"status": "deny", "source": source}
                if action in allowed:
                    allowed.remove(action)

        metadata = self._build_metadata(constraints, allowed, denied)

        # Persist runtime measurement to performance log consumer.
        self._last_timing = time.perf_counter() - start

        return {
            "allowed": sorted(allowed),
            "denied": sorted(denied),
            "decision_map": decision_map,
            "metadata": metadata,
        }

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    def _expand_groups(self, groups: Any) -> List[Dict[str, Any]]:
        if groups is None:
            return []
        if isinstance(groups, dict) and "generator" in groups:
            gen = groups["generator"]
            base = deepcopy(gen.get("base", {}))
            if not base:
                return []
            count = int(gen.get("count", 0))
            deny_every = int(gen.get("deny_every", 0)) or None
            deny_actions = [self._normalize_action(a) for a in gen.get("deny_actions", [])]
            expanded: List[Dict[str, Any]] = []
            for idx in range(count):
                entry = deepcopy(base)
                entry["name"] = f"{base.get('name', 'group')}-{idx}"
                if deny_every and (idx + 1) % deny_every == 0:
                    entry.setdefault("deny", [])
                    entry["deny"] = list(entry["deny"]) + deny_actions
                expanded.append(entry)
            return expanded
        if isinstance(groups, list):
            return [deepcopy(g) for g in groups]
        raise ValueError("Groups section must be a list or generator descriptor")

    def _collect_actions(self, section: Any, source: str) -> List[ActionEvent]:
        if not section:
            return []
        if not isinstance(section, dict):
            raise ValueError(f"Section for source '{source}' must be a mapping")
        events: List[ActionEvent] = []
        for action in section.get("allow", []) or []:
            normalized = self._normalize_action(action)
            events.append((normalized, f"allow:{source}"))
        for action in section.get("deny", []) or []:
            normalized = self._normalize_action(action)
            events.append((normalized, f"deny:{source}"))
        return events

    def _normalize_action(self, action: Any) -> str:
        if isinstance(action, str):
            return action
        if isinstance(action, dict) and action.get("name"):
            return str(action["name"])
        raise ValueError(f"Unsupported action descriptor: {action!r}")

    def _split_marker(self, marker: str) -> Tuple[str, str]:
        status, _, source = marker.partition(":")
        return status, source or "unknown"

    def _build_metadata(self, constraints: Dict[str, Any], allowed: List[str], denied: List[str]) -> Dict[str, Any]:
        lockdown = bool(constraints.get("lockdown", False))
        unique_allowed = set(allowed)
        unique_denied = set(denied)
        total = len(unique_allowed | unique_denied)
        denied_fraction = 0.0 if total == 0 else round(len(unique_denied) / total, 3)
        coverage = {
            "total_actions": total,
            "denied_fraction": denied_fraction,
            "lockdown_active": lockdown,
        }
        return {
            "lockdown_active": lockdown,
            "coverage": coverage,
        }

    @property
    def last_timing(self) -> float | None:
        return self._last_timing


def evaluate_permissions(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience functional API used by tests."""

    evaluator = PermissionEvaluator()
    return evaluator.evaluate(payload)


def load_cases(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data["cases"]


__all__ = ["PermissionEvaluator", "evaluate_permissions", "load_cases"]
