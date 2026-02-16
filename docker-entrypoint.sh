#!/bin/bash
# Entrypoint script for ZenBot evaluation container

set -e

echo "================================================"
echo "ZenBot Evaluation Pipeline"
echo "================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Using environment variables from docker-compose."
fi

# Function to run evaluation
run_evaluation() {
    echo "🔍 Running evaluation..."
    python evaluators.py --tests test_cases.json --predictions "${PREDICTIONS_FILE:-predictions_real.json}"
    echo "✅ Evaluation complete"
}

# Function to convert traces
convert_traces() {
    echo "🔄 Converting traces to predictions..."
    
    # Check if combined_traces.json exists, if not create it
    if [ ! -f combined_traces.json ]; then
        echo "📦 Combining individual trace files..."
        python -c "
import json
from pathlib import Path
traces = []
for f in Path('langsmith_traces').glob('*.json'):
    traces.append(json.loads(f.read_text()))
Path('combined_traces.json').write_text(json.dumps(traces, indent=2))
print(f'Combined {len(traces)} traces')
"
    fi
    
    python scripts/langsmith_to_predictions.py \
        --tests test_cases.json \
        --trace-file "${TRACE_FILE:-combined_traces.json}" \
        --out "${OUTPUT_FILE:-predictions_real.json}"
    echo "✅ Traces converted"
}

# Function to check thresholds
check_thresholds() {
    echo "✔️  Checking quality thresholds..."
    python scripts/check_results.py
    if [ $? -eq 0 ]; then
        echo "✅ All thresholds passed"
    else
        echo "❌ Threshold check failed"
        exit 1
    fi
}

# Main execution based on command
case "${1:-evaluate}" in
    evaluate)
        run_evaluation
        ;;
    convert)
        convert_traces
        ;;
    check)
        check_thresholds
        ;;
    full)
        convert_traces
        run_evaluation
        check_thresholds
        ;;
    *)
        echo "Usage: $0 {evaluate|convert|check|full}"
        echo ""
        echo "  evaluate - Run evaluation only"
        echo "  convert  - Convert traces to predictions"
        echo "  check    - Check quality thresholds"
        echo "  full     - Run complete pipeline"
        exit 1
        ;;
esac

echo ""
echo "================================================"
echo "Done!"
echo "================================================"
