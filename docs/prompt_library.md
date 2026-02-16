# Prompt Library — Gemini & ZenBot (examples and templates)

This file collects the concrete prompts used in the case study. Copy-and-use these prompts in Gemini (Workspace) or adapt for your assistant.

1) Follow-up Email (detailed prompt — good):

```
Write a professional follow-up email to Rajesh Sinha, Procurement Head at Eastern Infra Pvt. Ltd.
Context: I'm Ananya from ZenithSteel. We met at the Kolkata Steel Trade Show last Thursday where we discussed TMT bars for his upcoming highway project in Jharkhand. He expressed interest in quality certifications and delivery timelines.

He requested pricing for 500 MT delivered to Ranchi. Our current rate is ₹52,500 per MT for TMT 12mm Fe 550D grade. Delivery to Ranchi takes 5-7 business days.

Tone: Warm but professional. Reference our conversation about meeting deadlines on the project. Suggest a call next Tuesday to discuss specifications in detail.

Include: Pricing breakdown, delivery timeline, quality certifications available, and clear next steps.
```

2) Follow-up Email (short form — for quick drafts):

```
Draft a short follow-up email to Rajesh Sinha confirming pricing and delivery for 500 MT of TMT 12mm Fe 550D, quoting ₹52,500/MT and 5-7 business days delivery to Ranchi. Keep it warm and end with a call suggestion for next Tuesday.
```

3) Sheets Analysis Prompt (for Gemini in Sheets / Copilot):

```
Analyze this Q3 sales data and provide the top 3 actionable insights for our Sales Director. Focus on:
1) Average revenue per sales rep by region
2) Product category trends (winning vs losing)
3) Deal conversion patterns by rep/region
4) Client concentration risk
5) Pipeline health (deal status distribution)

Return each insight with a specific recommended action. Format as:
- Insight #1: [Finding] — Action: [Recommended next step]
```

4) Spec-check Guardrail Prompt (demand citations):

```
Provide the yield strength and tensile strength for Fe 550D 16mm and cite the authoritative document and page number where you found it. If you can't find a verified source, say "I could not find a confirmed source; please verify with technical documentation." Do not guess.
```

5) Hallucination-safe Prompt (for safety-critical answers):

```
Answer only using the documents attached (list them). If the document doesn't contain the answer, reply: "I couldn't find a definitive answer in the provided documents. Please consult the technical team." Include source citations and page numbers for any numeric specification.
```

6) Prompting Tips (short):
- Provide role and context (who you are, what the recipient cares about)
- Provide explicit numbers and constraints
- Ask for citations for technical data
- Ask for clear next steps and CTA (call, meeting, confirm specs)

Use these prompts as a starting point and store good variations in your team prompt library for reuse.
