#!/usr/bin/env python3
"""
Run ZenBot on all 10 test cases from test_cases.json and generate traces.

This script loads the test questions from test_cases.json and runs zenbot.py
for both "buggy" and "fixed" versions, generating comprehensive trace coverage.
"""
import os
import json
import sys
from dotenv import load_dotenv

# Load environment variables FIRST before importing zenbot
load_dotenv()

# Import from zenbot AFTER loading environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zenbot import run_query, LangChainTracer


def main():
    # Load test cases
    with open("test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)
    
    print(f"🚀 Running ZenBot on {len(test_cases)} test questions...")
    print(f"   Generating traces for both 'buggy' and 'fixed' versions\n")
    
    # Create tracer
    tracer = None
    if LangChainTracer is not None:
        project = os.environ.get("LANGSMITH_PROJECT", "Zen_Project")
        tracer = LangChainTracer(project_name=project)
        print(f"✅ LangSmith tracer initialized for project: {project}")
    else:
        print("⚠️  LangSmith tracer not available (imports failed)")
    
    # Create output directory
    outdir = "langsmith_traces"
    os.makedirs(outdir, exist_ok=True)
    
    total_success = 0
    total_failed = 0
    
    # Run both versions for all test cases
    for version in ("buggy", "fixed"):
        print(f"\n{'='*80}")
        print(f"🔧 Running version: {version.upper()}")
        print(f"{'='*80}\n")
        
        for test_case in test_cases:
            test_id = test_case["id"]
            question = test_case["input"]
            expected = test_case["expected_answer"]
            
            print(f"\n[Test {test_id}] Question: {question}")
            print(f"[Test {test_id}] Expected: {expected[:80]}...")
            
            try:
                # Run query
                trace = run_query(question, version, tracer=tracer)
                
                # Print response
                answer = trace["answer"].strip()
                print(f"[Test {test_id}] Answer: {answer[:100]}...")
                
                # Save trace to file using test_id for consistent naming
                fname = os.path.join(outdir, f"sim_trace_{version}_{test_id}.json")
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(trace, f, indent=2, ensure_ascii=False)
                
                print(f"[Test {test_id}] ✅ Trace saved to: {fname}")
                total_success += 1
                
            except Exception as e:
                print(f"[Test {test_id}] ❌ Error running query: {e}")
                total_failed += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"📊 SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successful: {total_success}")
    print(f"❌ Failed: {total_failed}")
    print(f"📁 Traces saved to: {outdir}/")
    print(f"\nNext steps:")
    print(f"1. Run: python scripts/langsmith_to_predictions.py --trace-dir {outdir}")
    print(f"2. Run: python evaluators.py --predictions predictions_real.json")
    print(f"3. Check results and adjust thresholds if needed")


if __name__ == "__main__":
    main()
