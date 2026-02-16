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
    """Improved spec accuracy evaluator with better number extraction and fuzzy matching"""
    
    # Extract numeric tokens from both strings
    pred_nums = set(re.findall(r"\d+", prediction))
    exp_nums = set(re.findall(r"\d+", expected))
    
    # Filter out dates, months, years from predictions (but keep important years like 1786)
    filtered_pred_nums = {n for n in pred_nums 
                         if int(n) not in range(1, 32)  # not day of month
                         and int(n) not in [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]}  # not recent years
    
    # Filter expected numbers similarly
    filtered_exp_nums = {n for n in exp_nums if int(n) not in range(1, 32)}
    
    # Special handling for important numbers (specs, prices)
    important_nums = {n for n in filtered_exp_nums if int(n) >= 100}
    
    # Check for IS 1786 standard citation (various formats)
    has_standard = bool(re.search(r"is\s*1786|is1786", prediction, re.IGNORECASE))
    
    # Check if 1786 is in expected answer (only matters if it's a spec question)
    expects_standard = bool(re.search(r"is\s*1786|is1786", expected, re.IGNORECASE))
    
    # Calculate matching score
    if not important_nums:
        # Non-numeric answer (e.g., test case 4, 10)
        # Use fuzzy text matching instead
        pred_lower = prediction.lower()
        exp_lower = expected.lower()
        
        # Extract key phrases from expected
        key_phrases = []
        if "verify" in exp_lower or "consult" in exp_lower or "specialist" in exp_lower:
            key_phrases = ["verify", "consult", "team", "specialist", "inventory"]
        if "structural engineer" in exp_lower or "licensed" in exp_lower:
            key_phrases = ["structural", "engineer", "technical", "consult"]
        
        # Check if key phrases are present
        phrase_matches = sum(1 for phrase in key_phrases if phrase in pred_lower)
        score = 1.0 if phrase_matches >= 2 else (0.5 if phrase_matches == 1 else 0.0)
        
        return {
            "key": "spec_accuracy",
            "score": score,
            "comment": f"Text matching: {phrase_matches}/{len(key_phrases)} key phrases found"
        }
    
    # For numeric answers: check how many important numbers match
    matched_nums = important_nums & filtered_pred_nums
    match_ratio = len(matched_nums) / len(important_nums) if important_nums else 0.0
    
    # Scoring logic:
    # - Full credit (1.0): All numbers match + standard cited (if required)
    # - Partial credit (0.7): All numbers match but no standard citation
    # - Partial credit (0.5): Some numbers match
    # - No credit (0.0): No numbers match
    
    if match_ratio == 1.0:
        if expects_standard:
            score = 1.0 if has_standard else 0.7
        else:
            score = 1.0
    elif match_ratio >= 0.5:
        score = 0.5
    else:
        score = 0.0
    
    return {
        "key": "spec_accuracy",
        "score": score,
        "comment": f"Numbers: {len(matched_nums)}/{len(important_nums)} matched; standard cited: {has_standard}"
    }


def pricing_evaluator(prediction: str, expected: str):
    """Improved pricing evaluator with better price extraction"""
    
    # Extract price numbers - handle ₹, Rs, INR symbols and commas
    def find_prices(text):
        # Pattern: optional currency symbol + number with optional commas + optional decimals
        prices = []
        # Match patterns like: ₹52,500, Rs 52500, 52,500, INR 52500
        for match in re.finditer(r"(?:₹|Rs\.?|INR)?\s*([0-9][0-9,]*(?:\.\d+)?)", text):
            price_str = match.group(1).replace(",", "")
            try:
                prices.append(int(float(price_str)))
            except ValueError:
                continue
        return prices

    exp_prices = find_prices(expected)
    pred_prices = find_prices(prediction)
    
    # Check date context words
    date_words = ['november', '2024', 'current', 'as of', 'effective', 'nov']
    has_date = any(word in prediction.lower() for word in date_words)

    if not exp_prices:
        # No price expected in answer (e.g., test case 4, 10)
        score = 1.0
    else:
        # Check if any expected price is in predicted prices
        price_match = any(exp_p in pred_prices for exp_p in exp_prices)
        
        if price_match and has_date:
            score = 1.0
        elif price_match:
            score = 0.7
        else:
            # Check for close matches (within 5% tolerance)
            close_match = False
            for exp_p in exp_prices:
                for pred_p in pred_prices:
                    if abs(pred_p - exp_p) / exp_p <= 0.05:  # 5% tolerance
                        close_match = True
                        break
            score = 0.5 if close_match else 0.0

    return {
        "key": "pricing_accuracy", 
        "score": score, 
        "comment": f"exp_prices={exp_prices}, pred_prices={pred_prices}, date_ctx={has_date}"
    }


def hallucination_detector(prediction: str, expected: str):
    """Improved hallucination detector with more nuanced scoring"""
    
    pred = prediction.lower()
    
    # Words that indicate uncertainty (good - admits limitations)
    uncertainty = ["verify", "check with", "need to confirm", "don't have", "not sure", 
                   "consult", "i could not find", "please contact", "i need to", "let me connect"]
    
    # Words that indicate confidence with citations (good - backed by sources)
    confidence = ["as per", "according to", "based on", "specified in", "is 1786", 
                  "per is", "as stated", "documented"]
    
    # Words that indicate guessing WITHOUT sources (bad - hallucination risk)
    # Note: "approximately" is OK if used with confidence indicators
    guessing_bad = ["probably", "likely", "i think", "maybe", "i guess", "possibly"]
    
    # Approximate/around is OK if used with a source citation
    has_uncertainty = any(w in pred for w in uncertainty)
    has_confidence = any(w in pred for w in confidence)
    has_bad_guessing = any(w in pred for w in guessing_bad)
    
    # Check for "approximately" or "around" - only bad if no confidence indicators
    has_approximate = any(w in pred for w in ["approximately", "around", "roughly", "about", "~"])
    approximate_with_source = has_approximate and has_confidence

    # Scoring logic:
    # 1.0: Has confidence indicators OR admits uncertainty appropriately
    # 0.5: Uses approximations with sources OR neutral language
    # 0.0: Uses bad guessing words or approximations without sources
    
    if has_bad_guessing:
        score = 0.0
    elif approximate_with_source:
        # "approximately X as per IS 1786" is fine
        score = 1.0
    elif has_confidence or has_uncertainty:
        score = 1.0
    elif has_approximate:
        # "approximately X" without source is risky
        score = 0.5
    else:
        # Neutral language
        score = 0.5

    return {
        "key": "hallucination_check", 
        "score": score, 
        "comment": f"bad_guessing={has_bad_guessing}, confident={has_confidence}, admits_unknown={has_uncertainty}, approx_with_source={approximate_with_source}"
    }


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
