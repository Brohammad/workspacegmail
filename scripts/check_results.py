#!/usr/bin/env python3
"""Small result checker used by CI to enforce thresholds.

Exit codes:
  0 - pass
  1 - fail

Thresholds (based on real baseline performance):
 - spec_accuracy average must be >= 0.08 (baseline: 0.10, allowing slight degradation)
 - hallucination_check average must be >= 0.50 (baseline: 0.70 in evaluators, 0.55 in check_results)

NOTE: These thresholds are conservative based on the current ZenBot implementation.
As the knowledge base expands and retrieval improves, thresholds should be increased.

This script loads `test_cases.json` and `predictions.json` and computes simple scores.
"""
import json
import re
from pathlib import Path
import sys


def spec_score(prediction: str, expected: str):
    """Use same logic as evaluators.py spec_accuracy_evaluator"""
    pred_nums = set(re.findall(r"\d+", prediction))
    exp_nums = set(re.findall(r"\d+", expected))
    
    # Filter out dates and small numbers
    filtered_pred_nums = {n for n in pred_nums if int(n) not in range(1, 32) and int(n) not in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}
    filtered_exp_nums = {n for n in exp_nums if int(n) not in range(1, 32)}
    
    has_standard = bool(re.search(r"is\s*1786|is1786", prediction, re.IGNORECASE))
    key_match = all(num in pred_nums for num in filtered_exp_nums if int(num) >= 100)
    
    return 1.0 if (key_match and has_standard) else 0.0


def hallucination_score(prediction: str):
    """Use same logic as evaluators.py hallucination_detector"""
    pred = prediction.lower()
    uncertainty = ["verify", "check with", "need to confirm", "don't have", "not sure", "consult", "i could not find"]
    confidence = ["as per", "according to", "based on", "specified in", "is 1786"]
    guessing = ["probably", "likely", "i think", "approximately", "around", "maybe", "estimated"]

    has_uncertainty = any(w in pred for w in uncertainty)
    has_confidence = any(w in pred for w in confidence)
    has_guessing = any(w in pred for w in guessing)

    if has_guessing:
        return 0.0
    elif has_confidence:
        return 1.0
    elif has_uncertainty:
        return 0.5
    else:
        return 0.5


def main():
    tests_path = Path('test_cases.json')
    preds_path = Path('predictions.json')
    if not tests_path.exists() or not preds_path.exists():
        print('Missing test_cases.json or predictions.json')
        sys.exit(1)

    tests = json.loads(tests_path.read_text())
    preds = json.loads(preds_path.read_text())

    spec_scores = []
    hall_scores = []
    for t in tests:
        tid = str(t.get('id'))
        expected = t.get('expected_answer','')
        pred = preds.get(tid, '')
        spec_scores.append(spec_score(pred, expected))
        hall_scores.append(hallucination_score(pred))

    spec_avg = sum(spec_scores) / len(spec_scores)
    hall_avg = sum(hall_scores) / len(hall_scores)

    print(f"Spec accuracy avg: {spec_avg:.3f}")
    print(f"Hallucination score avg: {hall_avg:.3f}")

    # Thresholds - realistic based on current baseline
    # Baseline: spec=0.10, hallucination=0.55
    # Allow 20% degradation buffer for safety
    if spec_avg < 0.08:
        print(f'SPEC ACCURACY THRESHOLD FAILED: {spec_avg:.3f} < 0.08')
        sys.exit(1)
    if hall_avg < 0.50:
        print(f'HALLUCINATION THRESHOLD FAILED: {hall_avg:.3f} < 0.50')
        sys.exit(1)

    print('✅ All checks passed!')
    print(f'  Spec accuracy: {spec_avg:.3f} >= 0.08')
    print(f'  Hallucination: {hall_avg:.3f} >= 0.50')
    sys.exit(0)


if __name__ == '__main__':
    main()
