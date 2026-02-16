# ZenBot - AI-Powered Steel Specifications Assistant

[![CI Evaluation](https://github.com/Brohammad/workspacegmail/actions/workflows/evaluate.yml/badge.svg)](https://github.com/Brohammad/workspacegmail/actions)

**ZenBot** is a production-ready RAG chatbot for ZenithSteel that answers technical questions about steel specifications, pricing, and delivery using Google Gemini (gemini-2.0-flash) and LangSmith for tracing and evaluation.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Google Gemini API key
- LangSmith API key (for tracing)
- Discord webhook URL (for notifications)

### Setup

1. **Clone and activate environment:**
   ```bash
   git clone https://github.com/Brohammad/workspacegmail.git
   cd workspacegmail
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and set:
   # - GEMINI_API_KEY=your_gemini_api_key
   # - LANGSMITH_API_KEY=your_langsmith_key
   # - LANGSMITH_PROJECT=Zen_Project
   ```

3. **Run ZenBot:**
   ```bash
   python zenbot.py
   ```

## 📊 Current Performance

**Latest Metrics** (with 10-document knowledge base):
- ✅ **Spec Accuracy:** 90% (9/10 passing)
- ✅ **Pricing Accuracy:** 100% (10/10 passing)
- ✅ **Hallucination Detection:** 80% (8/10 passing)

**Quality Thresholds:**
- Spec Accuracy ≥ 8%
- Hallucination Detection ≥ 50%

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   ZenBot    │─────▶│ Gemini 2.0   │─────▶│  LangSmith  │
│  (zenbot.py)│      │    Flash     │      │  (Tracing)  │
└─────────────┘      └──────────────┘      └─────────────┘
       │
       ├─▶ Knowledge Base (10 documents)
       │   ├── Current specs (Fe 500, Fe 550D)
       │   ├── Pricing & delivery times
       │   └── Technical standards (IS 1786)
       │
       └─▶ Retrieval Modes:
           ├── Fixed (current docs) ✅
           └── Buggy (outdated docs) ❌
```

## 🔄 CI/CD Pipeline

**Automated daily evaluation** via GitHub Actions:

1. **Generate Predictions:** Run ZenBot on 10 test cases
2. **Evaluate Quality:** Run evaluators (spec, pricing, hallucination)
3. **Check Thresholds:** Pass/fail based on quality gates
4. **Send Alerts:** Email + Discord notifications on failures
5. **Status Updates:** Discord status on every run (pass/fail)

**Workflow:** [`.github/workflows/evaluate.yml`](.github/workflows/evaluate.yml)

**View runs:** https://github.com/Brohammad/workspacegmail/actions

## 📁 Project Structure

```
├── zenbot.py                    # Main chatbot implementation
├── evaluators.py                # Quality evaluators (spec, pricing, hallucination)
├── test_cases.json              # 10 canonical test cases
├── predictions.json             # Latest predictions from ZenBot
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── docker-compose.yml           # Docker deployment config
│
├── scripts/
│   ├── check_results.py         # CI threshold checker + alerting
│   ├── langsmith_to_predictions.py  # Convert traces to predictions
│   └── run_all_tests.py         # Generate predictions from test cases
│
├── .github/workflows/
│   └── evaluate.yml             # Daily CI/CD evaluation workflow
│
├── langsmith_traces/            # LangSmith trace exports (JSON)
└── results/                     # Evaluation results (timestamped)
```

## 🧪 Running Evaluations

### Local Evaluation

```bash
# Run full evaluation pipeline
python evaluators.py

# Check if results pass thresholds
python scripts/check_results.py

# Generate new predictions from traces
python scripts/langsmith_to_predictions.py \
  --tests test_cases.json \
  --trace-file langsmith_traces/your_traces.json \
  --out predictions_new.json
```

### Docker Deployment

```bash
# Build and run
docker-compose up --build

# Run evaluation in container
docker-compose exec zenbot python evaluators.py
```

## 🔔 Alerting & Monitoring

**Email Alerts** (on quality failures):
- Sent to: `raabidmohamed@gmail.com`
- Includes: Failed checks, metrics, GitHub Actions links
- Configured via GitHub Secrets: `EMAIL_SENDER`, `EMAIL_PASSWORD`, `EMAIL_RECIPIENT`

**Discord Notifications** (on every run):
- ✅ **Green status** for passing runs with current metrics
- ❌ **Red alert** for failing runs with detailed breakdown
- Configured via GitHub Secret: `DISCORD_WEBHOOK_URL`

**Test locally:**
```bash
export DISCORD_WEBHOOK_URL="your_webhook_url"
python test_discord.py
```

## 🛠️ Key Features

### RAG Pipeline
- **Retrieval:** Semantic search over knowledge base (10 current documents)
- **Augmentation:** Inject relevant docs into prompt context
- **Generation:** Gemini 2.0 Flash generates grounded answers
- **Validation:** Evaluators check spec accuracy, pricing, hallucinations

### Quality Evaluators

1. **Spec Accuracy Evaluator**
   - Extracts numeric specs from predictions
   - Filters out dates/years to avoid false positives
   - Checks IS 1786 standard citations
   - Fuzzy matching for text-based answers

2. **Pricing Accuracy Evaluator**
   - Validates price ranges and currency
   - Checks for date-specific pricing info
   - Ensures "per metric ton" units mentioned

3. **Hallucination Detector**
   - Flags unsourced guesses ("probably", "maybe", "I think")
   - Rewards uncertainty admission ("verify with team")
   - Checks for confidence with citations ("as per IS 1786")
   - Allows approximations with sources

### Tracing with LangSmith
- All queries traced to LangSmith project: `Zen_Project`
- Local JSON traces saved to `langsmith_traces/`
- Supports buggy vs fixed version comparison
- Trace export for analysis and debugging

## 📈 Improvement Roadmap

**Completed:**
- ✅ Email alerts for quality failures
- ✅ Knowledge base expansion (2 → 10 documents)
- ✅ Improved evaluators (90%/100%/80% accuracy)
- ✅ Discord webhook integration
- ✅ Status messages on every run

**Next Priorities:**
- 🔜 **Expand test cases** (10 → 30+) for better coverage
- 🔜 **Deploy to Kubernetes** for production scalability
- 🔜 **Vector search** (Chroma/Pinecone) for better retrieval
- 🔜 **Metrics dashboard** (track trends over time)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is part of a ZenithSteel case study for Gemini adoption.

## 🔗 Links

- **GitHub Repo:** https://github.com/Brohammad/workspacegmail
- **GitHub Actions:** https://github.com/Brohammad/workspacegmail/actions
- **LangSmith Project:** https://smith.langchain.com/ (Project: Zen_Project)

## 📞 Support

For questions or issues, please open a GitHub issue or contact the team.

---

**Built with:** Google Gemini • LangSmith • LangChain • Python 3.10
