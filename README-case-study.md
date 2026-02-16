# Case Study Artifacts — How to run the local evaluation

What this provides:

- `evaluators.py` — local evaluation harness implementing the evaluators in the case study
- `test_cases.json` — canonical test cases (10 cases)
- `predictions.json` — sample predictions (identical to expected answers so evaluator will run and show passing scores)
- Other docs: prompt library, roadmap, governance, champions onboarding

Run the evaluator locally

1) Ensure you have Python 3.8+ installed.
2) From the repository root run:

```bash
python3 evaluators.py --tests test_cases.json --predictions predictions.json
```

The script prints per-case scores and an aggregate summary for the three evaluators.

Replace `predictions.json` with a real outputs file from ZenBot (map of test-case id to model output) to evaluate the real system.

Notes on keys and external systems
- The repository `.env` contains a placeholder `GEMINI_API_KEY=your_gemini_api_key_here`. Populate it only if you plan to run code that calls Gemini or other APIs.
- This deliverable does NOT call LangSmith or Gemini; it provides evaluation scaffolding and governance docs to integrate with LangSmith and other production tooling.

Next integration steps (suggested):

1. Export ZenBot outputs from logs or LangSmith traces into `predictions.json`.
2. Run the evaluator daily in a scheduled job and alert if aggregate accuracy drops.
3. Use LangSmith traces to map failing test cases back to specific retrieval steps and documents.
