# ProofPath AI - Updated Project Context & Handoff Brief

> **Purpose of this document:** This is the updated handoff brief for the current ProofPath project state. It reflects the latest implementation changes: the FastAPI-served Evidence Desk UI, real-time streamed workflow progress, improved TraceBack query strategy, qualitative evidence labels, updated color identity, and improved source classification.

---

## 1. Current One-Paragraph Summary

**ProofPath** is now positioned less like a generic "AI app" and more like an **Evidence Desk** for students, journalists, researchers, and careful readers who want to check whether an AI answer, viral claim, article excerpt, or product promise is hallucinated or unsupported. The app runs from one FastAPI server at `http://127.0.0.1:8000/`, accepts a claim, performs a multi-step investigation, streams the actual backend workflow into the UI in real time, retrieves sources, attempts TraceBack-style provenance search, scores citations, detects contradictions, produces a cautious verdict, and saves the case in SQLite. The core reasoning is still mostly deterministic Python rather than LLM-powered, but the user experience now presents an auditable evidence brief instead of a chatbot or fake progress animation.

---

## 2. Important Changes Since The Previous Brief

The previous handoff file is outdated in these areas:

| Area | Old brief said | Current state |
|---|---|---|
| Real-time workflow | Progress was simulated client-side with timers. | **Fixed.** `POST /api/investigate/stream` streams actual backend workflow events as NDJSON. |
| Work process UI | Side/compact agent list or static methodology. | **Updated.** Main-page Claude-like process timeline shows live steps, details, tools, and produced counts. |
| TraceBack | One exact/shortened phrase search only. | **Improved.** Multi-query TraceBack strategy now searches exact phrase, shortened phrase, origin, fact-check, and myth variants. |
| TraceBack reliability | Could look like "no origin" meant no origin exists. | **Clarified.** UI and report wording frame missing TraceBack as "not retrieved in this run," not proof of no origin. |
| Source labels | Many websites displayed as `unknown`. | **Improved.** Better classification for fact-check, medical/authority, research, news, government, and domain fallback labels. |
| DuckDuckGo result URLs | Redirect URLs could weaken domain classification. | **Fixed.** DuckDuckGo `uddg` redirect URLs are cleaned before scoring/classification. |
| Confidence display | Percentages appeared overprecise and unreliable. | **Updated.** Main UI uses qualitative labels: `Very weak`, `Weak`, `Mixed`, `Strong`, `Very strong`. Raw numeric score still exists internally. |
| Visual identity | Dark AI dashboard with oversized text. | **Updated.** UI is now `ProofPath | Evidence Desk`, more spacious, editorial, student/journalist friendly. |
| Accent colors | Teal/cyan identity. | **Updated.** Uses `#f80743` and `#09f6bb` as the main visual accents. |
| Tests | 6 backend tests. | **Updated.** 7 tests, including a streaming investigation test. |

---

## 3. Current Product Identity

### Name in UI

The UI now emphasizes:

```text
ProofPath
Evidence Desk
```

instead of leading with "ProofPath AI."

### Current positioning

ProofPath is an evidence-checking desk for:

- students verifying citations before using them,
- journalists checking viral claims,
- researchers reviewing source quality,
- people auditing AI-generated answers,
- creators who need to avoid sharing unsupported claims.

### Current tone

The UI should sound:

- reliable,
- calm,
- skeptical,
- transparent,
- citation-first,
- not like a generic AI chatbot.

---

## 4. Current Architecture

```text
ProofPath
|
|-- FastAPI backend
|   |-- /api/investigate
|   |-- /api/investigate/stream
|   |-- /api/cases
|   |-- /api/cases/{case_id}
|   |-- /api/report/{case_id}
|   |-- /api/upload
|   |-- /api/preferences
|   `-- /api/health
|
|-- Static Evidence Desk frontend
|   |-- backend/app/static/index.html
|   |-- backend/app/static/styles.css
|   `-- backend/app/static/app.js
|
|-- SQLite memory
|   `-- data/proofpath.db
|
`-- Optional/alternate frontend source
    `-- frontend/ React/Vite source and older Streamlit prototype
```

Users visit only:

```text
http://127.0.0.1:8000/
```

FastAPI serves both the API and the live dashboard.

---

## 5. Current Tech Stack

### Actually used

- Python
- FastAPI
- Pydantic
- SQLite via synchronous `sqlite3`
- httpx
- Tavily search when `TAVILY_API_KEY` is configured
- DuckDuckGo HTML fallback when Tavily is not configured
- PyMuPDF for PDF parsing
- Pillow + pytesseract wrapper for OCR
- HTML/CSS/vanilla JS frontend served from FastAPI
- Pytest

### Declared but not meaningfully used yet

- LangGraph
- LangChain Core
- OpenAI/Gemini/Anthropic API keys
- ChromaDB/vector memory

### Important reality check

The project still does **not** currently call an LLM anywhere. The "agents" are deterministic Python functions. The next major product leap would be wiring Gemini/OpenAI/Claude into claim extraction, planning, reasoning, contradiction analysis, and source classification.

---

## 6. Current Repository Structure

```text
ProofPath-ai/
|-- README.md
|-- ProofPath-AI-Project-Context-UPDATED.md
|-- pyproject.toml
|-- requirements.txt
|-- .env.example
|-- .gitignore
|
|-- backend/
|   `-- app/
|       |-- main.py
|       |-- models.py
|       |-- workflow.py
|       |
|       |-- api/
|       |   `-- routes.py
|       |
|       |-- agents/
|       |   |-- claim_extraction.py
|       |   |-- planner.py
|       |   `-- reasoning.py
|       |
|       |-- tools/
|       |   |-- search.py
|       |   |-- source_scoring.py
|       |   |-- contradictions.py
|       |   |-- confidence.py
|       |   |-- document_parsing.py
|       |   `-- reporting.py
|       |
|       |-- database/
|       |   |-- connection.py
|       |   `-- schema.py
|       |
|       |-- memory/
|       |   `-- sqlite_memory.py
|       |
|       `-- static/
|           |-- index.html
|           |-- styles.css
|           `-- app.js
|
|-- frontend/
|   |-- React/Vite source
|   `-- streamlit_app.py
|
|-- tests/
|   |-- test_health.py
|   |-- test_claim_extraction.py
|   |-- test_confidence.py
|   `-- test_source_scoring.py
|
|-- docs/
|   `-- original planning/specification corpus
|
`-- data/
    `-- proofpath.db
```

---

## 7. Current Workflow Behavior

Main workflow file:

```text
backend/app/workflow.py
```

Primary class:

```python
ProofPathWorkflow
```

Main method:

```python
async def run(raw_input, user_id="demo_user", progress_callback=None)
```

The workflow currently does:

1. Extract claim with heuristic claim extractor.
2. Plan investigation with rule-based planner.
3. Emit live progress event.
4. Search public web sources.
5. Emit live progress event.
6. Search academic/institutional sources when required.
7. Emit live progress event.
8. Curate and deduplicate source candidates.
9. Emit live progress event with citation count.
10. Run TraceBack multi-query search when required.
11. Curate TraceBack candidate events.
12. Emit live progress event with TraceBack count.
13. Score source reliability and stance.
14. Detect contradictions.
15. Build verdict.
16. Calculate confidence.
17. Generate Markdown report.
18. Save memory.
19. Emit final event.

### New real-time progress behavior

`ProofPathWorkflow.run()` now accepts:

```python
progress_callback: ProgressCallback | None
```

Each meaningful step calls:

```python
await self._emit(progress_callback, state, "activity")
```

The payload includes:

```json
{
  "event": "activity",
  "case_id": "...",
  "status": "...",
  "activity": {
    "step": "...",
    "agent": "...",
    "tool": "...",
    "detail": "..."
  },
  "counts": {
    "evidence": 0,
    "traceback": 0,
    "contradictions": 0
  },
  "errors": []
}
```

---

## 8. Current API Surface

Main API file:

```text
backend/app/api/routes.py
```

### `POST /api/investigate`

Runs the complete investigation and returns only the final case metadata. Still supported.

### `POST /api/investigate/stream`

**New and important.**

Runs the investigation and streams real backend progress as newline-delimited JSON.

Content type:

```text
application/x-ndjson
```

Events include:

- `activity`
- `heartbeat`
- `complete`
- `error`

This endpoint is now used by the live frontend.

### `GET /api/cases`

Lists saved cases for a `user_id`.

### `GET /api/cases/{case_id}`

Returns full case payload including:

- sources,
- TraceBack timeline,
- contradictions,
- activities,
- report markdown.

### `GET /api/report/{case_id}`

Returns Markdown report text.

### `POST /api/upload`

Extracts text from:

- text files,
- PDFs via PyMuPDF,
- images via pytesseract/Pillow.

Still not fully chained into the UI investigation flow.

### `POST /api/preferences`

Stores user preferences.

### `GET /api/health`

Health check.

---

## 9. Current Frontend State

The live frontend is:

```text
backend/app/static/
```

### Current UI identity

The UI is now:

```text
ProofPath | Evidence Desk
```

It is designed for students and journalists rather than feeling like a generic AI console.

### Current UI features

- top navigation instead of heavy left rail,
- claim intake card,
- saved checks panel,
- qualitative evidence-strength result tiles,
- readable verdict brief,
- real-time work process timeline,
- source cards,
- TraceBack trail,
- contradiction cautions,
- citation map,
- source reliability panel,
- dark/light mode,
- report export.

### Real-time workflow UI

The UI no longer advances steps with a fake timer.

It calls:

```javascript
fetch("/api/investigate/stream", ...)
```

Then reads the response stream with:

```javascript
response.body.getReader()
```

As each backend event arrives, the UI appends it to the process timeline.

### Visual identity

Current accent colors:

```text
#f80743
#09f6bb
```

The UI uses:

- `#f80743` for energy/risk/action contrast,
- `#09f6bb` for verification/trust/completion.

---

## 10. Current TraceBack Implementation

TraceBack is still heuristic, not a true provenance engine.

### What it now does

File:

```text
backend/app/tools/search.py
```

Method:

```python
async def traceback_search(claim, max_results=None)
```

It now runs multiple query strategies:

1. exact phrase:

```text
"full claim"
```

2. shortened phrase:

```text
"first 8 words"
```

3. origin query:

```text
core terms origin
```

4. fact-check query:

```text
core terms fact check
```

5. myth query:

```text
core terms myth
```

It deduplicates URLs and returns candidate sources.

### What it does not do yet

TraceBack does **not** prove:

- the first-ever origin,
- who started a claim,
- a complete mutation chain,
- social spread history.

Correct product wording remains:

- "earliest accessible candidate",
- "source candidate",
- "no earlier source retrieved in this run",
- not "this is the origin."

### Verified behavior

With network access enabled, the cold-water/cancer TraceBack query returned candidates such as:

- Snopes,
- AFP Fact Check,
- MythBreak,
- related health/myth pages.

If network is blocked or no search provider is reachable, TraceBack can return no events.

---

## 11. Source Classification Updates

File:

```text
backend/app/tools/source_scoring.py
```

The source type enum now includes:

```python
FACT_CHECK = "fact_check"
```

Additional domains are recognized:

- `snopes.com`
- `factcheck.org`
- `politifact.com`
- `cancer.org`
- `mayoclinic.org`
- `clevelandclinic.org`
- `healthline.com`
- `medicalnewstoday.com`
- `reuters.com`
- `apnews.com`

DuckDuckGo redirect URLs are cleaned in:

```text
backend/app/tools/search.py
```

This helps avoid source cards showing only `unknown`.

The UI also has a fallback label strategy:

- known `source_type`,
- fact-check domain detection,
- `.gov` as government,
- PubMed/Scholar/`.edu` as research,
- otherwise display the source domain.

---

## 12. Confidence Display

Internally the backend still stores confidence as a float:

```text
0.0 - 1.0
```

But the UI no longer emphasizes exact percentages because those looked misleading.

Current UI labels:

```text
Very weak
Weak
Mixed
Strong
Very strong
```

This is more honest for the current heuristic scoring system.

---

## 13. Current Tests

Tests now pass:

```text
7 passed
```

Current test coverage includes:

- health endpoint,
- root dashboard serving,
- streaming investigation endpoint,
- claim extraction,
- confidence scoring,
- source scoring.

Important streaming test:

```python
test_streaming_investigation_returns_progress_events
```

It asserts that `/api/investigate/stream` emits:

- activity events,
- completion event.

Additional smoke verification showed:

```text
stream emits Curating source candidates
stream emits Curating TraceBack trail
13 real activity events emitted
```

---

## 14. How To Run Current App

Recommended command:

```powershell
.\.venv-proofpath\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
```

Then open:

```text
http://127.0.0.1:8000/
```

API docs:

```text
http://127.0.0.1:8000/docs
```

Health:

```text
http://127.0.0.1:8000/api/health
```

If CSS/JS appears stale, hard refresh the browser.

---

## 15. Known Gaps After Latest Updates

These gaps remain important:

1. **No LLM is connected yet.** Agents are still deterministic heuristics.
2. **Not LangGraph yet.** The workflow is a custom async state machine with streaming callbacks.
3. **TraceBack is improved but still heuristic.** It finds accessible candidates, not definitive origins.
4. **No true academic APIs yet.** Academic search still uses web search with site operators.
5. **No ChromaDB/vector memory yet.**
6. **No authentication.** `user_id` is still a free-text workspace value.
7. **Upload extraction is not chained into investigation from the UI.**
8. **OCR requires system Tesseract installed, not just `pytesseract`.**
9. **SQLite is synchronous inside async routes.**
10. **No case deletion endpoint yet.**
11. **PDF report export is not implemented; reports are Markdown only.**
12. **React/Vite source exists but the live app is the FastAPI-served static Evidence Desk.**

The old gap "no streaming/SSE of agent progress" is no longer accurate and should be removed from any future handoff document.

---

## 16. Recommended Next Steps

Most valuable next steps:

1. Connect an LLM provider, likely Gemini, to:
   - claim extraction,
   - planning,
   - contradiction analysis,
   - final reasoning.
2. Preserve the heuristic agents as fallback paths.
3. Replace confidence overprecision with explainable evidence-strength factors in both report and UI.
4. Add real PubMed/Semantic Scholar/arXiv integrations.
5. Add upload-to-investigation chaining in the UI.
6. Add case deletion.
7. Convert SQLite access to async or isolate DB writes.
8. Decide whether React/Vite or static FastAPI UI is canonical.
9. Add a real deployment build path.
10. Make an initial git commit before further major changes.

---

## 17. Quick Reference

Current most important files:

```text
backend/app/workflow.py
backend/app/api/routes.py
backend/app/tools/search.py
backend/app/tools/source_scoring.py
backend/app/static/index.html
backend/app/static/styles.css
backend/app/static/app.js
tests/test_health.py
```

Current most important endpoint:

```text
POST /api/investigate/stream
```

Current demo claim:

```text
Drinking cold water after meals causes cancer.
```

Current status:

```text
FastAPI + SQLite + live Evidence Desk UI + streaming backend progress + heuristic agents + improved TraceBack search.
```

