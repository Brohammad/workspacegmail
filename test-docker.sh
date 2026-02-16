#!/bin/bash
# Test script to validate Docker setup (run this after installing Docker)

set -e

echo "🐳 Testing ZenBot Docker Setup"
echo "================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed."
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if docker compose is available
if command -v docker compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "✅ docker compose is installed"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "✅ Docker Compose (plugin) is available"
else
    echo "❌ Docker Compose is not available."
    echo "Install: https://docs.docker.com/compose/install/"
    exit 1
fi

echo ""
echo "📦 Building Docker image..."
$COMPOSE_CMD build

if [ $? -eq 0 ]; then
    echo "✅ Build successful"
else
    echo "❌ Build failed"
    exit 1
fi

echo ""
echo "🧪 Running test evaluation..."
$COMPOSE_CMD run --rm zenbot-evaluator python evaluators.py --tests test_cases.json --predictions predictions.json | head -20

if [ $? -eq 0 ]; then
    echo "✅ Test evaluation successful"
else
    echo "❌ Test evaluation failed"
    exit 1
fi

echo ""
echo "================================================"
echo "✅ All Docker tests passed!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Run full pipeline:"
echo "     $COMPOSE_CMD --profile full up full-pipeline"
echo ""
echo "  2. Run evaluation only:"
echo "     $COMPOSE_CMD up zenbot-evaluator"
echo ""
echo "  3. See DOCKER_SETUP.md for more options"
