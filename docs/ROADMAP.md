# 3-Day Roadmap: ProofPath AI

## Goal
Build a polished MVP that clearly demonstrates agentic behavior.

## Day 1: Core Agent Backend

### Morning
- Create project structure
- Set up environment variables
- Connect LLM API
- Build basic Streamlit/Next.js UI shell

### Afternoon
- Implement claim extraction
- Implement planner
- Implement web search tool
- Implement source scoring

### Evening
- Implement LangGraph/simple state machine
- Save investigation state
- Test with 3 claims

Deliverable:
- User enters claim
- Agent extracts claim
- Agent creates plan
- Agent searches web
- Agent returns source list

## Day 2: TraceBack + Reasoning

### Morning
- Implement TraceBack search
- Generate claim variants
- Build timeline from sources
- Add source quality labels

### Afternoon
- Implement contradiction detection
- Implement confidence calculator
- Implement verdict generator

### Evening
- Add SQLite memory
- Add past investigations panel
- Add report markdown generation

Deliverable:
- Full investigation report with:
  - evidence,
  - traceback timeline,
  - contradictions,
  - verdict,
  - confidence.

## Day 3: Polish + Demo

### Morning
- Improve UI
- Add loading states
- Add agent activity panel
- Add evidence locker

### Afternoon
- Add PDF/Markdown export
- Write README
- Add architecture diagrams
- Add screenshots

### Evening
- Record demo video
- Push GitHub repo
- Prepare LinkedIn post

Deliverable:
- GitHub-ready project
- Demo video
- README
- Polished UI

## Minimum Viable Feature List
By submission, the app must have:

- claim input,
- LLM planner,
- at least 2 tools,
- tool selection,
- evidence retrieval,
- source scoring,
- traceback timeline,
- contradiction detection,
- memory,
- final report.

## Features to Cut If Running Late
Cut in this order:
1. PDF export
2. OCR upload
3. ChromaDB
4. React Flow graph
5. External academic APIs
6. Authentication

Do not cut:
- planner,
- tools,
- memory,
- traceback timeline,
- evidence scoring.

## Best Demo Claim
Use a claim that is:
- easy to understand,
- has misinformation potential,
- has enough search results,
- produces clear contradiction.

Examples:
- "Cold water after meals causes cancer."
- "Creatine damages kidneys in healthy adults."
- "Blue light glasses prevent all eye damage."
- "AI detectors can reliably detect ChatGPT writing."
- "Drinking alkaline water cures disease."

## Demo Script
1. Open app.
2. Enter claim.
3. Show extracted claim.
4. Show investigation plan.
5. Show selected tools.
6. Show search results.
7. Show TraceBack timeline.
8. Show contradictions.
9. Show confidence score.
10. Show saved case memory.
