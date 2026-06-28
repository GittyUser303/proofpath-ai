from __future__ import annotations

from app.models import Contradiction, EvidenceSource, SourceStance


def detect_contradictions(claim: str, evidence: list[EvidenceSource]) -> list[Contradiction]:
    """Detect high-level disagreement across source stances."""
    supports = [source for source in evidence if source.stance == SourceStance.SUPPORTS]
    refutes = [source for source in evidence if source.stance == SourceStance.REFUTES]
    mixed = [source for source in evidence if source.stance == SourceStance.MIXED]
    contradictions: list[Contradiction] = []

    if supports and refutes:
        contradictions.append(
            Contradiction(
                claim_part=claim,
                source_a=supports[0].title,
                source_b=refutes[0].title,
                contradiction_summary=(
                    "Retrieved evidence contains both supporting and refuting language. "
                    "The verdict should explain this disagreement rather than flatten it."
                ),
                severity="high",
            )
        )
    if mixed:
        contradictions.append(
            Contradiction(
                claim_part=claim,
                source_a=mixed[0].title,
                contradiction_summary=(
                    "At least one source describes the evidence as mixed or inconclusive, "
                    "which reduces confidence."
                ),
                severity="medium",
            )
        )
    if evidence and max(source.quality_score for source in evidence) < 0.55:
        contradictions.append(
            Contradiction(
                claim_part=claim,
                contradiction_summary=(
                    "The available evidence is mostly low-authority or weakly contextual, "
                    "so ProofPath should avoid a strong verdict."
                ),
                severity="medium",
            )
        )
    return contradictions
