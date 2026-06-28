from __future__ import annotations

from statistics import mean

from app.models import ConfidenceBreakdown, Contradiction, EvidenceSource, SourceStance, SourceType


def calculate_confidence(
    evidence: list[EvidenceSource],
    contradictions: list[Contradiction],
    traceback_count: int,
) -> ConfidenceBreakdown:
    """Calculate confidence from source quality, consistency, primary evidence, recency, and TraceBack clarity."""
    if not evidence:
        return ConfidenceBreakdown(
            source_quality=0.0,
            evidence_consistency=0.0,
            primary_source_strength=0.0,
            recency=0.0,
            traceback_clarity=0.0,
            contradiction_penalty=0.0,
            final_score=0.12,
            explanation="No external evidence was retrieved, so confidence remains very low.",
        )

    source_quality = mean(source.quality_score for source in evidence)
    stance_counts = {
        stance: sum(1 for source in evidence if source.stance == stance)
        for stance in SourceStance
    }
    dominant_count = max(stance_counts.values())
    evidence_consistency = dominant_count / max(1, len(evidence))
    primary_source_strength = min(
        1.0,
        sum(
            1
            for source in evidence
            if source.source_type
            in {SourceType.GOVERNMENT, SourceType.ACADEMIC, SourceType.SYSTEMATIC_REVIEW}
        )
        / 3,
    )
    recency = 0.70
    traceback_clarity = min(1.0, traceback_count / 3)
    contradiction_penalty = min(0.25, len(contradictions) * 0.08)
    weighted = (
        0.30 * source_quality
        + 0.25 * evidence_consistency
        + 0.20 * primary_source_strength
        + 0.15 * recency
        + 0.10 * traceback_clarity
        - contradiction_penalty
    )
    final_score = min(0.98, max(0.05, weighted))
    explanation = (
        "Confidence reflects source quality, agreement across retrieved evidence, presence of primary "
        "or institutional sources, recency assumptions, TraceBack clarity, and contradiction severity."
    )
    return ConfidenceBreakdown(
        source_quality=round(source_quality, 3),
        evidence_consistency=round(evidence_consistency, 3),
        primary_source_strength=round(primary_source_strength, 3),
        recency=round(recency, 3),
        traceback_clarity=round(traceback_clarity, 3),
        contradiction_penalty=round(contradiction_penalty, 3),
        final_score=round(final_score, 3),
        explanation=explanation,
    )
