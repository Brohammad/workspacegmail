#!/usr/bin/env python3
"""Simple evaluation harness for the ZenBot case study.

Usage:
  - Place model outputs in `predictions.json` (map from case id to output string)
  - Run: python3 evaluators.py

This script implements three evaluators described in the case study:
  - spec_accuracy_evaluator
  - pricing_evaluator
  - hallucination_detector

It loads `test_cases.json` and `predictions.json` and prints per-case and aggregate scores.
"""

import json
import re
from pathlib import Path
import argparse


def spec_accuracy_evaluator(prediction: str, expected: str):
    # Extract numeric tokens (integers) from both, but filter out dates and other irrelevant numbers
    pred_nums = set(re.findall(r"\d+", prediction))
    exp_nums = set(re.findall(r"\d+", expected))
    
    # Filter out common date/metadata numbers from pred_nums (2024, 2019, 01-12 for months, etc.)
    filtered_pred_nums = {n for n in pred_nums if int(n) not in range(1, 32) and int(n) not in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}
    filtered_exp_nums = {n for n in exp_nums if int(n) not in range(1, 32)}
    
    # Check for IS 1786 standard citation (various formats)
    has_standard = bool(re.search(r"is\s*1786|is1786", prediction, re.IGNORECASE))
    
    # Check if key numbers (yield/tensile strength values, prices) are present
    # We need at least the main specification numbers, not all numbers
    key_match = all(num in pred_nums for num in filtered_exp_nums if int(num) >= 100)
    
    score = 1.0 if (key_match and has_standard) else 0.0
    return {
        "key": "spec_accuracy",
        "score": score,
        "comment": f"Key numbers: {filtered_exp_nums} in {filtered_pred_nums}; standard cited: {has_standard}"
    }


def pricing_evaluator(prediction: str, expected: str):
    # Extract price numbers (allow commas)
    def find_price(text):
        m = re.search(r"(?:\u20B9|Rs\.?|INR)?\s*([0-9][0-9,]+)", text)
        return m.group(1).replace(",", "") if m else None

    exp_price = find_price(expected)
    pred_price = find_price(prediction)

    # Check date context words
    date_words = ['november', '2024', 'current', 'as of', 'effective']
    has_date = any(word in prediction.lower() for word in date_words)

    if exp_price is None:
        score = 1.0
    else:
        price_match = (pred_price is not None and pred_price == exp_price)
        if price_match and has_date:
            score = 1.0
        elif price_match:
            score = 0.7
        else:
            score = 0.0

    return {"key": "pricing_accuracy", "score": score, "comment": f"exp_price={exp_price}, pred_price={pred_price}, date_ctx={has_date}"}


def hallucination_detector(prediction: str, expected: str):
    pred = prediction.lower()
    uncertainty = ["verify", "check with", "need to confirm", "don't have", "not sure", "consult", "i could not find"]
    confidence = ["as per", "according to", "based on", "specified in", "is 1786"]
    guessing = ["probably", "likely", "i think", "approximately", "around", "maybe", "estimated"]

    has_uncertainty = any(w in pred for w in uncertainty)
    has_confidence = any(w in pred for w in confidence)
    has_guessing = any(w in pred for w in guessing)

    if has_guessing:
        score = 0.0
    elif has_confidence or has_uncertainty:
        score = 1.0
    else:
        score = 0.5

    return {"key": "hallucination_check", "score": score, "comment": f"guessing={has_guessing}, confident={has_confidence}, admits_unknown={has_uncertainty}"}


def run_evaluation(test_cases_path: Path, predictions_path: Path):
    tests = json.loads(test_cases_path.read_text())
    preds = json.loads(predictions_path.read_text())

    results = []
    agg = {"spec_accuracy": [], "pricing_accuracy": [], "hallucination_check": []}

    for case in tests:
        cid = str(case.get("id"))
        inp = case.get("input")
        expected = case.get("expected_answer", "")
        prediction = preds.get(cid, "")

        spec_r = spec_accuracy_evaluator(prediction, expected)
        price_r = pricing_evaluator(prediction, expected)
        hall_r = hallucination_detector(prediction, expected)

        agg[spec_r['key']].append(spec_r['score'])
        agg[price_r['key']].append(price_r['score'])
        agg[hall_r['key']].append(hall_r['score'])

        results.append({
            "id": cid,
            "input": inp,
            "prediction": prediction,
            "expected": expected,
            "evaluations": [spec_r, price_r, hall_r]
        })

    # Print per-case summary
    print("Evaluation results per test case:\n")
    for r in results:
        print(f"Case {r['id']}: spec={r['evaluations'][0]['score']}, pricing={r['evaluations'][1]['score']}, hallucination={r['evaluations'][2]['score']}")

    # Aggregate
    summary = {}
    for k, vals in agg.items():
        summary[k] = {"avg_score": sum(vals) / len(vals) if vals else None, "count": len(vals)}

    print("\nAggregate summary:")
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tests", type=str, default="test_cases.json", help="Path to test_cases.json")
    parser.add_argument("--predictions", type=str, default="predictions.json", help="Path to predictions.json")
    args = parser.parse_args()

    tests_path = Path(args.tests)
    preds_path = Path(args.predictions)

    if not tests_path.exists():
        print(f"Test cases file not found: {tests_path}")
        return
    if not preds_path.exists():
        print(f"Predictions file not found: {preds_path}")
        print("Create predictions.json mapping test id -> output, or run ZenBot to capture outputs into the file.")
        return

    run_evaluation(tests_path, preds_path)


if __name__ == "__main__":
    main()
