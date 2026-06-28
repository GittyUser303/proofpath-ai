from __future__ import annotations

import json
import re

from app.llm.client import LLMClient
from app.models import Claim, ClaimDomain, RiskLevel


DOMAIN_KEYWORDS = {
    ClaimDomain.HEALTH: {"cancer", "kidney", "heart", "disease", "doctor", "medical", "supplement"},
    ClaimDomain.FINANCE: {"stock", "crypto", "investment", "profit", "loan", "inflation"},
    ClaimDomain.TECH: {"ai", "model", "software", "security", "data", "algorithm"},
    ClaimDomain.POLITICS: {"election", "government", "policy", "minister", "president"},
    ClaimDomain.PRODUCT: {"brand", "product", "price", "review", "testosterone", "claim"},
    ClaimDomain.ACADEMIC: {"study", "paper", "research", "journal", "scientists"},
}


def extract_claim(text: str) -> Claim:
    """Extract a structured claim using deterministic NLP-style heuristics."""
    normalized = " ".join(text.strip().split())
    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    main_claim = max(sentences, key=len) if sentences else normalized
    main_claim = main_claim.strip(" \"'")
    lower = normalized.lower()
    domain = ClaimDomain.GENERAL
    for candidate, keywords in DOMAIN_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            domain = candidate
            break
    risk = RiskLevel.LOW
    if domain in {ClaimDomain.HEALTH, ClaimDomain.FINANCE, ClaimDomain.POLITICS}:
        risk = RiskLevel.HIGH
    elif domain in {ClaimDomain.PRODUCT, ClaimDomain.TECH}:
        risk = RiskLevel.MEDIUM
    sub_claims = [sentence.strip(" \"'") for sentence in sentences if sentence.strip()]
    entities = extract_entities(main_claim)
    return Claim(
        main_claim=main_claim,
        sub_claims=sub_claims[:5],
        domain=domain,
        risk_level=risk,
        entities=entities,
    )


async def extract_claim_with_llm(
    text: str,
    llm: LLMClient | None = None,
) -> tuple[Claim, bool]:
    """Use an LLM for nuanced claim extraction when configured, with deterministic fallback."""
    client = llm or LLMClient()
    if not client.is_configured():
        return extract_claim(text), False

    system_prompt = (
        "You are ProofPath's Claim Extraction Agent. Extract the verifiable claim from user input. "
        "Return JSON only with keys: main_claim, sub_claims, domain, risk_level, entities. "
        "Allowed domains: health, tech, finance, politics, product, academic, general. "
        "Allowed risk levels: low, medium, high."
    )
    user_prompt = json.dumps({"input": text[:6000]}, ensure_ascii=False)
    try:
        payload = await client.complete_json(system_prompt, user_prompt, temperature=0)
        claim = Claim(
            main_claim=str(payload.get("main_claim") or text).strip(),
            sub_claims=[str(item).strip() for item in payload.get("sub_claims", [])][:5],
            domain=_coerce_domain(str(payload.get("domain") or "")),
            risk_level=_coerce_risk(str(payload.get("risk_level") or "")),
            entities=[str(item).strip() for item in payload.get("entities", []) if str(item).strip()][:8],
        )
        if not claim.main_claim:
            return extract_claim(text), False
        return claim, True
    except Exception:
        return extract_claim(text), False


def extract_entities(text: str) -> list[str]:
    terms = re.findall(r"\b[A-Z][A-Za-z0-9-]{2,}\b|\b[a-zA-Z]{5,}\b", text)
    stopwords = {"there", "their", "about", "after", "before", "causes", "claim", "because"}
    entities: list[str] = []
    for term in terms:
        cleaned = term.strip()
        if cleaned.lower() not in stopwords and cleaned.lower() not in {item.lower() for item in entities}:
            entities.append(cleaned)
    return entities[:8]


def _coerce_domain(value: str) -> ClaimDomain:
    normalized = value.strip().lower()
    for domain in ClaimDomain:
        if normalized == domain.value:
            return domain
    return ClaimDomain.GENERAL


def _coerce_risk(value: str) -> RiskLevel:
    normalized = value.strip().lower()
    for risk in RiskLevel:
        if normalized == risk.value:
            return risk
    return RiskLevel.LOW
