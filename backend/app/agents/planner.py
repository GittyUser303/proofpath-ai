from __future__ import annotations

from app.models import Claim, ClaimDomain, InvestigationPlan, RiskLevel


def plan_investigation(claim: Claim) -> InvestigationPlan:
    """Choose tools and steps based on claim type and risk."""
    steps = [
        "Search for high-quality evidence",
        "Score source reliability",
        "Detect contradictions",
        "Calculate confidence",
        "Generate evidence report",
    ]
    tools = ["web_search", "source_scoring", "contradiction_detection", "confidence_calculator"]
    needs_traceback = claim.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH} or claim.domain in {
        ClaimDomain.HEALTH,
        ClaimDomain.PRODUCT,
        ClaimDomain.POLITICS,
        ClaimDomain.GENERAL,
    }
    needs_academic = claim.domain in {ClaimDomain.HEALTH, ClaimDomain.ACADEMIC, ClaimDomain.TECH}
    if needs_academic:
        steps.insert(1, "Search academic or institutional sources")
        tools.append("academic_search")
    if needs_traceback:
        steps.insert(2, "Trace earliest accessible appearances and claim variants")
        tools.append("traceback_search")
    rationale = (
        f"The claim is classified as {claim.domain.value} with {claim.risk_level.value} risk, "
        "so the workflow prioritizes reliable evidence, provenance, and uncertainty."
    )
    return InvestigationPlan(
        steps=steps,
        selected_tools=tools,
        needs_traceback=needs_traceback,
        needs_academic_search=needs_academic,
        rationale=rationale,
    )
