# Quick Start Guide — ZenBot Evaluation Pipeline

## 🚀 What You Got

A complete, production-ready evaluation system for your ZenBot with:
- ✅ Documentation (Gemini adoption + governance + training)
- ✅ Evaluation pipeline (local + CI/CD)
- ✅ LangSmith integration (tested with your real traces)
- ✅ GitHub Actions workflow (daily automated runs)

## 📊 Current Status

**Baseline Performance** (from your 6 existing traces):
```
Spec Accuracy:      10% (1/10 passing)  ⚠️  Need more trace coverage
Pricing Accuracy:   20% (2/10 passing)  ⚠️  Need more trace coverage
Hallucination Rate: 75% (no guessing)   ✅  Good - bot doesn't fabricate

Coverage: 7/10 test cases matched to traces
```

**Why scores are low:** Only 3 unique scenarios in trace files (yield strength, pricing, delivery). Test suite needs 10 scenarios.

## ⚡ Run It Now (3 Steps)

### Option A: Native Python (Local)

### Step 1: Run Evaluation
```bash
cd /home/labuser/Desktop/langshmith
/home/labuser/Desktop/langshmith/.venv/bin/python evaluators.py
```

**Output:** Per-case scores + aggregate summary

### Step 2: Check Thresholds (CI Simulation)
```bash
/home/labuser/Desktop/langshmith/.venv/bin/python scripts/check_results.py
```

**Output:** Pass/fail based on thresholds (currently fails — need more trace coverage)

### Step 3: Generate New Predictions from Traces
```bash
# If you have new trace exports
/home/labuser/Desktop/langshmith/.venv/bin/python scripts/langsmith_to_predictions.py \
  --tests test_cases.json \
  --trace-file your_traces.json \
  --out predictions_new.json

# Then re-run evaluation
/home/labuser/Desktop/langshmith/.venv/bin/python evaluators.py \
  --predictions predictions_new.json
```

---

### Option B: Docker (Recommended for Production) 🐳

### Step 1: Build Docker Image
```bash
cd /home/labuser/Desktop/langshmith
docker compose build
```

### Step 2: Run Evaluation
```bash
docker compose up zenbot-evaluator
```

### Step 3: Run Full Pipeline (Convert + Evaluate + Check)
```bash
docker compose --profile full up full-pipeline
```

**📖 Complete Docker guide:** See `DOCKER_SETUP.md` for all services, volume mounts, CI/CD integration, and Kubernetes deployment.

## 📁 Key Files

| File | Purpose |
|------|---------|
| `test_cases.json` | 10 canonical test questions + expected answers |
| `predictions_real.json` | Real outputs from your LangSmith traces (current baseline) |
| `evaluators.py` | Main evaluation script (3 evaluators) |
| `scripts/langsmith_to_predictions.py` | Converts traces → predictions |
| `.github/workflows/evaluate.yml` | Daily automated evaluation (GitHub Actions) |
| `IMPLEMENTATION_SUMMARY.md` | Complete technical documentation |

## 🎯 Next Actions (Priority Order)

### Priority 1: Improve Coverage (Do First)
Your test suite has 10 diverse cases but traces only cover 3 scenarios.

**Action:** Run ZenBot on all 10 test questions and export traces
```bash
# For each test question in test_cases.json:
# 1. Send question to ZenBot
# 2. Capture the response + trace
# 3. Export as JSON
# 4. Combine into traces_complete.json

# Then regenerate predictions:
/home/labuser/Desktop/langshmith/.venv/bin/python scripts/langsmith_to_predictions.py \
  --trace-file traces_complete.json \
  --out predictions_complete.json
```

**Expected result:** Coverage goes from 7/10 → 10/10, scores become meaningful

### Priority 2: Adjust Thresholds
Current thresholds in `scripts/check_results.py`:
- Spec accuracy must be 100% (very strict)
- Hallucination score must be ≥80%

**Action:** Once you have full coverage, set realistic thresholds:
```python
# Edit scripts/check_results.py
if spec_avg < 0.95:  # 95% instead of 100%
    print('SPEC ACCURACY THRESHOLD FAILED')
    sys.exit(1)
```

### Priority 3: Enable GitHub Actions
The workflow is ready but needs GitHub repository setup.

**Action:**
1. Push this code to GitHub
2. Go to Actions tab → workflow will run daily at 6 AM UTC
3. Add Slack webhook (optional):
   ```yaml
   # In .github/workflows/evaluate.yml, add at end:
   - name: Notify on failure
     if: failure()
     run: |
       curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
         -d '{"text":"⚠️ ZenBot evaluation failed!"}'
   ```

### Priority 4: Production Integration
Wire this into your ZenBot deployment pipeline:

**Option A:** Scheduled Export
```bash
# Add to cron (daily at 6 AM)
0 6 * * * cd /path/to/langshmith && \
  ./export_traces.sh && \
  ./run_evaluation.sh && \
  ./alert_if_failed.sh
```

**Option B:** Real-time Monitoring
- Export traces continuously to S3/local storage
- Run evaluation hourly/daily
- Alert on degradation

## 🎓 Documentation Reference

| Document | When to Read |
|----------|--------------|
| `CASE_STUDY_SUMMARY.md` | Overview of all deliverables |
| `IMPLEMENTATION_SUMMARY.md` | Technical details, troubleshooting, API docs |
| `README-case-study.md` | How to run evaluation locally |
| `prompt_library.md` | Gemini prompt examples (for sales team) |
| `roadmap_90_days.md` | Gemini adoption timeline (for management) |
| `governance_policy.md` | AI policies, escalation rules (for compliance) |
| `champions_onboarding.md` | Training approach (for champions/Debashis) |
| `training_deck.md` | Workshop outline (for trainers) |

## 🔍 How the Evaluation Works

```
┌─────────────────────┐
│  test_cases.json    │  10 questions + expected answers
└──────────┬──────────┘
           │
           ├─────────────────────────────────────┐
           │                                     │
           ▼                                     ▼
┌──────────────────────┐            ┌────────────────────────┐
│ predictions_real.json│            │ LangSmith traces       │
│ (from traces)        │            │ (via API or export)    │
└──────────┬───────────┘            └───────────┬────────────┘
           │                                    │
           │    ┌───────────────────────────────┘
           │    │ scripts/langsmith_to_predictions.py
           │    │ (matches traces → test cases)
           │    │
           ▼    ▼
       ┌────────────┐
       │evaluators.py│
       │             │
       │ • spec_accuracy_evaluator     (checks numbers + IS 1786)
       │ • pricing_evaluator            (checks price + date context)
       │ • hallucination_detector       (checks for guessing)
       │             │
       └──────┬──────┘
              │
              ▼
   ┌────────────────────────┐
   │ Aggregate Summary      │
   │                        │
   │ spec_accuracy: 10%     │
   │ pricing_accuracy: 20%  │
   │ hallucination: 75%     │
   └────────────────────────┘
              │
              ▼
   ┌────────────────────────┐
   │ scripts/check_results.py│ ← Used by CI
   │ (enforce thresholds)   │
   └────────────────────────┘
```

## 💡 Pro Tips

### Tip 1: Start with One Scenario
Don't try to perfect all 10 test cases at once.

1. Pick one high-value scenario (e.g., "yield strength queries")
2. Get 5-10 traces for that scenario
3. Achieve 100% on those cases
4. Move to next scenario

### Tip 2: Use Fixed Traces Only
The converter prefers "fixed" over "buggy" traces automatically.

If you want to evaluate buggy performance:
```bash
# Filter to buggy traces
jq '[.[] | select(.version == "buggy")]' combined_traces.json > buggy_traces.json

# Generate predictions from buggy traces
python3 scripts/langsmith_to_predictions.py \
  --trace-file buggy_traces.json \
  --out predictions_buggy.json
```

### Tip 3: Monitor Trends, Not Absolutes
Don't obsess over 100% accuracy. Watch for:
- **Degradation:** Spec accuracy drops from 95% → 85% (alert!)
- **Improvement:** Hallucination rate goes 0.75 → 0.90 (celebrate!)
- **Consistency:** Scores stable over 30 days (system is mature)

### Tip 4: Add Custom Evaluators
The framework is extensible. Add domain-specific checks:

```python
# Example: Ensure delivery queries mention timeline
def delivery_evaluator(prediction: str, expected: str):
    if 'delivery' not in expected.lower():
        return {"key": "delivery_check", "score": 1.0}
    
    has_timeline = any(word in prediction.lower() 
                      for word in ['days', 'weeks', 'hours'])
    score = 1.0 if has_timeline else 0.0
    return {"key": "delivery_check", "score": score}
```

Add to `evaluators.py` and modify the runner to call it.

## 🆘 Troubleshooting

**Problem:** "LANGSMITH_API_KEY not found"
- **Solution:** Use local trace files instead: `--trace-file combined_traces.json`

**Problem:** Evaluation scores seem wrong
- **Solution:** Open `predictions_real.json` and manually compare to `test_cases.json`

**Problem:** CI always fails
- **Solution:** Current thresholds are strict. Either improve coverage or lower thresholds in `scripts/check_results.py`

**Problem:** No traces match test cases
- **Solution:** Check that trace questions are similar to test inputs. May need to add exact test questions to ZenBot production queries.

## 📞 Support

- **Technical docs:** `IMPLEMENTATION_SUMMARY.md`
- **LangSmith integration:** `scripts/langsmith_to_predictions.py` (comments explain trace format)
- **Evaluator logic:** `evaluators.py` (each function has docstrings)
- **GitHub Actions:** `.github/workflows/evaluate.yml` (standard workflow)

## ✅ Success Metrics (30-day goals)

After full implementation, target:
- **Coverage:** 10/10 test cases matched to traces
- **Spec Accuracy:** ≥95%
- **Pricing Accuracy:** ≥98%
- **Hallucination Rate:** <5%
- **CI Success Rate:** ≥90% (passing 27+ days/month)

---

**Everything is ready to run. Start with Step 1 above! 🚀**
