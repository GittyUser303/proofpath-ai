from __future__ import annotations

import json

from app.llm.client import LLMClient
from app.models import Contradiction, EvidenceSource, SourceStance, VerdictLabel


def reason_verdict(evidence: list[EvidenceSource]) -> tuple[VerdictLabel, str]:
    """Produce a cautious verdict from retrieved and scored evidence."""
    if not evidence:
        return (
            VerdictLabel.NOT_ENOUGH_EVIDENCE,
            "ProofPath could not retrieve external evidence. The system refuses to guess and marks the claim as unresolved.",
        )

    high_quality = [source for source in evidence if source.quality_score >= 0.70]
    refutes = [source for source in high_quality if source.stance == SourceStance.REFUTES]
    supports = [source for source in high_quality if source.stance == SourceStance.SUPPORTS]
    mixed = [source for source in evidence if source.stance == SourceStance.MIXED]

    if refutes and not supports:
        verdict = VerdictLabel.UNSUPPORTED
        summary = (
            "The strongest retrieved sources lean against the claim or describe it as unsupported. "
            "Lower-quality repetition should not be treated as proof."
        )
    elif supports and not refutes and len(supports) >= 2:
        verdict = VerdictLabel.MOSTLY_SUPPORTED
        summary = (
            "Multiple higher-quality sources appear to support the claim, but ProofPath still treats the verdict "
            "as evidence-weighted rather than absolute."
        )
    elif supports and refutes:
        verdict = VerdictLabel.MIXED_EVIDENCE
        summary = (
            "High-quality retrieved sources disagree. The claim needs careful qualification and should not be "
            "shared without context."
        )
    elif mixed:
        verdict = VerdictLabel.MIXED_EVIDENCE
        summary = "At least one source frames the evidence as limited or inconclusive."
    else:
        verdict = VerdictLabel.NOT_ENOUGH_EVIDENCE
        summary = (
            "The retrieved source set does not contain enough high-quality support or refutation for a strong verdict."
        )
    return verdict, summary


async def reason_verdict_with_llm(
    evidence: list[EvidenceSource],
    contradictions: list[Contradiction],
    llm: LLMClient | None = None,
) -> tuple[VerdictLabel, str, bool]:
    """Use an LLM for final synthesis when configured, otherwise use the deterministic fallback."""
    client = llm or LLMClient()
    if not client.is_configured():
        verdict, summary = reason_verdict(evidence)
        return verdict, summary, False

    system_prompt = (
        "You are ProofPath's Reasoning Agent. Produce cautious evidence-weighted verdicts. "
        "Never invent sources. Use only the supplied evidence. Return JSON only with keys "
        "verdict and reasoning_summary."
    )
    user_prompt = json.dumps(
        {
            "allowed_verdicts": [item.value for item in VerdictLabel],
            "evidence": [
                {
                    "title": source.title,
                    "url": source.url,
                    "snippet": source.snippet[:700],
                    "source_type": source.source_type.value,
                    "stance": source.stance.value,
                    "quality_score": source.quality_score,
                }
                for source in evidence[:12]
            ],
            "contradictions": [
                {
                    "severity": item.severity,
                    "source_a": item.source_a,
                    "source_b": item.source_b,
                    "summary": item.contradiction_summary,
                }
                for item in contradictions[:6]
            ],
            "instructions": (
                "Choose one allowed verdict. Explain support, refutation, uncertainty, and limitations "
                "in two concise sentences. If evidence is weak or missing, choose Not Enough Evidence."
            ),
        },
        ensure_ascii=False,
    )

    try:
        payload = await client.complete_json(system_prompt, user_prompt, temperature=0.05)
        verdict_text = str(payload.get("verdict") or VerdictLabel.NOT_ENOUGH_EVIDENCE.value)
        summary = str(payload.get("reasoning_summary") or "").strip()
        verdict = _coerce_verdict(verdict_text)
        if not summary:
            _, summary = reason_verdict(evidence)
        return verdict, summary, True
    except Exception:
        verdict, summary = reason_verdict(evidence)
        return verdict, summary, False


def _coerce_verdict(value: str) -> VerdictLabel:
    normalized = value.strip().lower().replace("_", " ")
    for verdict in VerdictLabel:
        if normalized == verdict.value.lower():
            return verdict
    if "mostly" in normalized and "support" in normalized:
        return VerdictLabel.MOSTLY_SUPPORTED
    if "support" in normalized:
        return VerdictLabel.SUPPORTED
    if "mixed" in normalized:
        return VerdictLabel.MIXED_EVIDENCE
    if "mislead" in normalized:
        return VerdictLabel.MISLEADING
    if "false" in normalized:
        return VerdictLabel.FALSE
    if "unsupported" in normalized:
        return VerdictLabel.UNSUPPORTED
    return VerdictLabel.NOT_ENOUGH_EVIDENCE
