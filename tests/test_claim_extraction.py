from app.agents.claim_extraction import extract_claim
from app.models import ClaimDomain, RiskLevel


def test_extract_claim_classifies_health_risk() -> None:
    claim = extract_claim("This viral post says drinking cold water after meals causes cancer.")

    assert claim.domain == ClaimDomain.HEALTH
    assert claim.risk_level == RiskLevel.HIGH
    assert "cancer" in claim.main_claim.lower()
