# 🐳 Docker Architecture Overview

## Container Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         Host System                            │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              docker-compose.yml                          │ │
│  │  (Orchestration Layer)                                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                          │                                     │
│        ┌─────────────────┼─────────────────┬─────────────┐   │
│        │                 │                 │             │   │
│   ┌────▼─────┐   ┌──────▼──────┐   ┌─────▼─────┐  ┌────▼───┐│
│   │evaluator │   │trace-       │   │ci-checker │  │full-   ││
│   │          │   │converter    │   │           │  │pipeline││
│   └────┬─────┘   └──────┬──────┘   └─────┬─────┘  └────┬───┘│
│        │                 │                 │             │   │
│   ┌────▼─────────────────▼─────────────────▼─────────────▼───┐│
│   │                 Docker Image                            ││
│   │          (zenbot-eval:latest)                           ││
│   │  ┌────────────────────────────────────────────┐        ││
│   │  │ Python 3.10 + Dependencies                 │        ││
│   │  │  • requests                                 │        ││
│   │  │  • langsmith                                │        ││
│   │  │  • langchain                                │        ││
│   │  │  • python-dotenv                            │        ││
│   │  └────────────────────────────────────────────┘        ││
│   │  ┌────────────────────────────────────────────┐        ││
│   │  │ Application Code                            │        ││
│   │  │  • evaluators.py                            │        ││
│   │  │  • scripts/langsmith_to_predictions.py     │        ││
│   │  │  • scripts/check_results.py                 │        ││
│   │  │  • docker-entrypoint.sh                     │        ││
│   │  └────────────────────────────────────────────┘        ││
│   └────────────────────────────────────────────────────────┘│
│                          │                                     │
│                     Volume Mounts                              │
│                          │                                     │
│   ┌──────────────────────┼──────────────────────────────┐    │
│   │                      │                              │    │
│   ▼                      ▼                              ▼    │
│ langsmith_traces/    test_cases.json       predictions_real. │
│ (read-only)          (read-only)           json              │
└────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌────────────────────┐
│  LangSmith Traces  │  (6 JSON files in langsmith_traces/)
│  • Fixed (3)       │
│  • Buggy (3)       │
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│  Service: trace-converter                               │
│  Container: zenbot-trace-converter                      │
│  ┌────────────────────────────────────────────────┐    │
│  │ scripts/langsmith_to_predictions.py            │    │
│  │  1. Load traces from volume                    │    │
│  │  2. Match to test_cases.json                   │    │
│  │  3. Extract question/answer pairs              │    │
│  │  4. Prefer "fixed" over "buggy"                │    │
│  └────────────────────────────────────────────────┘    │
└─────────┬───────────────────────────────────────────────┘
          │
          ▼
┌────────────────────┐
│ predictions_real.  │  (Generated JSON mapping test_id → output)
│ json               │
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│  Service: zenbot-evaluator                              │
│  Container: zenbot-evaluation                           │
│  ┌────────────────────────────────────────────────┐    │
│  │ evaluators.py                                  │    │
│  │  1. Load test_cases.json & predictions        │    │
│  │  2. Run 3 evaluators:                         │    │
│  │     • spec_accuracy_evaluator                 │    │
│  │     • pricing_evaluator                       │    │
│  │     • hallucination_detector                  │    │
│  │  3. Compute aggregate scores                  │    │
│  │  4. Print results                             │    │
│  └────────────────────────────────────────────────┘    │
└─────────┬───────────────────────────────────────────────┘
          │
          ▼
┌────────────────────┐
│  Evaluation        │  • Per-case scores
│  Results           │  • Aggregate summary
│  (stdout)          │  • Pass/fail status
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────┐
│  Service: ci-checker                                    │
│  Container: zenbot-ci-checker                           │
│  ┌────────────────────────────────────────────────┐    │
│  │ scripts/check_results.py                       │    │
│  │  1. Load predictions & compute scores          │    │
│  │  2. Check thresholds:                          │    │
│  │     • spec_accuracy >= 100%                    │    │
│  │     • hallucination >= 80%                     │    │
│  │  3. Exit 0 (pass) or 1 (fail)                 │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Service Comparison

| Service | Command | Input | Output | Use Case |
|---------|---------|-------|--------|----------|
| **evaluator** | `docker-compose up zenbot-evaluator` | predictions_real.json | Scores + summary | Daily monitoring |
| **trace-converter** | `docker-compose --profile converter up` | traces/*.json | predictions_real.json | After trace export |
| **ci-checker** | `docker-compose --profile ci up` | predictions_real.json | Exit code (0/1) | CI/CD pipelines |
| **full-pipeline** | `docker-compose --profile full up` | traces/*.json | Scores + pass/fail | Complete workflow |

## Volume Mount Strategy

```
Host                          Container               Mode
────────────────────────────  ──────────────────────  ────
./langsmith_traces/       →   /app/langsmith_traces/  ro (read-only)
./traces/                 →   /app/traces/            ro
./test_cases.json         →   /app/test_cases.json    ro
./predictions_real.json   →   /app/predictions_real.  rw (read-write)
                              json
./results/                →   /app/results/           rw
.env                      →   (env vars loaded)       -
```

**Why this approach?**
- **Read-only mounts:** Prevents containers from accidentally modifying input data
- **Read-write for predictions:** Allows trace-converter to update the file
- **Results directory:** Separate output location for logs, reports, artifacts

## Environment Variable Flow

```
.env file (on host)
    │
    ├─ LANGSMITH_API_KEY=lsv2_pt_...
    ├─ LANGSMITH_PROJECT=Zen_Project
    └─ GEMINI_API_KEY=...
         │
         ▼
docker-compose.yml (loads .env)
         │
         ├─► Container 1: zenbot-evaluator
         ├─► Container 2: trace-converter
         ├─► Container 3: ci-checker
         └─► Container 4: full-pipeline
              │
              ▼
         Python scripts access via os.environ
```

## CI/CD Integration Patterns

### Pattern 1: GitHub Actions

```yaml
# .github/workflows/evaluate.yml
- name: Build Docker image
  run: docker-compose build

- name: Run full pipeline
  run: docker-compose --profile full up full-pipeline
  env:
    LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
```

### Pattern 2: GitLab CI

```yaml
# .gitlab-ci.yml
evaluate:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker-compose build
    - docker-compose --profile full up full-pipeline
```

### Pattern 3: Kubernetes CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: zenbot-eval
spec:
  schedule: "0 6 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: evaluator
            image: zenbot-eval:latest
            command: ["python", "evaluators.py"]
```

## Deployment Scenarios

### Scenario 1: Local Development
```bash
# Build once
docker-compose build

# Run evaluation after changes
docker-compose up zenbot-evaluator

# Interactive debugging
docker-compose run --rm zenbot-evaluator bash
```

### Scenario 2: Automated CI/CD
```bash
# Scheduled pipeline (cron or GitHub Actions)
docker-compose --profile full up full-pipeline

# Exit code determines build status
# 0 = pass, 1 = fail
```

### Scenario 3: Production Monitoring
```bash
# Daily scheduled job exports traces, runs evaluation
0 6 * * * cd /opt/zenbot && \
  ./export_traces.sh && \
  docker-compose --profile full up full-pipeline && \
  ./send_results_to_slack.sh
```

### Scenario 4: Cloud Deployment (AWS ECS)
```bash
# Build and push
docker build -t 123456789.dkr.ecr.us-east-1.amazonaws.com/zenbot-eval .
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/zenbot-eval

# ECS scheduled task runs daily
# Pulls latest image, runs full-pipeline, sends results to CloudWatch
```

## Resource Requirements

| Component | CPU | Memory | Disk | Notes |
|-----------|-----|--------|------|-------|
| **Docker Image** | - | - | ~500 MB | Python 3.10 + deps |
| **Running Container** | 0.1-0.5 CPU | 128-256 MB | - | Lightweight evaluation |
| **Volume Data** | - | - | ~10 MB | Traces + predictions |

**Scaling:**
- Single container sufficient for <1000 test cases
- For parallel evaluation: run multiple containers with sharded test sets
- For high-frequency monitoring: use Kubernetes with HPA (Horizontal Pod Autoscaler)

---

**This Docker setup is production-ready and scalable! 🚀**
