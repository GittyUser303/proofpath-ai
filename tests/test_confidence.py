from app.models import EvidenceSource, SourceStance, SourceType
from app.tools.confidence import calculate_confidence


def test_confidence_is_low_without_evidence() -> None:
    confidence = calculate_confidence([], [], 0)

    assert confidence.final_score < 0.2


def test_confidence_increases_with_quality_evidence() -> None:
    evidence = [
        EvidenceSource(
            title="Official source",
            url="https://www.nih.gov/example",
            snippet="No evidence supports this claim.",
            source_type=SourceType.GOVERNMENT,
            stance=SourceStance.REFUTES,
            quality_score=0.92,
        ),
        EvidenceSource(
            title="Academic source",
            url="https://pubmed.ncbi.nlm.nih.gov/example",
            snippet="A review finds no evidence.",
            source_type=SourceType.ACADEMIC,
            stance=SourceStance.REFUTES,
            quality_score=0.88,
        ),
    ]

    confidence = calculate_confidence(evidence, [], 2)

    assert confidence.final_score > 0.65
