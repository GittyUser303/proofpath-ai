# UI/UX Specification: ProofPath AI

## 1. Product Feel
ProofPath AI should not look like a normal chatbot.

It should feel like an investigation cockpit.

Keywords:
- evidence,
- provenance,
- confidence,
- timeline,
- reasoning,
- transparency.

## 2. Layout

```text
┌─────────────────────┬───────────────────────────────┬──────────────────────┐
│ Investigation Panel │ Main Workspace                │ Evidence Locker      │
│                     │                               │                      │
│ Current Step        │ Claim Input / Chat            │ Sources              │
│ Agent Status        │ Verdict                       │ TraceBack Timeline   │
│ Tool Calls          │ Reasoning Graph               │ Contradictions       │
│ Confidence          │ Report Preview                │ Memory               │
└─────────────────────┴───────────────────────────────┴──────────────────────┘
```

## 3. Core Screens

## 3.1 Landing Screen
Content:
- headline,
- claim input box,
- upload button,
- example claims.

Headline:
> Trust evidence, not vibes.

Subheadline:
> ProofPath AI verifies claims by tracing origins, checking evidence, detecting contradictions, and producing transparent confidence scores.

Example cards:
- Verify a health claim
- Check a product claim
- Trace a viral rumor
- Audit an AI-generated answer

## 3.2 Investigation Screen

### Left Panel: Agent Activity
Shows:
- Extracting claim
- Planning investigation
- Searching sources
- Tracing origin
- Scoring reliability
- Detecting contradictions
- Generating verdict

Use progress chips:
- Pending
- Running
- Done
- Needs Retry

### Center Panel: Main Result
Contains:
- extracted claim,
- investigation plan,
- final verdict,
- confidence meter,
- reasoning summary,
- report download.

### Right Panel: Evidence Locker
Contains:
- source cards,
- quality scores,
- stance labels,
- timeline events,
- contradictions,
- related previous investigations.

## 4. Visual Features

## 4.1 Confidence Meter
Show:
- score from 0 to 100,
- label,
- reason.

Labels:
- 0–30: Very uncertain
- 31–50: Weak evidence
- 51–70: Mixed evidence
- 71–85: Strong evidence
- 86–100: Very strong evidence

## 4.2 TraceBack Timeline
Timeline item:
```text
2018 — Blog post repeats claim without source
2020 — Wellness page exaggerates claim
2023 — Viral social post removes context
2026 — User submits current version
```

## 4.3 Evidence Cards
Each card:
- title,
- URL,
- source type,
- stance,
- quality score,
- useful snippet.

## 4.4 Contradiction Map
Show:
- claim part,
- source A,
- source B,
- contradiction.

## 5. Design Style

### Light Mode
- Warm off-white background
- Soft cards
- Subtle borders
- Trustworthy blue/green accents

### Dark Mode
- Near-black background
- Neon evidence trails
- Glass panels
- Purple/cyan highlights
- Framer-like premium feel

## 6. Streamlit MVP Layout
Use:
- `st.sidebar` for agent activity,
- main area for verdict,
- right-like section using columns,
- expandable cards for sources,
- progress bar for confidence.

## 7. Next.js Portfolio Layout
Use:
- shadcn/ui cards,
- React Flow for reasoning graph,
- Framer Motion for transitions,
- command palette,
- persistent case sidebar.

## 8. Microcopy
Use strong product language:

- "Building evidence trail..."
- "Tracing claim origin..."
- "Checking source quality..."
- "Contradiction detected."
- "Confidence reduced due to weak primary evidence."
- "Verdict earned, not guessed."

## 9. Demo-Friendly UI Requirements
The app must visibly show:
- tool calls,
- planning,
- evidence collection,
- timeline,
- final confidence,
- memory.

This ensures judges understand it is agentic.
