# Memory Design

## 1. Why Memory Matters
ProofPath AI needs memory because the same user may verify related claims over time.

Example:
- Day 1: User verifies "Creatine damages kidneys."
- Day 2: User asks "What about creatine and hair loss?"
- The agent should remember the user's preference for medical studies and previous creatine investigation.

## 2. Memory Types

### 2.1 Session Memory
Temporary memory for the current investigation.

Stores:
- raw input,
- extracted claim,
- current plan,
- tool outputs,
- intermediate reasoning.

### 2.2 Case Memory
Persistent memory for completed investigations.

Stores:
- case ID,
- claim,
- sources,
- verdict,
- confidence,
- report,
- timeline.

### 2.3 User Preference Memory
Stores:
- preferred explanation style,
- trusted source types,
- avoided source types,
- preferred domains.

Example:
```json
{
  "user_id": "demo",
  "preferences": {
    "explanation_style": "simple but evidence-backed",
    "preferred_sources": ["systematic reviews", "official guidelines"],
    "avoid_sources": ["random blogs"]
  }
}
```

### 2.4 Claim Graph Memory
Stores relationships between claims.

Example:
```json
{
  "claim": "Cold water after meals causes cancer",
  "related_claims": [
    "Cold water solidifies fats",
    "Cold water causes digestive issues",
    "Cold drinks cause cancer"
  ],
  "verdict": "Unsupported",
  "confidence": 0.91
}
```

## 3. SQLite Schema

```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT,
    created_at TEXT
);

CREATE TABLE cases (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    claim TEXT,
    domain TEXT,
    verdict TEXT,
    confidence REAL,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE evidence (
    id TEXT PRIMARY KEY,
    case_id TEXT,
    title TEXT,
    url TEXT,
    source_type TEXT,
    stance TEXT,
    quality_score REAL,
    summary TEXT,
    published_date TEXT
);

CREATE TABLE traceback_events (
    id TEXT PRIMARY KEY,
    case_id TEXT,
    event_date TEXT,
    claim_version TEXT,
    source_title TEXT,
    source_url TEXT,
    notes TEXT
);

CREATE TABLE contradictions (
    id TEXT PRIMARY KEY,
    case_id TEXT,
    claim_part TEXT,
    contradiction TEXT,
    severity TEXT
);

CREATE TABLE user_preferences (
    user_id TEXT,
    preference_key TEXT,
    preference_value TEXT
);

CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    case_id TEXT,
    markdown TEXT,
    pdf_path TEXT,
    created_at TEXT
);
```

## 4. Optional Future Vector Store Design
ChromaDB can be added later for semantic recall. The implemented project currently uses SQLite memory.

Potential future collections:
- `claim_memory`
- `source_memory`
- `report_memory`
- `user_preference_memory`

Stored documents:
- claim summaries,
- source excerpts,
- contradiction explanations,
- final verdicts.

## 5. Retrieval Examples

### Similar Claim Retrieval
Input:
> Does creatine cause hair loss?

Retrieve:
- previous creatine investigations,
- user source preferences,
- related health claim reports.

### Source Trust Recall
Input:
> Is this claim true?

Retrieve:
- user's preference for source style,
- previous highly trusted sources.

## 6. Memory in the UI
Show a "Past Investigations" panel:

- Creatine and kidneys — Mostly unsupported — 82%
- Cold water and cancer — False — 91%
- Seed oils and heart disease — Mixed evidence — 67%

## 7. MVP Memory Implementation
For 3 days:
- SQLite only is enough.
- Store one row per case.
- Store sources as JSON.
- Store timeline as JSON.
- Add ChromaDB only if time remains.

## 8. Portfolio Upgrade
Later:
- Add ChromaDB.
- Add claim graph.
- Add related-claim suggestions.
- Add user-level source preference learning.
