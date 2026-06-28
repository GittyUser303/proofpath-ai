from __future__ import annotations

from urllib.parse import urlparse

from app.models import EvidenceSource, SourceStance, SourceType


HIGH_TRUST_DOMAINS = {
    "nih.gov": SourceType.GOVERNMENT,
    "cdc.gov": SourceType.GOVERNMENT,
    "fda.gov": SourceType.GOVERNMENT,
    "who.int": SourceType.OFFICIAL_ORGANIZATION,
    "nasa.gov": SourceType.GOVERNMENT,
    "nature.com": SourceType.ACADEMIC,
    "science.org": SourceType.ACADEMIC,
    "nejm.org": SourceType.ACADEMIC,
    "thelancet.com": SourceType.ACADEMIC,
    "cochranelibrary.com": SourceType.SYSTEMATIC_REVIEW,
    "pubmed.ncbi.nlm.nih.gov": SourceType.ACADEMIC,
    "arxiv.org": SourceType.ACADEMIC,
    "semanticscholar.org": SourceType.ACADEMIC,
    "cancer.org": SourceType.OFFICIAL_ORGANIZATION,
    "mayoclinic.org": SourceType.OFFICIAL_ORGANIZATION,
    "clevelandclinic.org": SourceType.OFFICIAL_ORGANIZATION,
    "healthline.com": SourceType.EXPERT_BLOG,
    "medicalnewstoday.com": SourceType.EXPERT_BLOG,
    "snopes.com": SourceType.FACT_CHECK,
    "factcheck.org": SourceType.FACT_CHECK,
    "politifact.com": SourceType.FACT_CHECK,
    "reuters.com": SourceType.NEWS,
    "apnews.com": SourceType.NEWS,
}

LOW_TRUST_HINTS = {"forum", "reddit", "quora", "tiktok", "facebook", "instagram", "blogspot"}
MARKETING_HINTS = {"shop", "buy", "sale", "supplement", "product", "brand"}
REFUTE_TERMS = {"myth", "false", "no evidence", "unsupported", "does not", "not shown", "debunk"}
SUPPORT_TERMS = {"evidence", "supports", "shown", "associated", "causes", "increases", "reduces"}


def classify_source_type(url: str, title: str = "") -> SourceType:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    text = f"{host} {title}".lower()
    for domain, source_type in HIGH_TRUST_DOMAINS.items():
        if host.endswith(domain):
            return source_type
    if any(hint in text for hint in LOW_TRUST_HINTS):
        return SourceType.FORUM
    if any(hint in text for hint in MARKETING_HINTS):
        return SourceType.MARKETING
    if host.endswith(".edu"):
        return SourceType.ACADEMIC
    if host.endswith(".gov"):
        return SourceType.GOVERNMENT
    if any(news in host for news in ("reuters", "apnews", "bbc", "nytimes", "guardian")):
        return SourceType.NEWS
    if any(fact in text for fact in ("fact check", "fact-check", "myth vs fact", "debunk")):
        return SourceType.FACT_CHECK
    return SourceType.UNKNOWN


def infer_stance(claim: str, title: str, snippet: str) -> SourceStance:
    text = f"{title} {snippet}".lower()
    if any(term in text for term in REFUTE_TERMS):
        return SourceStance.REFUTES
    if any(term in text for term in ("mixed", "uncertain", "inconclusive", "limited evidence")):
        return SourceStance.MIXED
    if any(term in text for term in SUPPORT_TERMS):
        return SourceStance.SUPPORTS
    if any(entity.lower() in text for entity in claim.split()[:4]):
        return SourceStance.BACKGROUND
    return SourceStance.NEUTRAL


def score_source(source: EvidenceSource) -> EvidenceSource:
    """Score credibility using transparent source-type and language heuristics."""
    source_type = classify_source_type(source.url, source.title)
    score_by_type = {
        SourceType.GOVERNMENT: 0.92,
        SourceType.SYSTEMATIC_REVIEW: 0.94,
        SourceType.ACADEMIC: 0.86,
        SourceType.OFFICIAL_ORGANIZATION: 0.84,
        SourceType.FACT_CHECK: 0.74,
        SourceType.NEWS: 0.62,
        SourceType.EXPERT_BLOG: 0.52,
        SourceType.UNKNOWN: 0.42,
        SourceType.MARKETING: 0.28,
        SourceType.FORUM: 0.20,
        SourceType.SOCIAL_MEDIA: 0.16,
    }
    text = f"{source.title} {source.snippet}".lower()
    citation_bonus = 0.05 if any(term in text for term in ("doi", "study", "review", "guideline")) else 0
    sensational_penalty = 0.12 if any(term in text for term in ("shocking", "secret", "miracle", "doctors hate")) else 0
    source.source_type = source_type
    source.quality_score = min(1.0, max(0.0, score_by_type[source_type] + citation_bonus - sensational_penalty))
    return source


def score_sources(claim: str, sources: list[EvidenceSource]) -> list[EvidenceSource]:
    scored: list[EvidenceSource] = []
    for source in sources:
        source.stance = infer_stance(claim, source.title, source.snippet)
        scored.append(score_source(source))
    return sorted(scored, key=lambda item: item.quality_score, reverse=True)
