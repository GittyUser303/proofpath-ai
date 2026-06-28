import pytest

from app.agents.reasoning import reason_verdict_with_llm
from app.agents.claim_extraction import extract_claim_with_llm
from app.llm.client import LLMClient
from app.models import ClaimDomain, EvidenceSource, SourceStance, SourceType, VerdictLabel


class UnconfiguredLLM(LLMClient):
    def __init__(self) -> None:
        pass

    def is_configured(self) -> bool:
        return False


@pytest.mark.asyncio
async def test_reasoning_agent_falls_back_without_llm_key() -> None:
    evidence = [
        EvidenceSource(
            title="Official cancer myth page",
            url="https://www.cancer.gov/example",
            snippet="No evidence supports this myth.",
            source_type=SourceType.GOVERNMENT,
            stance=SourceStance.REFUTES,
            quality_score=0.92,
        )
    ]

    verdict, summary, used_llm = await reason_verdict_with_llm(evidence, [], UnconfiguredLLM())

    assert used_llm is False
    assert verdict == VerdictLabel.UNSUPPORTED
    assert "strongest retrieved sources" in summary


@pytest.mark.asyncio
async def test_claim_extraction_agent_falls_back_without_llm_key() -> None:
    claim, used_llm = await extract_claim_with_llm(
        "A viral post says drinking cold water after meals causes cancer.",
        UnconfiguredLLM(),
    )

    assert used_llm is False
    assert claim.domain == ClaimDomain.HEALTH
    assert "cancer" in claim.main_claim.lower()
