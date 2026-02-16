# Case Study: Gemini (Productivity Layer) & LangSmith (AI Ops for ZenBot)

This repository contains the artifacts for the combined case study solution requested.

Overview of what's included:

- Part A — Gemini: adoption strategy, prompts, 90-day roadmap, champion onboarding, and governance
- Part B — LangSmith: debugging/monitoring approach, evaluation strategy, test dataset, and evaluators for ZenBot

Files added by this deliverable:

- `prompt_library.md` — curated prompts and examples (follow-up email, Sheets analysis, spec-check guardrails)
- `evaluators.py` — Python evaluators and a small runner to compute scores on model outputs
- `test_cases.json` — canonical test dataset (10+ cases) referenced by the evaluation strategy
- `predictions.json` — sample predictions (matching expected answers) so you can run the evaluator immediately
- `roadmap_90_days.md` — 90-day adoption roadmap (phases, success metrics)
- `governance_policy.md` — human-in-loop policies, escalation matrix, monitoring metrics
- `champions_onboarding.md` — onboarding playbook for champion users including the Debashis strategy
- `README-case-study.md` — how to run the evaluation and next steps

Notes and assumptions:

- These artifacts are scaffolding: they do not call external APIs (Gemini, LangSmith) — doing so requires credentials and live network access. The repository's `.env` currently contains a placeholder for `GEMINI_API_KEY`; update it before attempting any live API calls.
- The evaluation runner expects a `predictions.json` file containing model outputs for each test case. A sample `predictions.json` is included.

Suggested next steps:

1. Replace `predictions.json` with actual ZenBot outputs (from logs or LangSmith traces) and run `evaluators.py` to measure performance.
2. Wire LangSmith traces into a scheduler to run the evaluation daily and alert on regressions.
3. Add a monitoring job to check document freshness and embedding pipeline health (see `governance_policy.md`).

---

This summary is intentionally concise; detailed content is available in the other files.
