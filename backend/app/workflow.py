from __future__ import annotations

import inspect
import re
from collections.abc import Awaitable, Callable
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.claim_extraction import extract_claim_with_llm
from app.agents.planner import plan_investigation
from app.agents.reasoning import reason_verdict_with_llm
from app.memory.sqlite_memory import SQLiteMemory
from app.models import CaseStatus, InvestigationState, TracebackEvent
from app.tools.confidence import calculate_confidence
from app.tools.contradictions import detect_contradictions
from app.tools.reporting import generate_report
from app.tools.search import SearchClient, sources_from_tool_result
from app.tools.source_scoring import score_sources

ProgressCallback = Callable[[dict[str, Any]], Awaitable[None] | None]


class WorkflowRunState(TypedDict):
    state: InvestigationState
    progress_callback: ProgressCallback | None


class ProofPathWorkflow:
    """Stateful multi-step investigation workflow backed by a LangGraph StateGraph."""

    def __init__(self, search: SearchClient | None = None, memory: SQLiteMemory | None = None) -> None:
        self.search = search or SearchClient()
        self.memory = memory or SQLiteMemory()
        self.graph = self._build_graph()

    async def run(
        self,
        raw_input: str,
        user_id: str = "demo_user",
        progress_callback: ProgressCallback | None = None,
    ) -> InvestigationState:
        state = InvestigationState(user_id=user_id, raw_input=raw_input)
        try:
            result = await self.graph.ainvoke(
                {"state": state, "progress_callback": progress_callback}
            )
            state = result["state"]
        except Exception as exc:  # noqa: BLE001
            state.status = CaseStatus.FAILED
            state.errors.append(str(exc))
            state.record("Investigation failed", "Case Manager Agent", detail=str(exc))
            self.memory.save_case(state)
            await self._emit(progress_callback, state, "error")
        return state

    def _build_graph(self):
        graph = StateGraph(WorkflowRunState)
        graph.add_node("extract_claim", self._extract_claim_node)
        graph.add_node("plan_investigation", self._plan_node)
        graph.add_node("retrieve_evidence", self._retrieve_node)
        graph.add_node("traceback_search", self._traceback_node)
        graph.add_node("score_sources", self._score_node)
        graph.add_node("detect_contradictions", self._contradiction_node)
        graph.add_node("reason_verdict", self._reason_node)
        graph.add_node("score_confidence", self._confidence_node)
        graph.add_node("generate_report", self._report_node)
        graph.add_node("save_memory", self._memory_node)

        graph.set_entry_point("extract_claim")
        graph.add_edge("extract_claim", "plan_investigation")
        graph.add_edge("plan_investigation", "retrieve_evidence")
        graph.add_conditional_edges(
            "retrieve_evidence",
            self._route_after_retrieval,
            {
                "traceback_search": "traceback_search",
                "score_sources": "score_sources",
            },
        )
        graph.add_edge("traceback_search", "score_sources")
        graph.add_edge("score_sources", "detect_contradictions")
        graph.add_edge("detect_contradictions", "reason_verdict")
        graph.add_edge("reason_verdict", "score_confidence")
        graph.add_edge("score_confidence", "generate_report")
        graph.add_edge("generate_report", "save_memory")
        graph.add_edge("save_memory", END)
        return graph.compile()

    async def _extract_claim_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.status = CaseStatus.EXTRACTING_CLAIM
        state.claim, used_llm = await extract_claim_with_llm(state.raw_input)
        state.record(
            "Extracting claim",
            "LLM Claim Extraction Agent" if used_llm else "Claim Extraction Agent",
            "llm_claim_extraction" if used_llm else "deterministic_claim_extraction",
            state.claim.main_claim,
        )
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _plan_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.status = CaseStatus.PLANNING
        state.plan = plan_investigation(state.claim)
        state.selected_tools = state.plan.selected_tools
        state.record("Planning investigation", "Planner Agent", detail=state.plan.rationale)
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _retrieve_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.status = CaseStatus.SEARCHING
        evidence_results = []
        state.record(
            "Searching sources",
            "Evidence Retrieval Agent",
            "web_search",
            "Querying public web sources.",
        )
        await self._emit(run["progress_callback"], state, "activity")
        web_result = await self.search.web_search(self._evidence_query(state.claim.main_claim))
        evidence_results.extend(sources_from_tool_result(web_result))
        if not web_result.success:
            state.errors.append(web_result.error or "Web search failed.")

        if state.plan.needs_academic_search:
            state.record(
                "Searching academic sources",
                "Evidence Retrieval Agent",
                "academic_search",
                "Looking for research, medical, and institutional citations.",
            )
            await self._emit(run["progress_callback"], state, "activity")
            academic_result = await self.search.academic_search(state.claim.main_claim)
            evidence_results.extend(sources_from_tool_result(academic_result))
            if not academic_result.success:
                state.errors.append(academic_result.error or "Academic search failed.")

        state.evidence = self._deduplicate_sources(evidence_results)
        state.record(
            "Curating source candidates",
            "Evidence Retrieval Agent",
            "source_curation",
            f"Collected {len(state.evidence)} unique citation candidates for scoring.",
        )
        await self._emit(run["progress_callback"], state, "activity")
        return run

    def _route_after_retrieval(self, run: WorkflowRunState) -> str:
        return "traceback_search" if run["state"].plan.needs_traceback else "score_sources"

    async def _traceback_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.status = CaseStatus.TRACING_ORIGIN
        state.record(
            "Tracing claim origin",
            "TraceBack Agent",
            "traceback_search",
            "Running phrase, variant, myth, origin, and fact-check searches.",
        )
        await self._emit(run["progress_callback"], state, "activity")
        trace_result = await self.search.traceback_search(state.claim.main_claim)
        trace_sources = sources_from_tool_result(trace_result)
        trace_sources = score_sources(state.claim.main_claim, trace_sources)
        state.traceback_timeline = [
            TracebackEvent(
                event_date=source.published_date or self._guess_trace_date(source.title, source.snippet),
                source_title=source.title,
                source_url=source.url,
                claim_version=state.claim.main_claim,
                quality_label=source.source_type.value,
                notes=self._traceback_note(source.published_date, source.title, source.snippet),
            )
            for source in trace_sources[:5]
        ]
        state.evidence = self._deduplicate_sources([*state.evidence, *trace_sources])
        if not trace_result.success:
            state.errors.append(trace_result.error or "TraceBack search failed.")
        state.record(
            "Curating TraceBack trail",
            "TraceBack Agent",
            "traceback_curation",
            f"Prepared {len(state.traceback_timeline)} earliest-accessible candidate events.",
        )
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _score_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.status = CaseStatus.SCORING
        state.evidence = score_sources(state.claim.main_claim, state.evidence)
        state.record("Scoring reliability", "Source Quality Agent", "source_scoring")
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _contradiction_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.contradictions = detect_contradictions(state.claim.main_claim, state.evidence)
        state.record("Detecting contradictions", "Contradiction Agent", "contradiction_detection")
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _reason_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.status = CaseStatus.REASONING
        state.verdict, state.reasoning_summary, used_llm = await reason_verdict_with_llm(
            state.evidence,
            state.contradictions,
        )
        state.record(
            "Building verdict",
            "LLM Reasoning Agent" if used_llm else "Reasoning Agent",
            "llm_reasoning" if used_llm else "deterministic_reasoning",
            "Synthesized a cautious verdict from scored evidence and contradictions."
            if used_llm
            else "Used deterministic fallback because no LLM provider was configured or the LLM call failed.",
        )
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _confidence_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.confidence_breakdown = calculate_confidence(
            state.evidence,
            state.contradictions,
            len(state.traceback_timeline),
        )
        state.confidence = state.confidence_breakdown.final_score
        state.record("Calculating confidence", "Confidence Agent", "confidence_calculator")
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _report_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.report_markdown = generate_report(state)
        state.record("Generating report", "Report Generator Agent", "report_generator")
        await self._emit(run["progress_callback"], state, "activity")
        return run

    async def _memory_node(self, run: WorkflowRunState) -> WorkflowRunState:
        state = run["state"]
        state.status = CaseStatus.COMPLETED
        self.memory.save_case(state)
        state.record("Saving memory", "Case Manager Agent", "sqlite_memory")
        self.memory.save_case(state)
        await self._emit(run["progress_callback"], state, "activity")
        return run

    def _evidence_query(self, claim: str) -> str:
        return f"{claim} evidence primary source fact check"

    def _deduplicate_sources(self, sources):
        deduplicated = []
        seen_urls = set()
        for source in sources:
            if source.url in seen_urls:
                continue
            seen_urls.add(source.url)
            deduplicated.append(source)
        return deduplicated

    async def _emit(
        self,
        progress_callback: ProgressCallback | None,
        state: InvestigationState,
        event: str,
    ) -> None:
        if progress_callback is None:
            return
        payload = {
            "event": event,
            "case_id": state.case_id,
            "status": state.status.value,
            "activity": state.activities[-1].model_dump(mode="json") if state.activities else None,
            "counts": {
                "evidence": len(state.evidence),
                "traceback": len(state.traceback_timeline),
                "contradictions": len(state.contradictions),
            },
            "errors": state.errors,
        }
        result = progress_callback(payload)
        if inspect.isawaitable(result):
            await result

    def _guess_trace_date(self, title: str, snippet: str) -> str | None:
        match = re.search(r"\b(19\d{2}|20\d{2})\b", f"{title} {snippet}")
        return match.group(1) if match else None

    def _traceback_note(self, published_date: str | None, title: str, snippet: str) -> str:
        if published_date:
            return "Earliest accessible source candidate from search metadata; not guaranteed origin."
        if self._guess_trace_date(title, snippet):
            return "Year inferred from search result text; treat as a weak TraceBack clue, not verified publication metadata."
        return "Accessible source candidate found by phrase/variant search; no reliable publication date was available."
