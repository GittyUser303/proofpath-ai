SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cases (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT,
    original_input TEXT NOT NULL,
    extracted_claim TEXT,
    domain TEXT,
    verdict TEXT,
    confidence REAL,
    reasoning_summary TEXT,
    report_markdown TEXT,
    status TEXT NOT NULL,
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

CREATE TABLE IF NOT EXISTS activities (
    id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    step TEXT,
    agent TEXT,
    tool TEXT,
    status TEXT,
    detail TEXT,
    timestamp TEXT,
    FOREIGN KEY(case_id) REFERENCES cases(id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    updated_at TEXT
);
"""
