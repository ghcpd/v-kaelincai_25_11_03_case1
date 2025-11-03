"""Test runner for Project A (naive implementation).
Collects metrics and writes logs & performance summary.
"""
import json
import os
import time
import tracemalloc
from pathlib import Path
from typing import Any, Dict
import sys

# Ensure workspace root is on sys.path for package imports
ROOT_PATH = Path(__file__).resolve().parents[2]
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from ProjectA.src.original_code import diff_json

DATA_FILE = Path(__file__).parent.parent / 'data' / 'input_data.json'
LOG_FILE = Path(__file__).parent.parent / 'logs' / 'log_original.txt'
PERF_FILE = Path(__file__).parent.parent / 'performance' / 'time_original.txt'
SUMMARY_FILE = Path(__file__).parent.parent / 'performance' / 'summary.json'


def _generate_large_case(size: int, changes: int):
    base = {f"k{i}": i for i in range(size)}
    modified = base.copy()
    # apply modifications
    for j in range(changes):
        key = f"k{j}"  # modify first few
        modified[key] = base[key] + 1
    # additions
    modified['extra1'] = 'X'
    modified['extra2'] = 'Y'
    # removal
    if 'k999' in modified:
        del modified['k999']
    return base, modified


def run_tests():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        cases = json.load(f)

    results = []
    category_pass = {}
    total_pass = 0

    tracemalloc.start()
    start_suite = time.perf_counter()

    for case in cases:
        cid = case['id']
        expected = case['expected']
        category = case.get('category', 'unknown')
        if 'generator' in case:
            gen = case['generator']
            a, b = _generate_large_case(gen['size'], gen['changes'])
        else:
            a = case['input_a']
            b = case['input_b']
        t0 = time.perf_counter()
        try:
            diff = diff_json(a, b)
            elapsed = (time.perf_counter() - t0) * 1000.0
            stats = diff['stats']
            pass_case = True
            for k in ['num_added', 'num_removed', 'num_modified', 'num_type_changed']:
                if stats.get(k) != expected.get(k):
                    pass_case = False
                    break
            errors = diff['errors']
        except Exception as e:  # Capture crash for invalid inputs
            elapsed = (time.perf_counter() - t0) * 1000.0
            stats = {"num_added": 0, "num_removed": 0, "num_modified": 0, "num_type_changed": 0}
            pass_case = False
            errors = [f"EXCEPTION: {e}"]
        total_pass += int(pass_case)
        category_pass.setdefault(category, {'total': 0, 'passed': 0})
        category_pass[category]['total'] += 1
        category_pass[category]['passed'] += int(pass_case)
        results.append({
            'id': cid,
            'category': category,
            'pass': pass_case,
            'expected': expected,
            'actual': stats,
            'time_ms': round(elapsed, 3),
            'errors': errors,
        })

    peak_current, peak_alloc = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    suite_elapsed = (time.perf_counter() - start_suite) * 1000.0

    accuracy = total_pass / len(results) if results else 0.0
    edge_rate = 0.0
    if 'edge' in category_pass:
        cp = category_pass['edge']
        edge_rate = cp['passed'] / cp['total'] if cp['total'] else 0.0

    summary = {
        'implementation': 'naive',
        'total_cases': len(results),
        'passed': total_pass,
        'accuracy': accuracy,
        'edge_case_success_rate': edge_rate,
        'category_breakdown': category_pass,
        'suite_time_ms': round(suite_elapsed, 3),
        'peak_memory_bytes': peak_alloc,
        'results': results,
    }

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    PERF_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, 'w', encoding='utf-8') as lf:
        for r in results:
            lf.write(f"{r['id']} | category={r['category']} | pass={r['pass']} | time_ms={r['time_ms']} | errors={len(r['errors'])}\n")
    with open(PERF_FILE, 'w', encoding='utf-8') as pf:
        pf.write(f"suite_time_ms={summary['suite_time_ms']}\npeak_memory_bytes={summary['peak_memory_bytes']}\naccuracy={summary['accuracy']}\nedge_case_success_rate={summary['edge_case_success_rate']}\n")
    with open(SUMMARY_FILE, 'w', encoding='utf-8') as sf:
        json.dump(summary, sf, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    run_tests()
