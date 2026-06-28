from __future__ import annotations

import json
from typing import Any

from app.config.settings import Settings, get_settings
from app.database.connection import connect
from app.database.schema import SCHEMA_SQL
from app.models import (
    AgentActivity,
    CaseStatus,
    CaseSummary,
    Contradiction,
    EvidenceSource,
    InvestigationState,
    TracebackEvent,
    new_id,
)


class SQLiteMemory:
    """SQLite-backed memory for investigations, evidence, timelines, and preferences."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.initialize()

    def initialize(self) -> None:
        with connect(self.settings.database_url) as connection:
            connection.executescript(SCHEMA_SQL)

    def save_case(self, state: InvestigationState) -> None:
        claim_text = state.claim.main_claim if state.claim else None
        title = (claim_text or state.raw_input).strip()[:90]
        domain = state.claim.domain.value if state.claim else None
        with connect(self.settings.database_url) as connection:
            connection.execute(
                """
                INSERT INTO cases (
                    id, user_id, title, original_input, extracted_claim, domain, verdict,
                    confidence, reasoning_summary, report_markdown, status, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title=excluded.title,
                    extracted_claim=excluded.extracted_claim,
                    domain=excluded.domain,
                    verdict=excluded.verdict,
                    confidence=excluded.confidence,
                    reasoning_summary=excluded.reasoning_summary,
                    report_markdown=excluded.report_markdown,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (
                    state.case_id,
                    state.user_id,
                    title,
                    state.raw_input,
                    claim_text,
                    domain,
                    state.verdict.value if state.verdict else None,
                    state.confidence,
                    state.reasoning_summary,
                    state.report_markdown,
                    state.status.value,
                    state.created_at.isoformat(),
                    state.updated_at.isoformat(),
                ),
            )
            self._replace_sources(connection, state.case_id, state.evidence)
            self._replace_timeline(connection, state.case_id, state.traceback_timeline)
            self._replace_contradictions(connection, state.case_id, state.contradictions)
            self._replace_activities(connection, state.case_id, state.activities)

    def list_cases(self, user_id: str = "demo_user") -> list[CaseSummary]:
        with connect(self.settings.database_url) as connection:
            rows = connection.execute(
                """
                SELECT id, COALESCE(extracted_claim, original_input) AS claim, verdict, confidence, created_at
                FROM cases
                WHERE user_id = ?
                ORDER BY created_at DESC
                """,
                (user_id,),
            ).fetchall()
        return [
            CaseSummary(
                case_id=row["id"],
                claim=row["claim"],
                verdict=row["verdict"],
                confidence=row["confidence"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_case_payload(self, case_id: str) -> dict[str, Any] | None:
        with connect(self.settings.database_url) as connection:
            case = connection.execute("SELECT * FROM cases WHERE id = ?", (case_id,)).fetchone()
            if case is None:
                return None
            sources = connection.execute("SELECT * FROM sources WHERE case_id = ?", (case_id,)).fetchall()
            timeline = connection.execute(
                "SELECT * FROM traceback_events WHERE case_id = ? ORDER BY event_date",
                (case_id,),
            ).fetchall()
            contradictions = connection.execute(
                "SELECT * FROM contradictions WHERE case_id = ?",
                (case_id,),
            ).fetchall()
            activities = connection.execute(
                "SELECT * FROM activities WHERE case_id = ? ORDER BY timestamp",
                (case_id,),
            ).fetchall()
        return {
            "case_id": case["id"],
            "user_id": case["user_id"],
            "claim": case["extracted_claim"],
            "original_input": case["original_input"],
            "domain": case["domain"],
            "verdict": case["verdict"],
            "confidence": case["confidence"],
            "reasoning_summary": case["reasoning_summary"],
            "report_markdown": case["report_markdown"],
            "status": case["status"],
            "created_at": case["created_at"],
            "updated_at": case["updated_at"],
            "sources": [dict(row) for row in sources],
            "traceback_timeline": [dict(row) for row in timeline],
            "contradictions": [dict(row) for row in contradictions],
            "activities": [dict(row) for row in activities],
        }

    def save_preferences(self, user_id: str, preferences: dict[str, Any]) -> None:
        with connect(self.settings.database_url) as connection:
            for key, value in preferences.items():
                connection.execute(
                    """
                    INSERT INTO user_preferences (id, user_id, key, value, updated_at)
                    VALUES (?, ?, ?, ?, datetime('now'))
                    """,
                    (new_id("pref"), user_id, key, json.dumps(value)),
                )

    def get_preferences(self, user_id: str) -> dict[str, Any]:
        with connect(self.settings.database_url) as connection:
            rows = connection.execute(
                """
                SELECT key, value FROM user_preferences
                WHERE user_id = ?
                ORDER BY updated_at
                """,
                (user_id,),
            ).fetchall()
        preferences: dict[str, Any] = {}
        for row in rows:
            try:
                preferences[row["key"]] = json.loads(row["value"])
            except json.JSONDecodeError:
                preferences[row["key"]] = row["value"]
        return preferences

    def _replace_sources(self, connection, case_id: str, sources: list[EvidenceSource]) -> None:
        connection.execute("DELETE FROM sources WHERE case_id = ?", (case_id,))
        connection.executemany(
            """
            INSERT INTO sources (
                id, case_id, title, url, snippet, source_type, stance,
                quality_score, published_date, retrieved_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    source.id,
                    case_id,
                    source.title,
                    source.url,
                    source.snippet,
                    source.source_type.value,
                    source.stance.value,
                    source.quality_score,
                    source.published_date,
                    source.retrieved_at.isoformat(),
                )
                for source in sources
            ],
        )

    def _replace_timeline(
        self,
        connection,
        case_id: str,
        events: list[TracebackEvent],
    ) -> None:
        connection.execute("DELETE FROM traceback_events WHERE case_id = ?", (case_id,))
        connection.executemany(
            """
            INSERT INTO traceback_events (
                id, case_id, event_date, source_title, source_url,
                claim_version, quality_label, notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    event.id,
                    case_id,
                    event.event_date,
                    event.source_title,
                    event.source_url,
                    event.claim_version,
                    event.quality_label,
                    event.notes,
                )
                for event in events
            ],
        )

    def _replace_contradictions(
        self,
        connection,
        case_id: str,
        contradictions: list[Contradiction],
    ) -> None:
        connection.execute("DELETE FROM contradictions WHERE case_id = ?", (case_id,))
        connection.executemany(
            """
            INSERT INTO contradictions (
                id, case_id, claim_part, source_a, source_b, contradiction_summary, severity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    contradiction.id,
                    case_id,
                    contradiction.claim_part,
                    contradiction.source_a,
                    contradiction.source_b,
                    contradiction.contradiction_summary,
                    contradiction.severity,
                )
                for contradiction in contradictions
            ],
        )

    def _replace_activities(
        self,
        connection,
        case_id: str,
        activities: list[AgentActivity],
    ) -> None:
        connection.execute("DELETE FROM activities WHERE case_id = ?", (case_id,))
        connection.executemany(
            """
            INSERT INTO activities (id, case_id, step, agent, tool, status, detail, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    new_id("act"),
                    case_id,
                    activity.step,
                    activity.agent,
                    activity.tool,
                    activity.status,
                    activity.detail,
                    activity.timestamp.isoformat(),
                )
                for activity in activities
            ],
        )
