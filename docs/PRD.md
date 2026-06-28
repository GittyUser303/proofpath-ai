# Product Requirements Document: ProofPath AI

## 1. Product Vision
ProofPath AI helps users verify claims by constructing a transparent evidence trail before giving a verdict.

The updated product integrates TraceBack AI-style provenance tracing. It does not only ask whether a claim is true. It investigates where the claim came from, how it spread, whether it mutated, and what evidence exists.

## 2. Problem Statement
AI-generated content, misinformation, exaggerated marketing, health myths, viral statistics, and fake expert claims are spreading faster than people can verify them.

Current tools usually do one of two things:

1. Summarize search results.
2. Give a confident answer without showing how it reached that answer.

ProofPath AI solves this by creating a structured investigation workflow.

## 3. Target Users
- Students
- Researchers
- Journalists
- Content creators
- Developers
- Health-conscious users
- Startup founders validating product claims
- People verifying viral claims before sharing them

## 4. Core User Stories

### Claim Verification
As a user, I want to enter a claim so that the agent can verify it using reliable sources.

### Screenshot Verification
As a user, I want to upload a screenshot so that the agent can extract claims from it.

### Trace Origin
As a user, I want to know where a claim may have originated so that I understand its credibility.

### Detect Mutation
As a user, I want to see how a claim changed across sources so that I can spot exaggeration.

### Confidence Score
As a user, I want a confidence score so that I know how strongly to trust the final verdict.

### Evidence Report
As a user, I want a downloadable report so that I can share the investigation.

### Memory
As a returning user, I want the system to remember previous investigations so that I can continue or compare related claims.

## 5. MVP Features

| Feature | Priority | Description |
|---|---|---|
| Claim Input | P0 | User enters a claim manually |
| Claim Extraction | P0 | Extracts claims from long text |
| Planner Agent | P0 | Creates investigation plan |
| Web Search Tool | P0 | Searches web for sources |
| Source Quality Scoring | P0 | Scores sources by credibility |
| TraceBack Timeline | P0 | Shows earliest/repeated appearances found |
| Contradiction Detection | P0 | Finds support vs opposition |
| Confidence Score | P0 | Calculates final confidence |
| Case Memory | P0 | Stores past investigations |
| Final Report | P0 | Produces structured report |
| OCR Upload | P1 | Extracts claims from screenshots |
| PDF Upload | P1 | Extracts claims from PDFs |
| Knowledge Graph | P2 | Links recurring claims and sources |
| Social Spread Map | P2 | Visualizes claim propagation |

## 6. Non-Goals for MVP
- No legal advice
- No real-time Twitter/X scraping
- No guaranteed first-ever source discovery
- No automated posting or reporting
- No production-grade fact-checking certification
- No medical diagnosis

## 7. Success Criteria
The project is successful if the demo clearly shows:

- LLM usage
- at least two tools
- autonomous planning
- persistent memory
- multi-step workflow
- decision-making
- source ranking
- traceability
- polished frontend
- final answer with evidence, not blind generation

## 8. Key Differentiator
Most AI projects answer.

ProofPath AI investigates.

The TraceBack integration makes the project stand out because it adds digital provenance:

- origin tracing,
- mutation tracking,
- repeated-source detection,
- and evidence chain construction.

## 9. Example MVP Scenario

Input:

> Drinking cold water after meals causes cancer.

Output:

- Extracted claim: Cold water after meals causes cancer.
- Claim type: Health misinformation.
- Investigation plan:
  1. Search medical authorities.
  2. Search scientific literature.
  3. Search web for early appearances.
  4. Compare claim variants.
  5. Generate verdict.
- Evidence:
  - WHO/NCI/Mayo-style sources found no support.
  - Blog posts repeat claim without citations.
  - Earliest accessible appearances are low-quality chain-message style posts.
- Verdict:
  - Unsupported.
- Confidence:
  - High.
- TraceBack:
  - Appears to spread through wellness blogs and social reposts, not primary medical research.

## 10. User Experience Goals
- Should feel like an investigation dashboard.
- Should visually show the agent doing work.
- Should not look like a normal chatbot.
- Should make the evidence trail obvious.
- Should be demo-friendly in under 5 minutes.

## 11. Risks
- Search results may be incomplete.
- Source origin may not be exact.
- LLM may overstate confidence.
- Some claims require expert interpretation.
- Medical/legal claims need disclaimers.

## 12. Ethical Boundaries
ProofPath must state:

- It is an evidence assistant, not a final authority.
- It does not replace doctors, lawyers, regulators, or professional fact-checkers.
- It shows sources and uncertainty.
- It avoids making unsupported claims.
