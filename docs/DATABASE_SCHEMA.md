# Database Schema

## 1. SQLite MVP Schema

```sql
CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT,
    original_input TEXT NOT NULL,
    extracted_claim TEXT,
    domain TEXT,
    verdict TEXT,
    confidence REAL,
    report_markdown TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    title TEXT,
    url TEXT,
    snippet TEXT,
    source_type TEXT,
    stance TEXT,
    quality_score REAL,
    published_date TEXT,
    retrieved_at TEXT,
    FOREIGN KEY(case_id) REFERENCES cases(id)
);

CREATE TABLE IF NOT EXISTS traceback_events (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    event_date TEXT,
    source_title TEXT,
    source_url TEXT,
    claim_version TEXT,
    quality_label TEXT,
    notes TEXT,
    FOREIGN KEY(case_id) REFERENCES cases(id)
);

CREATE TABLE IF NOT EXISTS contradictions (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    claim_part TEXT,
    source_a TEXT,
    source_b TEXT,
    contradiction_summary TEXT,
    severity TEXT,
    FOREIGN KEY(case_id) REFERENCES cases(id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT
);
```

## 2. JSON Fields
For faster MVP, some complex objects can be stored as JSON strings inside the cases table.

Example:
```json
{
  "plan": ["Search web", "Trace claim", "Score sources"],
  "selected_tools": ["web_search", "traceback_search", "source_scorer"]
}
```

## 3. Case Status
Possible case statuses:
- created
- extracting_claim
- planning
- searching
- tracing_origin
- scoring
- reasoning
- completed
- failed

## 4. Source Stance
Possible stances:
- supports
- refutes
- mixed
- neutral
- background

## 5. Source Type
Possible types:
- government
- academic
- systematic_review
- official_organization
- news
- expert_blog
- forum
- social_media
- marketing
- unknown

## 6. Confidence Storage
Store confidence as float:
- 0.0 to 1.0 internally
- 0 to 100 in UI

## 7. Future Knowledge Graph Tables

```sql
CREATE TABLE claim_nodes (
    id TEXT PRIMARY KEY,
    normalized_claim TEXT,
    domain TEXT,
    latest_verdict TEXT,
    latest_confidence REAL
);

CREATE TABLE claim_edges (
    id TEXT PRIMARY KEY,
    source_claim_id TEXT,
    target_claim_id TEXT,
    relationship TEXT
);
```

Relationships:
- variant_of
- contradicts
- supports
- caused_by_misinterpretation
- repeated_from
