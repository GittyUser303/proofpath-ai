from app.models import EvidenceSource, SourceStance, SourceType
from app.tools.source_scoring import score_sources


def test_score_sources_rewards_government_sources() -> None:
    sources = [
        EvidenceSource(
            title="Cancer myths and facts",
            url="https://www.cancer.gov/about-cancer/causes-prevention/risk/myths",
            snippet="No evidence supports this myth.",
        )
    ]

    scored = score_sources("Cold water after meals causes cancer", sources)

    assert scored[0].source_type == SourceType.GOVERNMENT
    assert scored[0].stance == SourceStance.REFUTES
    assert scored[0].quality_score > 0.8
