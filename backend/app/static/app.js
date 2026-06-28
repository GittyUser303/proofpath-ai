const samples = [
  "Drinking cold water after meals causes cancer.",
  "Creatine damages kidneys in healthy adults.",
  "This supplement increases testosterone by 300%.",
  "AI detectors can always identify AI-written text.",
];

const processSteps = [
  {
    step: "Understand the claim",
    detail: "Extract the core statement, domain, risk level, and important entities.",
    tool: "Claim extraction",
  },
  {
    step: "Plan the verification route",
    detail: "Choose whether this needs web evidence, academic evidence, TraceBack, or deeper contradiction checks.",
    tool: "Planner",
  },
  {
    step: "Collect citations",
    detail: "Search for supporting, refuting, and contextual sources without inventing missing citations.",
    tool: "Search tools",
  },
  {
    step: "Trace provenance",
    detail: "Look for earliest accessible appearances and repeated wording, without claiming absolute origin.",
    tool: "TraceBack",
  },
  {
    step: "Compare the evidence",
    detail: "Classify source reliability, stance, and contradictions across the retrieved source set.",
    tool: "Evidence scoring",
  },
  {
    step: "Write the brief",
    detail: "Produce a cautious verdict, evidence-strength label, limitations, and a shareable report.",
    tool: "Report generator",
  },
];

const state = {
  caseId: null,
  cases: [],
  activeStep: 0,
  timer: null,
  light: false,
  liveActivities: [],
};

const $ = (selector) => document.querySelector(selector);

const els = {
  userId: $("#userId"),
  caseSearch: $("#caseSearch"),
  caseList: $("#caseList"),
  caseCount: $("#caseCount"),
  claimInput: $("#claimInput"),
  fileInput: $("#fileInput"),
  sampleButton: $("#sampleButton"),
  investigateButton: $("#investigateButton"),
  themeButton: $("#themeButton"),
  runStatus: $("#runStatus"),
  workflowTitle: $("#workflowTitle"),
  workflowOrb: $("#workflowOrb"),
  processPulse: $("#processPulse"),
  verdictMetric: $("#verdictMetric"),
  confidenceMetric: $("#confidenceMetric"),
  evidenceMetric: $("#evidenceMetric"),
  traceMetric: $("#traceMetric"),
  claimTitle: $("#claimTitle"),
  downloadReport: $("#downloadReport"),
  verdictCategory: $("#verdictCategory"),
  verdictLabel: $("#verdictLabel"),
  reasoningSummary: $("#reasoningSummary"),
  confidenceLabel: $("#confidenceLabel"),
  confidenceBar: $("#confidenceBar"),
  gaugeNeedle: $("#gaugeNeedle"),
  graphNodes: $("#graphNodes"),
  sourcesPanel: $("#sourcesPanel"),
  tracePanel: $("#tracePanel"),
  contradictionPanel: $("#contradictionPanel"),
  activityList: $("#activityList"),
  qualityList: $("#qualityList"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function sourceHost(url) {
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch {
    return "source";
  }
}

function evidenceLabel(value) {
  if (value == null) return "Not checked";
  if (value >= 0.86) return "Very strong";
  if (value >= 0.71) return "Strong";
  if (value >= 0.51) return "Mixed";
  if (value >= 0.31) return "Weak";
  return "Very weak";
}

function qualityLabel(value) {
  if (value >= 0.8) return "High trust";
  if (value >= 0.65) return "Credible";
  if (value >= 0.45) return "Context only";
  if (value >= 0.3) return "Weak";
  return "Low trust";
}

function qualityClass(value) {
  if (value >= 0.65) return "good";
  if (value >= 0.4) return "warn";
  return "bad";
}

function compactClaimTitle(detail) {
  const raw = detail.claim || detail.original_input || "Claim";
  const attachmentMatch = raw.match(/Attached (?:dataset|evidence) from ([^:\n]+):?/i);
  if (attachmentMatch) {
    const beforeAttachment = raw.split(/Attached (?:dataset|evidence) from/i)[0].trim();
    return beforeAttachment || `Uploaded evidence review: ${attachmentMatch[1].trim()}`;
  }
  return raw.length > 180 ? `${raw.slice(0, 177).trim()}...` : raw;
}

function verdictCategory(confidence, verdict) {
  const verdictText = String(verdict || "").toLowerCase();
  if (verdictText.includes("misleading") || verdictText.includes("false")) return "Likely misleading";
  if (verdictText.includes("not enough")) return "Insufficient evidence";
  if (confidence >= 0.78) return "Trustable";
  if (confidence >= 0.58) return "Mostly reliable";
  if (confidence >= 0.36) return "Needs caution";
  return "Weakly supported";
}

function sourceTypeLabel(source) {
  if (source.source_type && source.source_type !== "unknown") {
    return source.source_type.replaceAll("_", " ");
  }
  const host = sourceHost(source.url);
  if (host.includes("snopes") || host.includes("factcheck") || host.includes("politifact")) return "fact check";
  if (host.endsWith(".gov")) return "government";
  if (host.includes("pubmed") || host.endsWith(".edu") || host.includes("scholar")) return "research";
  return host;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) throw new Error(await response.text());
  const contentType = response.headers.get("content-type") || "";
  return contentType.includes("application/json") ? response.json() : response.text();
}

async function uploadEvidenceFile(file) {
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);

  els.fileInput.disabled = true;
  els.runStatus.textContent = `Extracting text from ${file.name}...`;

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
    });
    const responseText = await response.text();
    let payload = {};
    try {
      payload = responseText ? JSON.parse(responseText) : {};
    } catch {
      payload = { detail: responseText };
    }
    if (!response.ok) {
      throw new Error(payload.detail || `Upload failed with status ${response.status}.`);
    }

    const extracted = (payload.extracted_text || "").trim();
    if (!extracted) {
      els.runStatus.textContent = `${file.name} was read, but no usable text was found.`;
      return;
    }

    const isCsv = file.name.toLowerCase().endsWith(".csv");
    const attachmentBlock = isCsv
      ? extracted
      : [
          "",
          `Attached evidence from ${payload.file_id || file.name}:`,
          extracted.length > 6000 ? `${extracted.slice(0, 6000)}\n[Attachment truncated for readability.]` : extracted,
        ].join("\n");
    els.claimInput.value = els.claimInput.value.trim()
      ? `${els.claimInput.value.trim()}\n\n${attachmentBlock.trim()}`
      : attachmentBlock.trim();
    els.runStatus.textContent = `${file.name} attached. Click Verify claim to investigate with this context.`;
  } catch (error) {
    els.runStatus.textContent = `Attachment failed: ${error.message}`;
  } finally {
    els.fileInput.disabled = false;
    els.fileInput.value = "";
  }
}

function renderProcess(mode = "idle", activities = []) {
  const mapped = activities.length
    ? activities.map((activity) => ({
        step: activity.step,
        detail: describeActivity(activity),
        tool: activity.tool || activity.agent,
      }))
    : processSteps;

  els.activityList.innerHTML = mapped
    .map((item, index) => {
      const active =
        (mode === "running" && index === state.activeStep) ||
        (mode === "progress" && index === mapped.length - 1);
      const done = mode === "done";
      const counts = item.counts || {};
      return `
        <article class="process-item">
          <div class="process-icon ${active ? "running" : ""} ${done ? "done" : ""}">${done ? "✓" : active ? "…" : index + 1}</div>
          <div class="process-copy">
            <strong>${escapeHtml(item.step)}</strong>
            <p>${escapeHtml(item.detail)}</p>
            <span class="process-tool">${escapeHtml(item.tool)}</span>
            ${counts.evidence ? `<span class="process-count">${counts.evidence} citations</span>` : ""}
            ${counts.traceback ? `<span class="process-count">${counts.traceback} trace events</span>` : ""}
            ${counts.contradictions ? `<span class="process-count">${counts.contradictions} cautions</span>` : ""}
          </div>
        </article>
      `;
    })
    .join("");
}

function describeActivity(activity) {
  const text = `${activity.step} ${activity.agent} ${activity.tool || ""}`.toLowerCase();
  if (text.includes("extract")) return "ProofPath identified the main claim, likely domain, entities, and risk level.";
  if (text.includes("planning")) return "The system selected which tools and evidence routes were appropriate for this case.";
  if (text.includes("curating source")) return activity.detail || "Duplicate source URLs were removed and citation candidates were prepared for scoring.";
  if (text.includes("searching")) return "Search tools collected candidate citations for support, refutation, and context.";
  if (text.includes("curating traceback")) return activity.detail || "TraceBack candidates were converted into a cautious provenance trail.";
  if (text.includes("tracing")) return "TraceBack looked for earlier accessible appearances and repeated wording.";
  if (text.includes("scoring")) return "Sources were categorized by type and usefulness instead of being trusted equally.";
  if (text.includes("contradiction")) return "The evidence set was checked for disagreement, weak leaps, and missing context.";
  if (text.includes("verdict")) return "The reasoning layer wrote a cautious conclusion from the available evidence.";
  if (text.includes("confidence")) return "The confidence label was derived from source quality, consistency, and limitations.";
  if (text.includes("report")) return "A shareable evidence brief was generated for review or citation.";
  if (text.includes("memory")) return "The case was saved so it can be reopened and compared later.";
  return activity.detail || "ProofPath recorded this step in the verification workflow.";
}

function startProcess() {
  state.activeStep = 0;
  state.liveActivities = [];
  renderProcess("progress", [
    {
      step: "Opening verification run",
      detail: "Waiting for the backend workflow to acknowledge the case and stream its first real step.",
      tool: "live stream",
    },
  ]);
  updateProcessPulse("Starting", "Opening a live connection to the verification workflow.");
  els.workflowOrb.classList.add("running");
  els.workflowOrb.textContent = "Running";
}

function stopProcess(activities) {
  if (state.timer) window.clearInterval(state.timer);
  state.timer = null;
  els.workflowOrb.classList.remove("running");
  els.workflowOrb.textContent = "Done";
  els.workflowTitle.textContent = "Verification work log";
  updateProcessPulse("Complete", "The evidence brief is ready. Review citations and limitations before trusting the claim.");
  renderProcess("done", activities);
}

function updateProcessPulse(label, message) {
  els.processPulse.innerHTML = `
    <span>${escapeHtml(label)}</span>
    <strong>${escapeHtml(message)}</strong>
  `;
}

async function loadCases() {
  try {
    state.cases = await api(`/api/cases?user_id=${encodeURIComponent(els.userId.value || "demo_user")}`);
  } catch {
    state.cases = [];
  }
  renderCases();
}

function renderCases() {
  const query = els.caseSearch.value.trim().toLowerCase();
  const filtered = state.cases.filter((item) => item.claim.toLowerCase().includes(query));
  els.caseCount.textContent = String(filtered.length);
  if (!filtered.length) {
    els.caseList.innerHTML = '<div class="empty-state">No saved investigations yet.</div>';
    return;
  }
  els.caseList.innerHTML = filtered
    .map(
      (item) => `
      <button class="case-card" data-case-id="${escapeHtml(item.case_id)}">
        <strong>${escapeHtml(item.claim).slice(0, 92)}</strong>
        <p>${escapeHtml(item.verdict || "Pending")} · ${evidenceLabel(item.confidence)}</p>
      </button>
    `,
    )
    .join("");
}

async function runInvestigation() {
  const input = els.claimInput.value.trim();
  if (!input) return;

  els.investigateButton.disabled = true;
  els.downloadReport.disabled = true;
  els.runStatus.textContent = "Checking citations and building a readable verification brief...";
  els.workflowTitle.textContent = processSteps[0].step;
  startProcess();

  try {
    const response = await fetch("/api/investigate/stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: els.userId.value || "demo_user", input, mode: "standard" }),
    });
    if (!response.ok || !response.body) {
      throw new Error(await response.text());
    }

    const finalCaseId = await consumeInvestigationStream(response.body);
    const detail = await api(`/api/cases/${encodeURIComponent(finalCaseId)}`);
    state.caseId = finalCaseId;
    renderCase(detail);
    await loadCases();
    els.runStatus.textContent = "Verification complete. Review the evidence before trusting the answer.";
    stopProcess(detail.activities || []);
  } catch (error) {
    els.runStatus.textContent = "Verification failed.";
    els.activityList.innerHTML = `<div class="empty-state">${escapeHtml(error.message)}</div>`;
    els.workflowTitle.textContent = "Needs attention";
  } finally {
    els.investigateButton.disabled = false;
  }
}

async function consumeInvestigationStream(stream) {
  const reader = stream.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalCaseId = null;

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";
    for (const line of lines) {
      if (!line.trim()) continue;
      const event = JSON.parse(line);
      if (event.event === "heartbeat") continue;
      if (event.event === "activity" && event.activity) {
        finalCaseId = event.case_id || finalCaseId;
        appendLiveActivity(event.activity, event.counts || {});
      }
      if (event.event === "complete") {
        finalCaseId = event.case_id;
      }
      if (event.event === "error") {
        finalCaseId = event.case_id || finalCaseId;
      }
    }
  }

  if (!finalCaseId) {
    throw new Error("Investigation finished without returning a case id.");
  }
  return finalCaseId;
}

function appendLiveActivity(activity, counts) {
  state.liveActivities.push({ ...activity, counts });
  els.workflowTitle.textContent = activity.step || "Working";
  els.evidenceMetric.textContent = `${counts.evidence || 0} reviewed`;
  els.traceMetric.textContent = counts.traceback ? `${counts.traceback} events` : "Tracing...";
  updateProcessPulse(activity.step || "Working", describeActivity(activity));
  renderProcess("progress", state.liveActivities);
}

async function loadCase(caseId) {
  const detail = await api(`/api/cases/${encodeURIComponent(caseId)}`);
  state.caseId = caseId;
  renderCase(detail);
  stopProcess(detail.activities || []);
  els.runStatus.textContent = "Loaded saved verification brief.";
}

function renderCase(detail) {
  const confidence = detail.confidence || 0;
  els.verdictMetric.textContent = detail.verdict || "Not enough evidence";
  els.confidenceMetric.textContent = evidenceLabel(confidence);
  els.evidenceMetric.textContent = `${detail.sources?.length || 0} reviewed`;
  els.traceMetric.textContent = detail.traceback_timeline?.length ? `${detail.traceback_timeline.length} events` : "No origin found";
  els.claimTitle.textContent = compactClaimTitle(detail);
  els.claimTitle.title = detail.claim || detail.original_input || "Claim";
  els.verdictCategory.textContent = verdictCategory(confidence, detail.verdict);
  els.verdictLabel.textContent = detail.verdict || "Not enough evidence";
  els.reasoningSummary.textContent = detail.reasoning_summary || "No reasoning summary available.";
  els.confidenceLabel.textContent = `${evidenceLabel(confidence)} evidence strength`;
  els.confidenceBar.style.width = `${Math.max(8, Math.round(confidence * 100))}%`;
  els.gaugeNeedle.style.transform = `translateX(-50%) rotate(${Math.round(-84 + confidence * 168)}deg)`;
  els.downloadReport.disabled = false;

  renderGraph(detail.sources || []);
  renderSources(detail.sources || []);
  renderTraceback(detail.traceback_timeline || []);
  renderContradictions(detail.contradictions || [], detail.sources || []);
  renderQuality(detail.sources || []);
}

function renderGraph(sources) {
  const graphSources = sources.length ? sources.slice(0, 5) : [
    { title: "Authority citation", source_type: "government", stance: "pending", quality_score: 0.82, url: "#" },
    { title: "Research citation", source_type: "academic", stance: "pending", quality_score: 0.76, url: "#" },
    { title: "TraceBack candidate", source_type: "traceback", stance: "pending", quality_score: 0.55, url: "#" },
  ];
  els.graphNodes.innerHTML = graphSources
    .map(
      (source, index) => `
      <article class="graph-node" data-source-index="${index}" style="animation-delay:${index * 65}ms">
        <button class="graph-node-main" type="button" data-source-index="${index}" aria-label="Inspect ${escapeHtml(source.title)}">
          <span class="source-rank">${String(index + 1).padStart(2, "0")}</span>
          <span>
            <span class="graph-meta">
              <span class="badge">${escapeHtml(source.stance || "neutral")}</span>
              <span class="badge ${qualityClass(source.quality_score || 0)}">${escapeHtml(qualityLabel(source.quality_score || 0))}</span>
            </span>
            <strong>${escapeHtml(source.title).slice(0, 72)}</strong>
            <small>${escapeHtml(sourceTypeLabel(source))} · ${escapeHtml(sourceHost(source.url))}</small>
          </span>
        </button>
        <div class="graph-actions">
          <button class="mini-action" type="button" data-source-index="${index}">Inspect</button>
          <a class="mini-action" href="${escapeHtml(source.url || "#")}" target="_blank" rel="noreferrer">Open ↗</a>
        </div>
      </article>
    `,
    )
    .join("");
}

function renderSources(sources) {
  if (!sources.length) {
    els.sourcesPanel.innerHTML = '<div class="empty-state">No external citations retrieved.</div>';
    return;
  }
  els.sourcesPanel.innerHTML = sources
    .slice(0, 10)
    .map(
      (source, index) => `
      <article class="source-card" data-source-index="${index}">
        <div>
          <span class="badge">${escapeHtml(sourceTypeLabel(source))}</span>
          <span class="badge">${escapeHtml(source.stance || "neutral")}</span>
          <span class="badge ${qualityClass(source.quality_score || 0)}">${escapeHtml(qualityLabel(source.quality_score || 0))}</span>
        </div>
        <a href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer" title="Open citation">${escapeHtml(source.title)} ↗</a>
        <p>${escapeHtml(source.snippet || "No snippet available.").slice(0, 300)}</p>
      </article>
    `,
    )
    .join("");
}

function activateTab(panelId) {
  document.querySelectorAll(".tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.tab === panelId));
  document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.toggle("active", panel.id === panelId));
}

function inspectSource(index) {
  activateTab("sourcesPanel");
  document.querySelectorAll(".source-card.selected-source").forEach((card) => card.classList.remove("selected-source"));
  const target = document.querySelector(`.source-card[data-source-index="${index}"]`);
  if (!target) return;
  target.classList.remove("selected-source");
  window.requestAnimationFrame(() => {
    target.classList.add("selected-source");
    target.scrollIntoView({ behavior: "smooth", block: "center" });
  });
}

function renderTraceback(events) {
  if (!events.length) {
    els.tracePanel.innerHTML = '<div class="empty-state">No earlier accessible appearances were found. This does not prove the claim has no origin; it only means this run did not retrieve one.</div>';
    return;
  }
  els.tracePanel.innerHTML = events
    .map(
      (event) => `
      <article class="source-card">
        <span class="badge">${escapeHtml(event.event_date || "date unknown")}</span>
        <a href="${escapeHtml(event.source_url)}" target="_blank" rel="noreferrer" title="Open TraceBack citation">${escapeHtml(event.source_title)} ↗</a>
        <p>${escapeHtml(event.notes)}</p>
      </article>
    `,
    )
    .join("");
}

function findSourceByTitle(sources, title) {
  if (!title) return null;
  const normalized = title.trim().toLowerCase();
  return sources.find((source) => (source.title || "").trim().toLowerCase() === normalized) || null;
}

function renderMentionedSource(title, sources) {
  if (!title) return "";
  const source = findSourceByTitle(sources, title);
  const host = source ? sourceHost(source.url) : "retrieved evidence";
  const sourceType = source ? sourceTypeLabel(source) : "source";
  const trust = source ? qualityLabel(source.quality_score || 0) : "Referenced";
  const content = `
    <span class="mention-title">${escapeHtml(title)}</span>
    <span class="mention-meta">${escapeHtml(sourceType)} · ${escapeHtml(host)} · ${escapeHtml(trust)}</span>
  `;
  if (!source?.url) {
    return `<span class="mentioned-source">${content}</span>`;
  }
  return `<a class="mentioned-source" href="${escapeHtml(source.url)}" target="_blank" rel="noreferrer">${content}<span class="mention-open">Open ↗</span></a>`;
}

function renderContradictions(items, sources = []) {
  if (!items.length) {
    els.contradictionPanel.innerHTML = '<div class="empty-state">No direct contradictions were detected in this retrieved source set.</div>';
    return;
  }
  els.contradictionPanel.innerHTML = items
    .map(
      (item) => {
        const mentionedSources = [item.source_a, item.source_b]
          .filter(Boolean)
          .map((title) => renderMentionedSource(title, sources))
          .join("");
        return `
      <article class="source-card">
        <span class="badge warn">${escapeHtml(item.severity)}</span>
        <strong>Evidence caution</strong>
        <p>${escapeHtml(item.contradiction_summary)}</p>
        ${
          mentionedSources
            ? `<div class="mentioned-sources"><span>Sources mentioned</span>${mentionedSources}</div>`
            : '<div class="mentioned-sources muted-note">No single source was isolated for this caution; it comes from the overall retrieved evidence set.</div>'
        }
      </article>
    `;
      },
    )
    .join("");
}

function renderQuality(sources) {
  const ranked = [...sources].sort((a, b) => b.quality_score - a.quality_score).slice(0, 5);
  if (!ranked.length) {
    els.qualityList.innerHTML = '<div class="empty-state">Citation reliability appears after source retrieval.</div>';
    return;
  }
  els.qualityList.innerHTML = ranked
    .map((source) => {
      const value = Math.max(8, Math.round((source.quality_score || 0) * 100));
      return `
        <div class="quality-row">
          <div class="quality-top">
            <strong>${escapeHtml(source.title).slice(0, 52)}</strong>
            <span>${escapeHtml(qualityLabel(source.quality_score || 0))}</span>
          </div>
          <div class="quality-bar"><div style="width:${value}%"></div></div>
        </div>
      `;
    })
    .join("");
}

async function downloadReport() {
  if (!state.caseId) return;
  const report = await api(`/api/report/${encodeURIComponent(state.caseId)}`);
  const blob = new Blob([report], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${state.caseId}_proofpath_report.md`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function toggleTheme() {
  state.light = !state.light;
  document.body.classList.toggle("light", state.light);
  els.themeButton.textContent = state.light ? "Dark" : "Light";
}

document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    activateTab(button.dataset.tab);
  });
});

els.graphNodes.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (link) return;
  const trigger = event.target.closest("[data-source-index]");
  if (!trigger) return;
  inspectSource(trigger.dataset.sourceIndex);
});

els.sampleButton.addEventListener("click", () => {
  els.claimInput.value = samples[Math.floor(Math.random() * samples.length)];
});
els.fileInput.addEventListener("change", (event) => {
  uploadEvidenceFile(event.target.files?.[0]);
});
els.investigateButton.addEventListener("click", runInvestigation);
els.downloadReport.addEventListener("click", downloadReport);
els.themeButton.addEventListener("click", toggleTheme);
els.caseSearch.addEventListener("input", renderCases);
els.userId.addEventListener("change", loadCases);
els.caseList.addEventListener("click", (event) => {
  const card = event.target.closest("[data-case-id]");
  if (card) loadCase(card.dataset.caseId);
});

renderProcess("idle");
renderGraph([]);
renderQuality([]);
loadCases();

// Reveal cards on scroll (visual-only addition, no app logic touched above)
const cardRevealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = "1";
        entry.target.style.transform = "translateY(0)";
        cardRevealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.1 },
);

document.querySelectorAll(".card").forEach((card) => {
  card.style.opacity = "0";
  card.style.transform = "translateY(24px)";
  card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
  cardRevealObserver.observe(card);
});
