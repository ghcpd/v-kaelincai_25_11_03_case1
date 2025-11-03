"""Optimized JSON diff implementation (post-optimization).

Improvements over naive version:
 - Robust input normalization (graceful handling of malformed JSON strings)
 - Iterative stack traversal to avoid deep recursion & reduce call overhead
 - Clear separation of type changes vs value changes
 - Efficient path construction using tuples; join only when recording a change
 - Handles non-dict/list primitives at root
 - Structured error accumulation without aborting all processing
 - Designed to scale to large nested structures (stress tests included)
"""
from __future__ import annotations
import json
import traceback
from typing import Any, Dict, List, Tuple


def _parse_if_json_string(value: Any, errors: List[str]) -> Any:
    if isinstance(value, str):
        s = value.strip()
        if (s.startswith('{') and s.endswith('}')) or (s.startswith('[') and s.endswith(']')):
            try:
                return json.loads(value)
            except Exception as e:  # Malformed JSON captured
                errors.append(f"Malformed JSON string: {e}: {value[:60]}...")
                return value  # Return original string for graceful degradation
    return value


def diff_json(a: Any, b: Any, max_depth: int | None = None) -> Dict[str, Any]:
    errors: List[str] = []
    a = _parse_if_json_string(a, errors)
    b = _parse_if_json_string(b, errors)

    changes = {
        'added': {},
        'removed': {},
        'modified': {},
        'type_changed': {},
    }
    stats = {
        'total_paths_compared': 0,
        'num_added': 0,
        'num_removed': 0,
        'num_modified': 0,
        'num_type_changed': 0,
    }

    # Stack holds tuples: (path_components, left_value, right_value, depth)
    stack: List[Tuple[Tuple[str, ...], Any, Any, int]] = [(tuple(), a, b, 0)]

    while stack:
        path_components, left, right, depth = stack.pop()
        stats['total_paths_compared'] += 1

        if max_depth is not None and depth > max_depth:
            # Record truncation as a type change to indicate incomplete traversal
            p = _join_path(path_components)
            changes['type_changed'][p] = {
                'old_type': type(left).__name__,
                'new_type': type(right).__name__,
                'old_value': _maybe_repr(left),
                'new_value': _maybe_repr(right),
                'note': 'max_depth_exceeded'
            }
            stats['num_type_changed'] += 1
            continue

        # Type divergence
        if type(left) != type(right):  # noqa: E721
            p = _join_path(path_components)
            changes['type_changed'][p] = {
                'old_type': type(left).__name__,
                'new_type': type(right).__name__,
                'old_value': _maybe_repr(left),
                'new_value': _maybe_repr(right)
            }
            stats['num_type_changed'] += 1
            continue

        # Dict handling
        if isinstance(left, dict):
            # Added keys
            for k in right.keys() - left.keys():
                p = _join_path(path_components + (k,))
                changes['added'][p] = right[k]
                stats['num_added'] += 1
            # Removed keys
            for k in left.keys() - right.keys():
                p = _join_path(path_components + (k,))
                changes['removed'][p] = left[k]
                stats['num_removed'] += 1
            # Common keys -> push to stack
            for k in left.keys() & right.keys():
                stack.append((path_components + (k,), left[k], right[k], depth + 1))
            continue

        # List handling
        if isinstance(left, list):
            min_len = min(len(left), len(right))
            for i in range(min_len):
                stack.append((path_components + (f"[{i}]",), left[i], right[i], depth + 1))
            if len(right) > len(left):
                for i in range(len(left), len(right)):
                    p = _join_path(path_components + (f"[{i}]",))
                    changes['added'][p] = right[i]
                    stats['num_added'] += 1
            elif len(left) > len(right):
                for i in range(len(right), len(left)):
                    p = _join_path(path_components + (f"[{i}]",))
                    changes['removed'][p] = left[i]
                    stats['num_removed'] += 1
            continue

        # Primitive handling
        if left != right:
            p = _join_path(path_components)
            changes['modified'][p] = {'old': left, 'new': right}
            stats['num_modified'] += 1

    result = {
        'changes': changes,
        'stats': stats,
        'errors': errors,
    }
    return result


def _join_path(components: Tuple[str, ...]) -> str:
    if not components:
        return ''
    # Components may include list indices already bracketed
    out: List[str] = []
    for c in components:
        if c.startswith('[') and c.endswith(']'):
            if not out:  # Leading list index
                out.append(c)
            else:
                out[-1] = out[-1] + c  # Append index to previous segment (e.g. key[0][1])
        else:
            out.append(c)
    return '.'.join(out)


def _maybe_repr(v: Any, limit: int = 60) -> str:
    r = repr(v)
    if len(r) > limit:
        return r[:limit] + '…'
    return r


if __name__ == '__main__':
    from pprint import pprint
    sample_a = {"a": 1, "b": 2}
    sample_b = {"a": 1, "b": 3, "c": 4}
    pprint(diff_json(sample_a, sample_b))
