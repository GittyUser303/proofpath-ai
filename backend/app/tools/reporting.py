from __future__ import annotations

from app.models import InvestigationState


def generate_report(state: InvestigationState) -> str:
    """Generate a shareable Markdown investigation report."""
    claim = state.claim.main_claim if state.claim else state.raw_input
    confidence_percent = int(round((state.confidence or 0) * 100))
    lines = [
        f"# ProofPath AI Report: {claim}",
        "",
        "## Verdict",
        f"**{state.verdict.value if state.verdict else 'Not Enough Evidence'}**",
        "",
        f"Confidence: **{confidence_percent}%**",
        "",
        "## Reasoning Summary",
        state.reasoning_summary or "ProofPath could not complete a reasoning summary.",
        "",
        "## Evidence Trail",
    ]
    if state.evidence:
        lines.extend(["", "| Source | Type | Stance | Quality |", "|---|---:|---:|---:|"])
        for source in state.evidence:
            lines.append(
                f"| [{source.title}]({source.url}) | {source.source_type.value} | "
                f"{source.stance.value} | {source.quality_score:.2f} |"
            )
    else:
        lines.append("")
        lines.append("No external sources were retrieved. The verdict is intentionally low confidence.")

    lines.extend(["", "## TraceBack Timeline"])
    if state.traceback_timeline:
        for event in state.traceback_timeline:
            date = event.event_date or "Date unknown"
            lines.append(
                f"- **{date}**: [{event.source_title}]({event.source_url}) repeated "
                f"`{event.claim_version}`. {event.notes}"
            )
    else:
        lines.append("- No earlier accessible appearances were retrieved.")

    lines.extend(["", "## Contradictions"])
    if state.contradictions:
        for contradiction in state.contradictions:
            lines.append(f"- **{contradiction.severity}**: {contradiction.contradiction_summary}")
    else:
        lines.append("- No direct contradictions were detected in the retrieved source set.")

    lines.extend(
        [
            "",
            "## Confidence Breakdown",
            state.confidence_breakdown.explanation if state.confidence_breakdown else "Unavailable.",
            "",
            "## Limitations",
            "- ProofPath reports the earliest accessible source found, not a guaranteed first origin.",
            "- Search coverage depends on configured search providers and public indexing.",
            "- Health, legal, and financial outputs are evidence summaries, not professional advice.",
        ]
    )
    return "\n".join(lines)
