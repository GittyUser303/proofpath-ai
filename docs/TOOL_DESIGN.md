# Tool Design

## 1. Tool Philosophy
Each tool should do one job well and return structured data.

The LLM should not scrape websites manually or hallucinate source metadata. Tools should provide factual inputs.

## 2. Required MVP Tools

## 2.1 Web Search Tool

```python
def web_search(query: str, max_results: int = 5) -> list[dict]:
    \"\"\"Searches the web for relevant sources.\"\"\"
```

Returns:
```json
[
  {
    "title": "...",
    "url": "...",
    "snippet": "...",
    "published_date": "..."
  }
]
```

## 2.2 TraceBack Search Tool

```python
def traceback_search(claim: str) -> list[dict]:
    \"\"\"Searches exact phrases and claim variants to find earlier appearances.\"\"\"
```

Search strategies:
- exact phrase search,
- shortened claim search,
- entity + phrase search,
- old-date search,
- repeated wording detection.

## 2.3 Source Scoring Tool

```python
def score_source(source: dict) -> dict:
    \"\"\"Scores source credibility and relevance.\"\"\"
```

Scoring factors:
- government/academic source: high,
- peer-reviewed research: high,
- official organization: high,
- mainstream news: medium,
- blogs: low to medium,
- forums/social: low,
- marketing pages: low unless verifying company claim.

## 2.4 Contradiction Detection Tool

```python
def detect_contradictions(claim: str, evidence: list[dict]) -> list[dict]:
    \"\"\"Compares evidence and finds disagreement.\"\"\"
```

## 2.5 Confidence Calculator

```python
def calculate_confidence(source_quality, consistency, primary_strength, recency, traceback_clarity):
    return (
        0.30 * source_quality +
        0.25 * consistency +
        0.20 * primary_strength +
        0.15 * recency +
        0.10 * traceback_clarity
    )
```

## 2.6 Report Generator

```python
def generate_report(case_data: dict) -> str:
    \"\"\"Generates Markdown report.\"\"\"
```

## 3. Optional Tools

### Academic Search Tool
Searches PubMed, Semantic Scholar, or arXiv.

### OCR Tool
Extracts text from screenshots.

### PDF Parser
Extracts text from PDF files.

### Claim Variant Generator
Generates search variants for traceback.

### Timeline Builder
Sorts sources by date.

## 4. Tool Selection Logic

| Claim Type | Tools |
|---|---|
| Health | Web Search, PubMed, Source Scoring, Contradiction |
| Viral Rumor | Web Search, TraceBack, Timeline, Source Scoring |
| Product Claim | Web Search, Company Search, Source Scoring, Contradiction |
| AI Answer | Claim Extraction, Web Search, Evidence Ranking |
| Academic Claim | arXiv, Semantic Scholar, Source Scoring |

## 5. Tool Output Contract
Every tool should return:
- success boolean,
- data,
- error if any,
- source metadata,
- timestamp.

Example:
```json
{
  "success": true,
  "tool": "web_search",
  "query": "cold water after meals cancer evidence",
  "data": [],
  "error": null,
  "timestamp": "2026-06-26T12:00:00"
}
```

## 6. MVP Tool Choices
For the fastest build:
- use Tavily for web search,
- use LLM for claim extraction,
- use Python for scoring,
- use SQLite for memory,
- use Markdown for reports.

This is enough to satisfy the bootcamp requirements.
