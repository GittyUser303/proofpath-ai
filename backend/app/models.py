from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, HttpUrl


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(UTC)


def new_id(prefix: str) -> str:
    """Create a readable unique identifier."""
    return f"{prefix}_{uuid4().hex[:12]}"


class ClaimDomain(StrEnum):
    HEALTH = "health"
    TECH = "tech"
    FINANCE = "finance"
    POLITICS = "politics"
    PRODUCT = "product"
    ACADEMIC = "academic"
    GENERAL = "general"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceType(StrEnum):
    GOVERNMENT = "government"
    ACADEMIC = "academic"
    SYSTEMATIC_REVIEW = "systematic_review"
    OFFICIAL_ORGANIZATION = "official_organization"
    FACT_CHECK = "fact_check"
    NEWS = "news"
    EXPERT_BLOG = "expert_blog"
    FORUM = "forum"
    SOCIAL_MEDIA = "social_media"
    MARKETING = "marketing"
    UNKNOWN = "unknown"


class SourceStance(StrEnum):
    SUPPORTS = "supports"
    REFUTES = "refutes"
    MIXED = "mixed"
    NEUTRAL = "neutral"
    BACKGROUND = "background"


class CaseStatus(StrEnum):
    CREATED = "created"
    EXTRACTING_CLAIM = "extracting_claim"
    PLANNING = "planning"
    SEARCHING = "searching"
    TRACING_ORIGIN = "tracing_origin"
    SCORING = "scoring"
    REASONING = "reasoning"
    COMPLETED = "completed"
    FAILED = "failed"


class VerdictLabel(StrEnum):
    SUPPORTED = "Supported"
    MOSTLY_SUPPORTED = "Mostly Supported"
    MIXED_EVIDENCE = "Mixed Evidence"
    UNSUPPORTED = "Unsupported"
    MISLEADING = "Misleading"
    FALSE = "False"
    NOT_ENOUGH_EVIDENCE = "Not Enough Evidence"


class AgentActivity(BaseModel):
    step: str
    agent: str
    tool: str | None = None
    status: str = "done"
    detail: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)


class Claim(BaseModel):
    main_claim: str
    sub_claims: list[str] = Field(default_factory=list)
    domain: ClaimDomain = ClaimDomain.GENERAL
    risk_level: RiskLevel = RiskLevel.LOW
    entities: list[str] = Field(default_factory=list)


class InvestigationPlan(BaseModel):
    steps: list[str]
    selected_tools: list[str]
    needs_traceback: bool = True
    needs_academic_search: bool = False
    rationale: str


class ToolResult(BaseModel):
    success: bool
    tool: str
    query: str | None = None
    data: list[dict[str, Any]] | dict[str, Any] | None = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=utc_now)


class EvidenceSource(BaseModel):
    id: str = Field(default_factory=lambda: new_id("src"))
    title: str
    url: str
    snippet: str = ""
    source_type: SourceType = SourceType.UNKNOWN
    stance: SourceStance = SourceStance.NEUTRAL
    quality_score: float = 0.0
    published_date: str | None = None
    retrieved_at: datetime = Field(default_factory=utc_now)


class TracebackEvent(BaseModel):
    id: str = Field(default_factory=lambda: new_id("trace"))
    event_date: str | None = None
    source_title: str
    source_url: str
    claim_version: str
    quality_label: str = "unknown"
    notes: str = "Earliest accessible source candidate, not guaranteed origin."


class Contradiction(BaseModel):
    id: str = Field(default_factory=lambda: new_id("contra"))
    claim_part: str
    source_a: str | None = None
    source_b: str | None = None
    contradiction_summary: str
    severity: str = "medium"


class ConfidenceBreakdown(BaseModel):
    source_quality: float
    evidence_consistency: float
    primary_source_strength: float
    recency: float
    traceback_clarity: float
    contradiction_penalty: float = 0.0
    final_score: float
    explanation: str


class InvestigationState(BaseModel):
    case_id: str = Field(default_factory=lambda: new_id("case"))
    user_id: str = "demo_user"
    raw_input: str
    files: list[str] = Field(default_factory=list)
    status: CaseStatus = CaseStatus.CREATED
    claim: Claim | None = None
    plan: InvestigationPlan | None = None
    selected_tools: list[str] = Field(default_factory=list)
    evidence: list[EvidenceSource] = Field(default_factory=list)
    traceback_timeline: list[TracebackEvent] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    verdict: VerdictLabel | None = None
    confidence: float | None = None
    confidence_breakdown: ConfidenceBreakdown | None = None
    reasoning_summary: str | None = None
    report_markdown: str | None = None
    memory_refs: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    activities: list[AgentActivity] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)

    def record(self, step: str, agent: str, tool: str | None = None, detail: str | None = None) -> None:
        self.activities.append(AgentActivity(step=step, agent=agent, tool=tool, detail=detail))
        self.updated_at = utc_now()


class InvestigationRequest(BaseModel):
    user_id: str = "demo_user"
    input: str = Field(min_length=3)
    mode: str = "standard"


class InvestigationResponse(BaseModel):
    case_id: str
    status: CaseStatus
    claim: Claim | None = None
    verdict: VerdictLabel | None = None
    confidence: float | None = None


class CaseSummary(BaseModel):
    case_id: str
    claim: str
    verdict: str | None
    confidence: float | None
    created_at: str


class UserPreferenceUpdate(BaseModel):
    user_id: str = "demo_user"
    preferences: dict[str, Any]
