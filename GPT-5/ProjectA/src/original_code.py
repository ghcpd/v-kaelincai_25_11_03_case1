"""Naive JSON diff implementation (pre-optimization).

Feature: Produce a diff summary between two JSON-like structures (dict/list/primitives).
Issues intentionally present:
 - Inefficient recursion (string path concatenation at every step)
 - Limited error handling (malformed JSON strings raise exceptions)
 - Treats type changes as generic modifications
 - Deep recursion risk for very nested inputs
 - Does not normalize non-dict/list roots
"""
from __future__ import annotations
import json
from typing import Any, Dict


def _ensure_parsed(value: Any) -> Any:
    # Intentionally no try/except for malformed JSON strings.
    if isinstance(value, str):
        # If it's a JSON string try to parse, else leave as string
        if value.strip().startswith('{') or value.strip().startswith('['):
            return json.loads(value)
    return value


def diff_json(a: Any, b: Any) -> Dict[str, Any]:
    a = _ensure_parsed(a)
    b = _ensure_parsed(b)

    changes = {
        'added': {},
        'removed': {},
        'modified': {},
        'type_changed': {},  # Intentionally never populated
    }
    stats = {
        'total_paths_compared': 0,
        'num_added': 0,
        'num_removed': 0,
        'num_modified': 0,
        'num_type_changed': 0,
    }
    errors = []

    def walk(x: Any, y: Any, path: str):
        stats['total_paths_compared'] += 1
        # Basic type divergence leads to modification rather than type_changed
        if type(x) != type(y):  # noqa: E721
            changes['modified'][path] = {'old': x, 'new': y}
            stats['num_modified'] += 1
            return
        if isinstance(x, dict):
            # Keys present in y but not x are added
            for k in y.keys() - x.keys():
                p = f"{path}.{k}" if path else k
                changes['added'][p] = y[k]
                stats['num_added'] += 1
            # Keys present in x but not y are removed
            for k in x.keys() - y.keys():
                p = f"{path}.{k}" if path else k
                changes['removed'][p] = x[k]
                stats['num_removed'] += 1
            # Recurse common keys
            for k in x.keys() & y.keys():
                p = f"{path}.{k}" if path else k
                walk(x[k], y[k], p)
        elif isinstance(x, list):
            # Compare element-wise up to min length
            min_len = min(len(x), len(y))
            for i in range(min_len):
                p = f"{path}[{i}]" if path else f"[{i}]"
                walk(x[i], y[i], p)
            # Remaining elements are added/removed
            if len(y) > len(x):
                for i in range(len(x), len(y)):
                    p = f"{path}[{i}]" if path else f"[{i}]"
                    changes['added'][p] = y[i]
                    stats['num_added'] += 1
            elif len(x) > len(y):
                for i in range(len(y), len(x)):
                    p = f"{path}[{i}]" if path else f"[{i}]"
                    changes['removed'][p] = x[i]
                    stats['num_removed'] += 1
        else:
            if x != y:
                changes['modified'][path] = {'old': x, 'new': y}
                stats['num_modified'] += 1

    try:
        walk(a, b, '')
    except Exception as e:  # Broad except; will hide precise issues
        errors.append(str(e))

    result = {'changes': changes, 'stats': stats, 'errors': errors}
    return result


if __name__ == '__main__':
    # Simple manual run example
    sample_a = {"a": 1, "b": 2}
    sample_b = {"a": 1, "b": 3, "c": 4}
    from pprint import pprint
    pprint(diff_json(sample_a, sample_b))
