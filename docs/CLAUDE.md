# CLAUDE.md

## Project
ProofPath AI — an agentic evidence verification engine with TraceBack-style claim provenance.

## Objective
Build a working MVP in 3 days that satisfies the bootcamp requirements and looks strong on GitHub.

## Core Rules
- Do not build a generic chatbot.
- Every response must go through the investigation workflow.
- Keep agents modular.
- Keep tools independent.
- Use structured JSON between agents.
- Save memory after every investigation.
- Show tool usage in the UI.
- Show confidence and uncertainty.
- Never fabricate sources.

## Required Workflow
1. Extract claim
2. Plan investigation
3. Select tools
4. Retrieve evidence
5. Trace origin/versions
6. Score source quality
7. Detect contradictions
8. Reason verdict
9. Calculate confidence
10. Save memory
11. Generate report

## Coding Style
- Python type hints
- Pydantic models where useful
- Clear file separation
- Small functions
- No business logic inside UI components
- Use `.env` for keys
- Use meaningful logs
- Handle tool failures gracefully

## Suggested File Structure

```text
proofpath-ai/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── graph.py
│   ├── agents/
│   │   ├── claim_extractor.py
│   │   ├── planner.py
│   │   ├── evidence_retriever.py
│   │   ├── traceback_agent.py
│   │   ├── source_quality.py
│   │   ├── contradiction.py
│   │   ├── reasoning.py
│   │   └── reporter.py
│   ├── tools/
│   │   ├── web_search.py
│   │   ├── academic_search.py
│   │   ├── traceback_search.py
│   │   ├── source_scoring.py
│   │   ├── pdf_parser.py
│   │   └── report_generator.py
│   ├── memory/
│   │   ├── sqlite_store.py
│   │   └── vector_store.py
│   └── ui/
│       └── streamlit_app.py
├── docs/
├── tests/
├── README.md
├── requirements.txt
└── .env.example
```

## MVP Priority
Build in this order:
1. Streamlit UI
2. LLM connection
3. Claim extraction
4. Planner
5. Web search
6. Source scoring
7. TraceBack timeline
8. Contradiction detection
9. SQLite memory
10. Report generation

## UI Rules
The UI must show:
- current agent step,
- selected tools,
- source cards,
- evidence locker,
- TraceBack timeline,
- confidence score,
- final verdict,
- saved previous cases.

## Safety Rules
- Medical/legal/financial claims need disclaimers.
- Do not say "definitely true" unless evidence is extremely strong.
- Use "earliest accessible source found" instead of "original source" unless certain.
- Include source limitations in final reports.

## Definition of Done
The project is done when:
- user can enter a claim,
- app runs multi-step workflow,
- at least 2 tools are used,
- investigation is saved,
- final report is generated,
- README explains workflow, tools, and memory.
