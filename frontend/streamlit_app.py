from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.memory.sqlite_memory import SQLiteMemory  # noqa: E402
from app.workflow import ProofPathWorkflow  # noqa: E402


st.set_page_config(
    page_title="ProofPath AI",
    page_icon="PP",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@500;600;700;800&display=swap');

:root {
  --bg: #090b0f;
  --panel: rgba(18, 22, 30, 0.82);
  --panel-strong: #121720;
  --line: rgba(135, 156, 179, 0.18);
  --line-hot: rgba(76, 201, 240, 0.42);
  --text: #f5f7fb;
  --muted: #9aa8b6;
  --soft: #c7d0db;
  --cyan: #4cc9f0;
  --green: #45d483;
  --amber: #f8c14a;
  --red: #ff6b6b;
}

* { box-sizing: border-box; }

.stApp {
  background:
    radial-gradient(circle at 18% 4%, rgba(76, 201, 240, 0.14), transparent 32%),
    radial-gradient(circle at 88% 18%, rgba(69, 212, 131, 0.10), transparent 28%),
    linear-gradient(180deg, #090b0f 0%, #10141c 58%, #090b0f 100%) !important;
  color: var(--text) !important;
}

[data-testid="stAppViewBlockContainer"] {
  max-width: 1500px !important;
  padding: 2rem 2.4rem 3rem !important;
}

[data-testid="stSidebar"] {
  background: rgba(10, 13, 18, 0.96) !important;
  border-right: 1px solid var(--line) !important;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
h1, h2, h3 {
  font-family: 'Sora', sans-serif !important;
  color: var(--text) !important;
}

html, body, [class*="css"], p, li, label, div {
  font-family: 'Inter', sans-serif;
}

.hero {
  border: 1px solid var(--line);
  background:
    linear-gradient(135deg, rgba(18, 22, 30, 0.92), rgba(10, 13, 18, 0.80)),
    linear-gradient(90deg, rgba(76, 201, 240, 0.08), rgba(69, 212, 131, 0.05));
  border-radius: 10px;
  padding: 1.45rem 1.55rem;
  box-shadow: 0 18px 45px rgba(0,0,0,0.34);
  margin-bottom: 1rem;
}

.eyebrow {
  color: var(--cyan);
  text-transform: uppercase;
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.12em;
  margin-bottom: 0.45rem;
}

.hero-title {
  font-family: 'Sora', sans-serif;
  font-size: 2.5rem;
  line-height: 1.05;
  font-weight: 800;
  letter-spacing: 0;
  margin: 0;
}

.hero-copy {
  color: var(--muted);
  font-size: 1rem;
  line-height: 1.55;
  max-width: 860px;
  margin-top: 0.65rem;
}

.panel {
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 10px;
  padding: 1rem;
  box-shadow: 0 12px 34px rgba(0,0,0,0.26);
}

.panel-title {
  font-family: 'Sora', sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 0.8rem;
  color: var(--text);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.75rem;
  margin: 0.95rem 0;
}

.metric {
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.035);
  border-radius: 8px;
  padding: 0.9rem;
  min-height: 86px;
}

.metric span {
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.metric strong {
  display: block;
  color: var(--text);
  font-family: 'Sora', sans-serif;
  font-size: 1.45rem;
  margin-top: 0.35rem;
}

.verdict-box {
  border: 1px solid var(--line-hot);
  background: linear-gradient(135deg, rgba(76, 201, 240, 0.10), rgba(69, 212, 131, 0.06));
  border-radius: 10px;
  padding: 1rem;
  margin: 0.9rem 0;
}

.verdict-box strong {
  font-family: 'Sora', sans-serif;
  font-size: 1.1rem;
}

.verdict-box p {
  color: var(--soft);
  margin: 0.65rem 0 0;
  line-height: 1.55;
}

.activity, .source, .timeline, .case-row {
  border: 1px solid var(--line);
  background: rgba(255,255,255,0.035);
  border-radius: 8px;
  padding: 0.82rem;
  margin-bottom: 0.65rem;
}

.activity {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
}

.dot {
  width: 9px;
  height: 9px;
  background: var(--green);
  border-radius: 99px;
  margin-top: 0.35rem;
  box-shadow: 0 0 18px rgba(69, 212, 131, 0.75);
  flex: 0 0 auto;
}

.chip {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 0.18rem 0.5rem;
  color: var(--muted);
  font-size: 0.72rem;
  font-weight: 700;
  margin: 0.25rem 0.25rem 0.25rem 0;
}

.source a, .timeline a {
  color: var(--cyan) !important;
  text-decoration: none !important;
  font-weight: 700;
}

.source p, .timeline p, .case-row p {
  color: var(--muted);
  line-height: 1.48;
  margin: 0.45rem 0 0;
  font-size: 0.9rem;
}

.case-row strong {
  color: var(--text);
  font-size: 0.88rem;
}

.case-row span {
  color: var(--muted);
  font-size: 0.78rem;
}

textarea, [data-testid="stTextInput"] input {
  background: rgba(255,255,255,0.045) !important;
  color: var(--text) !important;
  border: 1px solid var(--line) !important;
  border-radius: 8px !important;
}

textarea:focus, [data-testid="stTextInput"] input:focus {
  border-color: var(--cyan) !important;
  box-shadow: 0 0 0 4px rgba(76, 201, 240, 0.14) !important;
}

[data-testid="stButton"] > button,
[data-testid="baseButton-secondary"] {
  border-radius: 8px !important;
  border: 1px solid var(--line) !important;
  background: rgba(255,255,255,0.045) !important;
  color: var(--text) !important;
  font-weight: 700 !important;
}

[data-testid="baseButton-primary"],
div.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #4cc9f0 0%, #45d483 100%) !important;
  color: #071014 !important;
  border: none !important;
  border-radius: 8px !important;
  font-family: 'Sora', sans-serif !important;
  font-weight: 800 !important;
  box-shadow: 0 10px 28px rgba(76, 201, 240, 0.24) !important;
}

[data-testid="baseButton-primary"]:hover,
div.stButton > button[kind="primary"]:hover {
  transform: translateY(-1px);
  box-shadow: 0 14px 34px rgba(69, 212, 131, 0.25) !important;
}

[data-testid="stProgress"] > div > div > div {
  background: linear-gradient(90deg, #4cc9f0, #45d483) !important;
}

.stAlert {
  border-radius: 8px !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def run_investigation(claim: str, user_id: str):
    workflow = ProofPathWorkflow()
    return asyncio.run(workflow.run(raw_input=claim, user_id=user_id))


def confidence_label(score: float | None) -> str:
    percent = int(round((score or 0) * 100))
    if percent >= 86:
        return "Very strong"
    if percent >= 71:
        return "Strong"
    if percent >= 51:
        return "Mixed"
    if percent >= 31:
        return "Weak"
    return "Very uncertain"


memory = SQLiteMemory()

with st.sidebar:
    st.markdown("## ProofPath AI")
    user_id = st.text_input("User", value="demo_user", label_visibility="collapsed")
    st.caption("Evidence-first investigations")
    st.divider()
    st.markdown("### Previous Cases")
    cases = memory.list_cases(user_id=user_id)
    if cases:
        for case in cases[:8]:
            score = "-" if case.confidence is None else f"{round(case.confidence * 100)}%"
            st.markdown(
                f"""
                <div class="case-row">
                  <strong>{case.claim[:72]}</strong>
                  <p>{case.verdict or 'Pending'} · {score}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.caption("No saved investigations yet.")

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Agentic verification platform</div>
      <h1 class="hero-title">Trust evidence, not vibes.</h1>
      <div class="hero-copy">
        ProofPath AI investigates claims through planning, source retrieval, TraceBack provenance,
        contradiction checks, confidence scoring, and persistent case memory.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

input_col, insight_col = st.columns([1.2, 0.8], gap="large")

with input_col:
    st.markdown('<div class="panel-title">Start An Investigation</div>', unsafe_allow_html=True)
    claim_input = st.text_area(
        "Claim",
        value="Drinking cold water after meals causes cancer.",
        height=135,
        label_visibility="collapsed",
        placeholder="Paste a viral claim, product promise, health myth, or AI-generated answer...",
    )
    example_cols = st.columns(3)
    examples = [
        "Creatine damages kidneys in healthy adults.",
        "This supplement increases testosterone by 300%.",
        "AI detectors can always identify AI-written text.",
    ]
    for col, example in zip(example_cols, examples, strict=True):
        with col:
            if st.button(example, use_container_width=True):
                claim_input = example
    submit = st.button("Build Evidence Trail", type="primary", use_container_width=True)

with insight_col:
    st.markdown(
        """
        <div class="panel">
          <div class="panel-title">What You Will See</div>
          <div class="activity"><div class="dot"></div><div><strong>Current agent</strong><p>Every step exposes who is acting and which tool is being used.</p></div></div>
          <div class="activity"><div class="dot"></div><div><strong>Evidence locker</strong><p>Sources are scored by type, stance, quality, and usefulness.</p></div></div>
          <div class="activity"><div class="dot"></div><div><strong>TraceBack trail</strong><p>Origins are shown cautiously as earliest accessible candidates.</p></div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

state = None

if submit and claim_input.strip():
    with st.status("Building evidence trail...", expanded=True) as status:
        state = run_investigation(claim_input, user_id)
        for activity in state.activities:
            tool = f" using {activity.tool}" if activity.tool else ""
            st.write(f"{activity.agent}: {activity.step}{tool}")
        status.update(label="Verdict earned.", state="complete")
    st.session_state["latest_case_id"] = state.case_id

if state:
    result_col, locker_col = st.columns([1.05, 0.95], gap="large")

    with result_col:
        verdict = state.verdict.value if state.verdict else "Not Enough Evidence"
        confidence = int(round((state.confidence or 0) * 100))
        domain = state.claim.domain.value if state.claim else "general"
        risk = state.claim.risk_level.value if state.claim else "unknown"
        st.markdown(
            f"""
            <div class="metric-grid">
              <div class="metric"><span>Verdict</span><strong>{verdict}</strong></div>
              <div class="metric"><span>Confidence</span><strong>{confidence}%</strong></div>
              <div class="metric"><span>Risk</span><strong>{risk.title()}</strong></div>
            </div>
            <div class="verdict-box">
              <strong>{state.claim.main_claim if state.claim else state.raw_input}</strong>
              <p>{state.reasoning_summary or ''}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(state.confidence or 0, text=f"{confidence_label(state.confidence)} evidence")

        st.markdown("### Investigation Plan")
        if state.plan:
            for step in state.plan.steps:
                st.markdown(f"- {step}")
            st.caption(state.plan.rationale)

        if state.confidence_breakdown:
            with st.expander("Confidence Breakdown", expanded=False):
                st.write(state.confidence_breakdown.model_dump())

        st.download_button(
            "Download Markdown Report",
            data=state.report_markdown or "",
            file_name=f"{state.case_id}_proofpath_report.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with locker_col:
        st.markdown("### Agent Activity")
        for activity in state.activities:
            tool_chip = f'<span class="chip">{activity.tool}</span>' if activity.tool else ""
            st.markdown(
                f"""
                <div class="activity">
                  <div class="dot"></div>
                  <div>
                    <strong>{activity.step}</strong><br>
                    <span class="chip">{activity.agent}</span>{tool_chip}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        tab_sources, tab_trace, tab_contra = st.tabs(["Evidence", "TraceBack", "Contradictions"])

        with tab_sources:
            if state.evidence:
                for source in state.evidence[:10]:
                    st.markdown(
                        f"""
                        <div class="source">
                          <a href="{source.url}" target="_blank">{source.title}</a><br>
                          <span class="chip">{source.source_type.value}</span>
                          <span class="chip">{source.stance.value}</span>
                          <span class="chip">quality {source.quality_score:.2f}</span>
                          <p>{source.snippet[:260]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No external evidence retrieved.")

        with tab_trace:
            if state.traceback_timeline:
                for event in state.traceback_timeline:
                    st.markdown(
                        f"""
                        <div class="timeline">
                          <strong>{event.event_date or 'Date unknown'}</strong><br>
                          <a href="{event.source_url}" target="_blank">{event.source_title}</a>
                          <p>{event.notes}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("No earlier accessible appearances found.")

        with tab_contra:
            if state.contradictions:
                for contradiction in state.contradictions:
                    st.warning(f"{contradiction.severity.title()}: {contradiction.contradiction_summary}")
            else:
                st.success("No direct contradictions detected in the retrieved source set.")
else:
    st.markdown(
        """
        <div class="metric-grid">
          <div class="metric"><span>Workflow</span><strong>10 agents</strong></div>
          <div class="metric"><span>Memory</span><strong>SQLite</strong></div>
          <div class="metric"><span>Output</span><strong>Report</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
