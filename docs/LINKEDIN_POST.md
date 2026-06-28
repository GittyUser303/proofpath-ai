# LinkedIn Post Draft

I built **ProofPath AI** — an agentic AI system that does not answer claims immediately.

It investigates first.

Most AI tools give confident answers, but they rarely show where the answer came from. ProofPath AI is designed around a different principle:

> Trust evidence, not vibes.

The system takes a claim, decomposes it, plans an investigation, searches for evidence, traces earlier versions of the claim, scores source quality, detects contradictions, and then generates a confidence-backed verdict.

I also integrated TraceBack-style provenance features, so the system can explore:
- where a claim may have appeared earlier,
- how the wording changed,
- which sources repeat it,
- what primary evidence exists,
- and where contradictions appear.

Tech stack:
- LLM API
- LangGraph-style workflow
- Python
- Search tools
- SQLite memory
- Source quality scoring
- TraceBack timeline
- Report generation

What makes it agentic:
- autonomous planning,
- tool selection,
- multi-step workflow,
- persistent memory,
- evidence ranking,
- contradiction detection,
- confidence scoring.

This project helped me understand that powerful AI applications should not just generate answers.

They should earn them.
