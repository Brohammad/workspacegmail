# Governance & Policy (Gemini + ZenBot)

This document summarizes the governance rules recommended in the case study (concise actionable items).

1) Human-in-the-loop policies (Gemini)
- "Edit Before Send" — All AI-drafted emails must be reviewed and edited by the rep. The rep owns what is sent.
- Technical specs and pricing extracted from AI must be verified against authoritative documents and signed off by technical/QC or pricing teams before being shared with customers.

2) ZenBot (Autonomous assistant) rules
- Confidence threshold: If answer confidence < 80% or required sources missing -> auto-route to human.
- Critical topics (pricing, specs, legal, safety) -> always show source citations and route to human if not found.

3) Monitoring & Alerts
- Hallucination rate > 5% in a 6-hour window -> Issue P1 alert and start trace analysis.
- Document freshness: Pricing docs >7 days old -> alert to Pricing team.
- P95 latency > 5s -> alert to infra team.

4) Embedding & Data Freshness
- All pricing/spec documents must be re-embedded within 24 hours of upload.
- Monitor embedding pipeline; alert on failures older than 48 hours.

5) Escalation matrix (summary)
- P0 (Wrong spec sent to client / safety issue): Immediate notification to CTO, Legal, Sales Director and client-contact; investigate 1 hour.
- P1 (Wrong pricing > ₹50K impact): Notify Sales Director + Finance within 1 hour.
- P2 (Hallucination caught before client): Product team investigates within 4 hours.

6) Audit & Retention
- Store all AI interactions (input, context, sources) for 90 days for auditability.

7) Data Privacy
- No PII in prompts for public tools. Use Workspace Gemini with enterprise controls for sensitive data. Redact sensitive data before external model calls if needed.
