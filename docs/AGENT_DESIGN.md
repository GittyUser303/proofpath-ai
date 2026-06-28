# Agent Design: ProofPath AI

## 1. Agentic Philosophy
ProofPath AI should not behave like a chatbot.

It should behave like an investigator.

Each agent has a narrow role and produces structured outputs that the next agent can use.

## 2. Agents

## 2.1 Case Manager Agent
The orchestrator.

Responsibilities:
- receives user input,
- creates case ID,
- coordinates agents,
- handles retries,
- saves memory,
- decides when the investigation is complete.

Prompt behavior:
- Be cautious.
- Prefer evidence over confidence.
- Never fabricate sources.
- Mark uncertainty clearly.

## 2.2 Claim Extraction Agent
Responsibilities:
- extract main claim,
- split subclaims,
- identify entities,
- classify domain,
- estimate harm/risk.

Example:
Input:
> This viral post says seed oils are toxic and cause heart disease.

Output:
```json
{
  "main_claim": "Seed oils are toxic and cause heart disease.",
  "sub_claims": [
    "Seed oils are toxic",
    "Seed oils cause heart disease"
  ],
  "domain": "health",
  "risk": "medium",
  "entities": ["seed oils", "heart disease"]
}
```

## 2.3 Planner Agent
Responsibilities:
- create investigation plan,
- choose tools,
- decide if TraceBack is needed,
- decide if academic sources are needed,
- decide if more evidence is needed.

Decision rules:
- Health claims require medical/scientific sources.
- Product claims require independent sources.
- Viral claims require TraceBack.
- AI answers require claim decomposition.
- Low confidence requires search retry.

## 2.4 Evidence Retrieval Agent
Responsibilities:
- search for evidence,
- collect supporting sources,
- collect opposing sources,
- collect neutral context,
- prefer primary sources.

Tools:
- Tavily
- DuckDuckGo
- PubMed
- Semantic Scholar
- arXiv

## 2.5 TraceBack Agent
This is the key integration from TraceBack AI.

Responsibilities:
- search for earlier appearances,
- find repeated wording,
- detect claim mutation,
- identify source chains,
- generate timeline.

It should not claim the absolute origin unless evidence is strong. Use wording like:
- "earliest accessible source found"
- "likely repeated from"
- "appears to have spread through"

## 2.6 Source Quality Agent
Responsibilities:
- score credibility,
- classify source type,
- detect sensationalism,
- detect primary vs secondary evidence,
- detect citation quality.

Source categories:
- primary research,
- systematic review,
- government/regulatory,
- official organization,
- expert institution,
- news article,
- blog,
- forum,
- social media,
- marketing page.

## 2.7 Contradiction Agent
Responsibilities:
- compare sources,
- identify disagreement,
- identify outdated claims,
- identify exaggeration,
- flag weak evidence.

Output:
```json
{
  "contradictions": [
    {
      "claim": "X increases testosterone by 300%",
      "conflict": "Independent studies show no significant effect.",
      "severity": "high"
    }
  ]
}
```

## 2.8 Reasoning Agent
Responsibilities:
- combine evidence,
- explain support and opposition,
- avoid overclaiming,
- generate final verdict.

Verdict labels:
- Supported
- Mostly Supported
- Mixed Evidence
- Unsupported
- Misleading
- False
- Not Enough Evidence

## 2.9 Confidence Agent
Responsibilities:
- assign score from 0 to 100,
- explain score,
- show what would improve confidence.

Factors:
- source quality,
- evidence agreement,
- primary evidence,
- date relevance,
- contradiction level,
- traceback clarity.

## 2.10 Report Agent
Responsibilities:
- generate readable report,
- include evidence table,
- include timeline,
- include confidence,
- include limitations,
- export to Markdown/PDF.

## 3. Agent State

```python
class InvestigationState(TypedDict):
    case_id: str
    user_id: str
    raw_input: str
    extracted_claims: list
    plan: dict
    evidence: list
    traceback_timeline: list
    source_scores: list
    contradictions: list
    verdict: str
    confidence: float
    report_path: str
```

## 4. Human-Readable Agent Activity
The frontend should display:

- Extracting claim...
- Planning investigation...
- Searching primary sources...
- Tracing earlier appearances...
- Scoring source quality...
- Detecting contradictions...
- Building verdict...
- Saving memory...
- Generating report...

## 5. Safety Rules
Agents must:
- not fabricate sources,
- not hide uncertainty,
- not present medical/legal/financial advice as final authority,
- cite source URLs,
- use cautious wording for origin tracing,
- show limitations.
