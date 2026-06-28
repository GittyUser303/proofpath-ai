# Task Breakdown

## Milestone 1: Project Setup
- Create repo
- Create virtual environment
- Add requirements
- Add `.env.example`
- Create folder structure
- Set up LLM provider

## Milestone 2: UI Shell
- Build landing screen
- Add claim input
- Add submit button
- Add sidebar for agent activity
- Add placeholder evidence locker
- Add past cases panel

## Milestone 3: Claim Extraction
- Create claim extraction prompt
- Return structured JSON
- Show extracted claim in UI
- Handle long text

## Milestone 4: Planner
- Build planner prompt
- Choose tools based on claim type
- Display investigation plan
- Add routing logic

## Milestone 5: Tool Layer
- Build web search tool
- Build traceback search tool
- Build source scoring tool
- Build confidence calculator
- Build report generator

## Milestone 6: Evidence Retrieval
- Run search queries
- Parse results
- Remove duplicate URLs
- Classify source stance
- Store source metadata

## Milestone 7: TraceBack
- Generate claim variants
- Search exact phrase
- Search older wording
- Build timeline
- Detect repeated wording
- Show timeline in UI

## Milestone 8: Contradiction Detection
- Compare source stances
- Identify support/refute/mixed
- Generate contradiction table
- Lower confidence if contradictions are severe

## Milestone 9: Verdict + Confidence
- Generate verdict
- Calculate score
- Explain why confidence is high/low
- Show limitations

## Milestone 10: Memory
- Create SQLite database
- Save cases
- Save sources
- Save timeline
- Load past cases
- Show case history

## Milestone 11: Report Export
- Generate Markdown report
- Add download button
- Optional PDF export

## Milestone 12: Documentation
- README
- PRD
- TRD
- Architecture
- Agent design
- UI spec
- Demo script

## Milestone 13: Demo Prep
- Choose best claim
- Record 3–5 min demo
- Push GitHub
- Write LinkedIn post

## Priority Labels
P0:
- Claim input
- Planner
- Search
- Source scoring
- TraceBack timeline
- Verdict
- Memory

P1:
- OCR
- PDF upload
- Report download

P2:
- React Flow graph
- ChromaDB
- Google Trends
- Social spread visualization
