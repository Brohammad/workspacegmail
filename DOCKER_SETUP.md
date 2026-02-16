# 🐳 Docker Setup for ZenBot Evaluation Pipeline

## Quick Start (3 Commands)

### 1. Build the Docker Image
```bash
docker compose build
```

### 2. Run Evaluation
```bash
docker compose up zenbot-evaluator
```

### 3. Run Full Pipeline (Convert + Evaluate + Check)
```bash
docker compose --profile full up full-pipeline
```

---

## What's Included

The Docker setup provides:
- ✅ Python 3.10 runtime
- ✅ All dependencies pre-installed
- ✅ Evaluation pipeline ready to run
- ✅ Volume mounts for traces and results
- ✅ Multiple service profiles for different use cases

---

## Available Services

### Default Service: `zenbot-evaluator`
Runs evaluation on existing predictions.

```bash
docker compose up zenbot-evaluator
```

**What it does:**
- Loads `predictions_real.json`
- Runs 3 evaluators (spec_accuracy, pricing_accuracy, hallucination)
- Prints aggregate summary

---

### Trace Converter: `trace-converter`
Converts LangSmith traces to predictions.

```bash
docker compose --profile converter up trace-converter
```

**What it does:**
- Reads traces from `langsmith_traces/` or `traces/`
- Matches traces to test cases
- Generates `predictions_real.json`

---

### CI Checker: `ci-checker`
Checks if results meet quality thresholds.

```bash
docker compose --profile ci up ci-checker
```

**What it does:**
- Loads `predictions_real.json` and `test_cases.json`
- Checks spec_accuracy ≥ 100%, hallucination ≥ 80%
- Exits with code 1 if thresholds not met

---

### Full Pipeline: `full-pipeline`
Runs everything: convert → evaluate → check.

```bash
docker compose --profile full up full-pipeline
```

**What it does:**
1. Combines all traces in `langsmith_traces/`
2. Converts traces to predictions
3. Runs evaluation
4. Checks thresholds
5. Reports pass/fail

---

## Configuration

### Environment Variables

Create `.env` file (or use `.env.example`):

```bash
cp .env.example .env
```

Edit `.env`:
```env
LANGSMITH_API_KEY=lsv2_pt_your_key_here
LANGSMITH_PROJECT=Zen_Project
GEMINI_API_KEY=your_gemini_key_here

# Optional overrides
PREDICTIONS_FILE=predictions_real.json
TRACE_FILE=combined_traces.json
```

---

## Volume Mounts

The containers mount these directories:

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./langsmith_traces/` | `/app/langsmith_traces/` | Input: LangSmith traces |
| `./traces/` | `/app/traces/` | Input: Additional traces |
| `./results/` | `/app/results/` | Output: Evaluation results |
| `./predictions_real.json` | `/app/predictions_real.json` | Predictions file |
| `./test_cases.json` | `/app/test_cases.json` | Test suite |

---

## Advanced Usage

### Run Specific Command Inside Container

```bash
# Run evaluator with custom files
docker compose run --rm zenbot-evaluator \
  python evaluators.py --tests test_cases.json --predictions custom_predictions.json

# Convert traces with custom input
docker compose run --rm trace-converter \
  python scripts/langsmith_to_predictions.py \
    --trace-file /app/traces/new_traces.json \
    --out /app/results/new_predictions.json

# Get a shell inside the container
docker compose run --rm zenbot-evaluator bash
```

### Build with Custom Tags

```bash
docker build -t zenbot-eval:v1.0 .
docker run --rm -v $(pwd)/traces:/app/traces zenbot-eval:v1.0
```

### Run Without Docker Compose

```bash
# Build
docker build -t zenbot-eval .

# Run evaluation
docker run --rm \
  -v $(pwd)/langsmith_traces:/app/langsmith_traces:ro \
  -v $(pwd)/predictions_real.json:/app/predictions_real.json:ro \
  -v $(pwd)/test_cases.json:/app/test_cases.json:ro \
  zenbot-eval python evaluators.py

# Run full pipeline
docker run --rm \
  -v $(pwd)/langsmith_traces:/app/langsmith_traces:ro \
  -v $(pwd)/predictions_real.json:/app/predictions_real.json \
  -v $(pwd)/test_cases.json:/app/test_cases.json:ro \
  -e LANGSMITH_API_KEY=$LANGSMITH_API_KEY \
  -e LANGSMITH_PROJECT=$LANGSMITH_PROJECT \
  zenbot-eval sh docker-entrypoint.sh full
```

---

## CI/CD Integration

### GitHub Actions (Already in `.github/workflows/evaluate.yml`)

The existing workflow can use Docker:

```yaml
jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker compose build
      
      - name: Run evaluation in Docker
        run: docker compose --profile full up full-pipeline
        env:
          LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
          LANGSMITH_PROJECT: Zen_Project
```

### GitLab CI

```yaml
# .gitlab-ci.yml
evaluate:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker compose build
    - docker compose --profile full up full-pipeline
  only:
    - schedules
```

### Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: zenbot-evaluation
spec:
  schedule: "0 6 * * *"  # Daily at 6 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: evaluator
            image: zenbot-eval:latest
            command: ["python", "evaluators.py"]
            volumeMounts:
            - name: traces
              mountPath: /app/traces
            env:
            - name: LANGSMITH_API_KEY
              valueFrom:
                secretKeyRef:
                  name: zenbot-secrets
                  key: langsmith-api-key
          volumes:
          - name: traces
            persistentVolumeClaim:
              claimName: zenbot-traces-pvc
          restartPolicy: OnFailure
```

---

## Troubleshooting

### Issue: "Permission denied" on mounted volumes
```bash
# Fix: Ensure files are readable
chmod -R 755 langsmith_traces/
chmod 644 predictions_real.json test_cases.json
```

### Issue: Container can't find .env
```bash
# The .env file is excluded by .dockerignore (intentionally)
# Pass env vars via docker compose or --env-file

docker compose --env-file .env up zenbot-evaluator
```

### Issue: "No such file: predictions_real.json"
```bash
# First run the converter to generate it
docker compose --profile converter up trace-converter

# Or create an empty one
echo '{}' > predictions_real.json
```

### Issue: Docker build fails on dependencies
```bash
# Clear cache and rebuild
docker compose build --no-cache
```

---

## Production Deployment

### Option 1: Docker Swarm

```bash
# Initialize swarm
docker swarm init

# Create secret for API key
echo "your_key_here" | docker secret create langsmith_api_key -

# Deploy stack
docker stack deploy -c docker compose.yml zenbot
```

### Option 2: AWS ECS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker build -t zenbot-eval .
docker tag zenbot-eval:latest YOUR_ECR_URI/zenbot-eval:latest
docker push YOUR_ECR_URI/zenbot-eval:latest

# Create ECS task definition and schedule it
```

### Option 3: Kubernetes

```bash
# Build and push to registry
docker build -t your-registry/zenbot-eval:v1.0 .
docker push your-registry/zenbot-eval:v1.0

# Apply Kubernetes manifests
kubectl apply -f k8s/
```

---

## Performance & Optimization

### Multi-stage Build (for smaller images)

```dockerfile
# Dockerfile.optimized
FROM python:3.10-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "evaluators.py"]
```

Build: `docker build -f Dockerfile.optimized -t zenbot-eval:slim .`

---

## Monitoring & Logging

### Export logs to file

```bash
docker compose up zenbot-evaluator 2>&1 | tee results/evaluation_$(date +%Y%m%d_%H%M%S).log
```

### Send logs to monitoring service

```bash
# Docker logging driver
docker run --log-driver=json-file --log-opt max-size=10m zenbot-eval
```

---

## Summary: Common Commands

```bash
# Build image
docker compose build

# Run evaluation only
docker compose up zenbot-evaluator

# Run full pipeline
docker compose --profile full up full-pipeline

# Convert traces only
docker compose --profile converter up trace-converter

# Check thresholds only
docker compose --profile ci up ci-checker

# Interactive shell
docker compose run --rm zenbot-evaluator bash

# Clean up
docker compose down
docker system prune -f
```

---

**Your evaluation pipeline is now fully containerized and ready for production! 🚀**
