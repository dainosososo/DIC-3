"""
Evaluation Metrics for LabSteward Benchmark
"""
import numpy as np
from typing import List, Dict, Any

def calculate_task_success_rate(results: List[Dict[str, Any]]) -> float:
    if not results:
        return 0.0
    correct = sum(1 for r in results if r["predicted_status"] == r["expected_status"])
    return correct / len(results)

def calculate_pass_at_k(n: int, c: int, k: int = 4) -> float:
    """
    pass@k estimator from HumanEval / tau-bench:
    1 - comb(n - c, k) / comb(n, k)
    """
    if n - c < k:
        return 1.0
    from math import comb
    try:
        return 1.0 - (comb(n - c, k) / comb(n, k))
    except Exception:
        return float(c) / float(n)

def calculate_mape(actual: List[float], predicted: List[float]) -> float:
    """Mean Absolute Percentage Error (MAPE)."""
    if not actual or len(actual) != len(predicted):
        return 0.0
    errors = []
    for a, p in zip(actual, predicted):
        if a > 0:
            errors.append(abs(a - p) / a)
    return float(np.mean(errors)) * 100.0 if errors else 0.0

def calculate_violation_rate(results: List[Dict[str, Any]]) -> float:
    """Percentage of tasks that resulted in statutory compliance violation."""
    if not results:
        return 0.0
    violations = sum(1 for r in results if r.get("illegal_action", False))
    return (violations / len(results)) * 100.0
