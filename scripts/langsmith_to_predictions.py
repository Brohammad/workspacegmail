#!/usr/bin/env python3
"""Simple converter: LangSmith trace export -> predictions.json

This script supports two modes:
 - Local trace file: pass --trace-file traces.json (JSON array or JSONL). It will attempt
   to match tests from test_cases.json to trace inputs and extract the assistant's output.
 - (Optional) LangSmith API: if you provide LANGSMITH_API_KEY and the project slug, you
   can implement an API fetch by editing the fetch_traces() function. The code is left
   intentionally simple and safe (no network calls by default).

Usage:
  python3 scripts/langsmith_to_predictions.py --tests test_cases.json --trace-file traces.json --out predictions.json

The resulting `predictions.json` maps test id -> assistant output (string).
"""

import json
from pathlib import Path
import argparse
import os


def load_tests(tests_path: Path):
    return json.loads(tests_path.read_text())


def load_traces_from_file(trace_path: Path):
    text = trace_path.read_text()
    # Try JSON array first
    try:
        data = json.loads(text)
        # If it's a dict with 'traces' key, unwrap
        if isinstance(data, dict) and 'traces' in data:
            return data['traces']
        return data
    except Exception:
        # Try JSONL
        traces = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                traces.append(json.loads(line))
            except Exception:
                continue
        return traces


def fetch_traces_from_langsmith(api_key: str, project: str):
    """Fetch traces from LangSmith API."""
    import requests
    
    # LangSmith API endpoint for traces
    base_url = "https://api.smith.langchain.com"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Get runs/traces from the project
    url = f"{base_url}/runs"
    params = {
        "project": project,
        "limit": 100,  # Adjust as needed
        "offset": 0
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract runs - LangSmith returns runs in a 'runs' field
        runs = data.get('runs', []) if isinstance(data, dict) else data
        
        print(f"Fetched {len(runs)} runs from LangSmith project '{project}'")
        return runs
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from LangSmith API: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text[:500]}")
        raise


def extract_input_and_output(trace_item: dict):
    """Try to extract a user input string and assistant output string from a trace item.
    
    For our ZenBot trace format: 'question' field is the input, 'answer' field is the output.
    """
    user_text = None
    assistant_text = None

    # ZenBot trace format
    if 'question' in trace_item and isinstance(trace_item['question'], str):
        user_text = trace_item['question']
    if 'answer' in trace_item and isinstance(trace_item['answer'], str):
        assistant_text = trace_item['answer']

    # LangSmith run structure: inputs/outputs (fallback)
    if not user_text and 'inputs' in trace_item:
        inputs = trace_item['inputs']
        if isinstance(inputs, dict):
            # Common field names in LangSmith
            for key in ('input', 'query', 'question', 'prompt', 'text'):
                if key in inputs and isinstance(inputs[key], str):
                    user_text = inputs[key]
                    break
        elif isinstance(inputs, str):
            user_text = inputs

    if not assistant_text and 'outputs' in trace_item:
        outputs = trace_item['outputs']
        if isinstance(outputs, dict):
            # Common output field names
            for key in ('output', 'answer', 'response', 'text', 'content'):
                if key in outputs and isinstance(outputs[key], str):
                    assistant_text = outputs[key]
                    break
        elif isinstance(outputs, str):
            assistant_text = outputs

    # Legacy fallback fields
    if not user_text and 'input' in trace_item and isinstance(trace_item['input'], str):
        user_text = trace_item['input']
    if not assistant_text and 'output' in trace_item and isinstance(trace_item['output'], str):
        assistant_text = trace_item['output']

    return user_text, assistant_text


def match_tests_to_traces(tests, traces):
    # Build mapping of test id -> prediction
    preds = {}

    # Separate fixed and buggy traces, prefer fixed
    fixed_traces = [tr for tr in traces if tr.get('version') == 'fixed']
    buggy_traces = [tr for tr in traces if tr.get('version') == 'buggy']
    
    print(f"Found {len(fixed_traces)} fixed traces and {len(buggy_traces)} buggy traces")

    for t in tests:
        tid = str(t.get('id'))
        inp = t.get('input', '').lower().strip()
        matched = False
        
        # Try fixed traces first
        for trace_set, version in [(fixed_traces, 'fixed'), (buggy_traces, 'buggy')]:
            if matched:
                break
                
            # Try exact match first
            for tr in trace_set:
                user_text, assistant_text = extract_input_and_output(tr)
                if not user_text or not assistant_text:
                    continue
                if inp and inp == user_text.lower().strip():
                    preds[tid] = assistant_text
                    matched = True
                    print(f"Exact match for test {tid} ({version}): '{inp[:30]}...'")
                    break
            
            # If no exact match, try partial match on key terms
            if not matched:
                # Extract key terms from test input
                key_terms = []
                if 'yield strength' in inp:
                    key_terms.extend(['yield strength', 'fe 550d'])
                if 'price' in inp and 'tmt' in inp:
                    key_terms.extend(['price', 'tmt'])
                if 'delivery' in inp:
                    key_terms.append('delivery')
                if 'tensile strength' in inp:
                    key_terms.extend(['tensile strength', 'fe 550d'])
                if 'difference' in inp:
                    key_terms.extend(['difference', 'fe 500', 'fe 550d'])
                    
                for tr in trace_set:
                    user_text, assistant_text = extract_input_and_output(tr)
                    if not user_text or not assistant_text:
                        continue
                    user_lower = user_text.lower()
                    
                    # Check if most key terms match
                    matches = sum(1 for term in key_terms if term in user_lower)
                    if key_terms and matches >= len(key_terms) // 2:  # At least half the key terms
                        preds[tid] = assistant_text
                        matched = True
                        print(f"Partial match for test {tid} ({version}): '{inp[:30]}...' -> '{user_text[:30]}...'")
                        break
        
        if not matched:
            preds[tid] = ""  # empty string if no match found
            print(f"No match found for test {tid}: '{inp[:30]}...'")

    return preds


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tests', required=True, help='Path to test_cases.json')
    parser.add_argument('--trace-file', help='Path to local traces export (JSON or JSONL)')
    parser.add_argument('--out', default='predictions.json', help='Output predictions.json path')
    parser.add_argument('--use-langsmith', action='store_true', help='(Optional) attempt to fetch traces from LangSmith API (not implemented)')
    args = parser.parse_args()

    tests_path = Path(args.tests)
    if not tests_path.exists():
        print(f"Tests file not found: {tests_path}")
        return

    if args.use_langsmith:
        api_key = os.environ.get('LANGSMITH_API_KEY')
        project = os.environ.get('LANGSMITH_PROJECT')
        if not api_key or not project:
            print('LANGSMITH_API_KEY and LANGSMITH_PROJECT are required in env to fetch from LangSmith')
            return
        traces = fetch_traces_from_langsmith(api_key, project)
    else:
        if not args.trace_file:
            print('Provide --trace-file when not using --use-langsmith')
            return
        trace_path = Path(args.trace_file)
        if not trace_path.exists():
            print(f'Trace file not found: {trace_path}')
            return
        traces = load_traces_from_file(trace_path)

    tests = load_tests(tests_path)
    preds = match_tests_to_traces(tests, traces)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(preds, indent=2))
    print(f'Wrote predictions to {out_path} (matched {sum(1 for v in preds.values() if v)}/{len(preds)})')


if __name__ == '__main__':
    main()
