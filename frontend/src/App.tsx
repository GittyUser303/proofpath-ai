import { AnimatePresence, motion } from "framer-motion";
import {
  Activity,
  AlertTriangle,
  ArrowUpRight,
  Brain,
  CheckCircle2,
  Clock3,
  Download,
  FileUp,
  Gauge,
  GitBranch,
  History,
  Loader2,
  Moon,
  Network,
  PanelRight,
  Search,
  ShieldCheck,
  Sparkles,
  Sun,
  UploadCloud,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { getCase, getReport, investigate, listCases } from "./lib/api";
import { Badge, Button, Card } from "./components/ui";
import type { Activity as AgentActivity, CaseDetail, CaseSummary, Source } from "./types";
import { cn } from "./lib/utils";

const samples = [
  "Drinking cold water after meals causes cancer.",
  "Creatine damages kidneys in healthy adults.",
  "This supplement increases testosterone by 300%.",
  "AI detectors can always identify AI-written text.",
];

const runningSteps = [
  "Extracting claim",
  "Planning investigation",
  "Searching sources",
  "Tracing provenance",
  "Scoring reliability",
  "Detecting contradictions",
  "Calculating confidence",
  "Generating report",
];

type Theme = "dark" | "light";

export function App() {
  const [userId, setUserId] = useState("demo_user");
  const [claim, setClaim] = useState(samples[0]);
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [caseFilter, setCaseFilter] = useState("");
  const [activeCase, setActiveCase] = useState<CaseDetail | null>(null);
  const [isInvestigating, setIsInvestigating] = useState(false);
  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [theme, setTheme] = useState<Theme>("dark");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    refreshCases();
  }, [userId]);

  useEffect(() => {
    if (!isInvestigating) return;
    const timer = window.setInterval(() => {
      setActiveStepIndex((current) => (current + 1) % runningSteps.length);
    }, 900);
    return () => window.clearInterval(timer);
  }, [isInvestigating]);

  async function refreshCases() {
    try {
      const payload = await listCases(userId);
      setCases(payload);
    } catch {
      setCases([]);
    }
  }

  async function startInvestigation() {
    const input = claim.trim();
    if (!input) return;
    setError(null);
    setIsInvestigating(true);
    setActiveStepIndex(0);
    try {
      const response = await investigate(userId, input);
      const detail = await getCase(response.case_id);
      setActiveCase(detail);
      await refreshCases();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Investigation failed.");
    } finally {
      setIsInvestigating(false);
    }
  }

  async function openCase(caseId: string) {
    setError(null);
    const detail = await getCase(caseId);
    setActiveCase(detail);
  }

  async function downloadReport() {
    if (!activeCase) return;
    const report = await getReport(activeCase.case_id);
    const blob = new Blob([report], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `${activeCase.case_id}_proofpath_report.md`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  const filteredCases = cases.filter((item) =>
    item.claim.toLowerCase().includes(caseFilter.toLowerCase()),
  );

  const confidence = Math.round((activeCase?.confidence ?? 0) * 100);
  const topSources = activeCase?.sources?.slice(0, 6) ?? [];

  return (
    <div className={cn(theme === "light" && "bg-slate-100 text-slate-950")}>
      <div
        className={cn(
          "glass-grid min-h-screen",
          theme === "light"
            ? "bg-[radial-gradient(circle_at_16%_6%,rgba(14,165,233,0.18),transparent_32%),linear-gradient(180deg,#f8fafc,#e2e8f0)] text-slate-950"
            : "text-slate-50",
        )}
      >
        <div className="grid min-h-screen grid-cols-[320px_minmax(0,1fr)] max-xl:grid-cols-1">
          <aside
            className={cn(
              "border-r border-white/10 bg-black/25 p-5 backdrop-blur-2xl max-xl:border-b max-xl:border-r-0",
              theme === "light" && "border-slate-300 bg-white/70",
            )}
          >
            <div className="mb-7 flex items-center gap-3">
              <div className="grid size-11 place-items-center rounded-xl bg-gradient-to-br from-cyan to-mint font-display font-black text-obsidian shadow-glow">
                PP
              </div>
              <div>
                <div className="font-display text-lg font-bold">ProofPath AI</div>
                <div className={muted(theme)}>Evidence operating system</div>
              </div>
            </div>

            <div className="mb-5 grid gap-2">
              <label className={label(theme)}>Investigator</label>
              <input
                value={userId}
                onChange={(event) => setUserId(event.target.value)}
                className={inputClass(theme)}
              />
            </div>

            <div className="mb-5 grid gap-2">
              <label className={label(theme)}>Search History</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-slate-500" />
                <input
                  value={caseFilter}
                  onChange={(event) => setCaseFilter(event.target.value)}
                  placeholder="Find investigation..."
                  className={cn(inputClass(theme), "pl-9")}
                />
              </div>
            </div>

            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2 font-display font-bold">
                <History className="size-4 text-cyan" />
                Previous Cases
              </div>
              <Badge>{filteredCases.length}</Badge>
            </div>

            <div className="grid max-h-[calc(100vh-260px)] gap-3 overflow-auto pr-1 max-xl:max-h-72">
              {filteredCases.length ? (
                filteredCases.map((item) => (
                  <button
                    key={item.case_id}
                    onClick={() => openCase(item.case_id)}
                    className={cn(
                      "rounded-xl border border-white/10 bg-white/[0.035] p-3 text-left transition hover:border-cyan/50 hover:bg-cyan/10",
                      theme === "light" && "border-slate-200 bg-white hover:bg-sky-50",
                    )}
                  >
                    <div className="line-clamp-2 text-sm font-bold">{item.claim}</div>
                    <div className={cn("mt-2 flex items-center justify-between text-xs", muted(theme))}>
                      <span>{item.verdict ?? "Pending"}</span>
                      <span>{score(item.confidence)}</span>
                    </div>
                  </button>
                ))
              ) : (
                <Card className={cn("p-4", theme === "light" && "border-slate-200 bg-white")}>
                  <div className={muted(theme)}>No saved investigations yet.</div>
                </Card>
              )}
            </div>
          </aside>

          <main className="p-6 max-md:p-4">
            <header className="mb-5 flex items-center justify-between gap-4 max-md:flex-col max-md:items-stretch">
              <div>
                <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 text-xs font-extrabold uppercase tracking-[0.18em] text-cyan">
                  <Sparkles className="size-3.5" />
                  Agentic verification
                </div>
                <h1 className="max-w-4xl text-balance font-display text-6xl font-black leading-[0.95] tracking-normal max-lg:text-5xl max-md:text-4xl">
                  Trust evidence, not vibes.
                </h1>
                <p className={cn("mt-4 max-w-3xl text-lg leading-7", muted(theme))}>
                  A premium investigation cockpit for claims, sources, provenance, contradictions,
                  confidence, memory, and reports.
                </p>
              </div>

              <Button
                variant="ghost"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className={theme === "light" ? "border-slate-300 bg-white text-slate-950" : ""}
              >
                {theme === "dark" ? <Sun className="size-4" /> : <Moon className="size-4" />}
                {theme === "dark" ? "Light" : "Dark"}
              </Button>
            </header>

            <section className="mb-5 grid grid-cols-[minmax(0,1.25fr)_minmax(340px,0.75fr)] gap-5 max-lg:grid-cols-1">
              <Card className={cn("p-5", theme === "light" && "border-slate-200 bg-white")}>
                <div className="mb-4 flex items-center justify-between gap-4">
                  <div>
                    <div className={label(theme)}>New Investigation</div>
                    <h2 className="mt-1 font-display text-2xl font-bold">Search Claim</h2>
                  </div>
                  <Button
                    variant="ghost"
                    onClick={() => setClaim(samples[Math.floor(Math.random() * samples.length)])}
                    className={theme === "light" ? "border-slate-300 bg-white text-slate-950" : ""}
                  >
                    <Sparkles className="size-4" />
                    Sample
                  </Button>
                </div>

                <textarea
                  value={claim}
                  onChange={(event) => setClaim(event.target.value)}
                  className={cn(inputClass(theme), "min-h-40 resize-y p-4 text-base leading-7")}
                  placeholder="Paste a viral claim, health myth, product promise, or AI answer..."
                />

                <div className="mt-4 grid grid-cols-[1fr_auto] gap-3 max-sm:grid-cols-1">
                  <label
                    className={cn(
                      "flex cursor-pointer items-center gap-3 rounded-xl border border-dashed border-white/15 bg-white/[0.03] px-4 py-3 text-sm transition hover:border-cyan/40 hover:bg-cyan/10",
                      theme === "light" && "border-slate-300 bg-slate-50",
                    )}
                  >
                    <UploadCloud className="size-5 text-cyan" />
                    <span className={muted(theme)}>Drag-and-drop upload surface is API-ready for text, PDF, and images</span>
                    <input className="hidden" type="file" />
                  </label>

                  <Button onClick={startInvestigation} disabled={isInvestigating} className="px-6">
                    {isInvestigating ? <Loader2 className="size-4 animate-spin" /> : <Search className="size-4" />}
                    Investigate
                  </Button>
                </div>

                {error && (
                  <div className="mt-4 rounded-xl border border-red/30 bg-red/10 p-3 text-sm text-red-200">
                    {error}
                  </div>
                )}
              </Card>

              <InvestigationStatus
                isRunning={isInvestigating}
                stepIndex={activeStepIndex}
                theme={theme}
                activeCase={activeCase}
              />
            </section>

            <section className="mb-5 grid grid-cols-4 gap-4 max-lg:grid-cols-2 max-sm:grid-cols-1">
              <Metric title="Verdict" value={activeCase?.verdict ?? "Awaiting Claim"} icon={ShieldCheck} theme={theme} />
              <Metric title="Confidence" value={activeCase ? `${confidence}%` : "--"} icon={Gauge} theme={theme} />
              <Metric title="Evidence" value={`${activeCase?.sources?.length ?? 0} sources`} icon={Network} theme={theme} />
              <Metric title="TraceBack" value={`${activeCase?.traceback_timeline?.length ?? 0} events`} icon={GitBranch} theme={theme} />
            </section>

            <section className="grid grid-cols-[minmax(0,1fr)_420px] gap-5 max-xl:grid-cols-1">
              <div className="grid gap-5">
                <VerdictPanel
                  activeCase={activeCase}
                  confidence={confidence}
                  onDownload={downloadReport}
                  theme={theme}
                />
                <EvidenceGraph sources={topSources} theme={theme} />
                <EvidenceTabs activeCase={activeCase} theme={theme} />
              </div>

              <div className="grid gap-5">
                <ActivityTimeline activities={activeCase?.activities ?? []} theme={theme} />
                <SourceQuality sources={activeCase?.sources ?? []} theme={theme} />
              </div>
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}

function InvestigationStatus({
  isRunning,
  stepIndex,
  theme,
  activeCase,
}: {
  isRunning: boolean;
  stepIndex: number;
  theme: Theme;
  activeCase: CaseDetail | null;
}) {
  return (
    <Card className={cn("p-5", theme === "light" && "border-slate-200 bg-white")}>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <div className={label(theme)}>Live Workflow</div>
          <h2 className="mt-1 font-display text-2xl font-bold">
            {isRunning ? runningSteps[stepIndex] : activeCase ? "Verdict earned" : "Ready"}
          </h2>
        </div>
        <div className="grid size-12 place-items-center rounded-xl border border-cyan/30 bg-cyan/10 text-cyan">
          {isRunning ? <Loader2 className="size-5 animate-spin" /> : <Brain className="size-5" />}
        </div>
      </div>

      <div className="grid gap-2">
        {runningSteps.map((step, index) => {
          const done = activeCase && !isRunning;
          const active = isRunning && index === stepIndex;
          return (
            <div
              key={step}
              className={cn(
                "flex items-center gap-3 rounded-lg border px-3 py-2 text-sm",
                active ? "border-cyan/50 bg-cyan/10 text-cyan" : "border-white/10 bg-white/[0.025]",
                done && "border-mint/30 bg-mint/10 text-mint",
                theme === "light" && !active && !done && "border-slate-200 bg-slate-50 text-slate-700",
              )}
            >
              {done ? <CheckCircle2 className="size-4" /> : active ? <Activity className="size-4" /> : <Clock3 className="size-4 opacity-60" />}
              {step}
            </div>
          );
        })}
      </div>
    </Card>
  );
}

function Metric({
  title,
  value,
  icon: Icon,
  theme,
}: {
  title: string;
  value: string;
  icon: typeof ShieldCheck;
  theme: Theme;
}) {
  return (
    <Card className={cn("p-4", theme === "light" && "border-slate-200 bg-white")}>
      <div className="mb-3 flex items-center justify-between">
        <span className={label(theme)}>{title}</span>
        <Icon className="size-4 text-cyan" />
      </div>
      <div className="font-display text-2xl font-black">{value}</div>
    </Card>
  );
}

function VerdictPanel({
  activeCase,
  confidence,
  onDownload,
  theme,
}: {
  activeCase: CaseDetail | null;
  confidence: number;
  onDownload: () => void;
  theme: Theme;
}) {
  return (
    <Card className={cn("p-5", theme === "light" && "border-slate-200 bg-white")}>
      <div className="mb-5 flex items-start justify-between gap-4">
        <div>
          <div className={label(theme)}>Reasoned Output</div>
          <h2 className="mt-1 max-w-3xl font-display text-3xl font-black">
            {activeCase?.claim ?? "Submit a claim to generate an evidence-backed verdict."}
          </h2>
        </div>
        <Button
          variant="ghost"
          onClick={onDownload}
          disabled={!activeCase}
          className={theme === "light" ? "border-slate-300 bg-white text-slate-950" : ""}
        >
          <Download className="size-4" />
          Report
        </Button>
      </div>

      <div className="mb-5 rounded-xl border border-cyan/25 bg-cyan/10 p-4">
        <div className="mb-2 flex items-center gap-2 font-display text-xl font-bold">
          <ShieldCheck className="size-5 text-mint" />
          {activeCase?.verdict ?? "No verdict yet"}
        </div>
        <p className={cn("leading-7", muted(theme))}>
          {activeCase?.reasoning_summary ??
            "ProofPath will explain support, opposition, contradictions, and limitations here."}
        </p>
      </div>

      <div>
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className={muted(theme)}>Confidence meter</span>
          <span className="font-bold">{activeCase ? `${confidence}%` : "--"}</span>
        </div>
        <div className={cn("h-3 overflow-hidden rounded-full bg-white/10", theme === "light" && "bg-slate-200")}>
          <motion.div
            className="h-full rounded-full bg-gradient-to-r from-cyan to-mint"
            initial={{ width: 0 }}
            animate={{ width: `${confidence}%` }}
            transition={{ duration: 0.6 }}
          />
        </div>
      </div>
    </Card>
  );
}

function EvidenceGraph({ sources, theme }: { sources: Source[]; theme: Theme }) {
  return (
    <Card className={cn("overflow-hidden p-5", theme === "light" && "border-slate-200 bg-white")}>
      <div className="mb-5 flex items-center justify-between">
        <div>
          <div className={label(theme)}>Evidence Graph</div>
          <h2 className="mt-1 font-display text-2xl font-bold">Claim Network</h2>
        </div>
        <Network className="size-5 text-cyan" />
      </div>

      <div className="relative min-h-72 rounded-xl border border-white/10 bg-black/20 p-5">
        <div className="absolute inset-0 opacity-40 glass-grid" />
        <div className="relative mx-auto grid size-32 place-items-center rounded-full border border-cyan/40 bg-cyan/15 text-center font-display text-sm font-bold text-cyan shadow-glow">
          Claim
        </div>
        <div className="relative mt-8 grid grid-cols-3 gap-3 max-md:grid-cols-1">
          {(sources.length ? sources : placeholderSources()).slice(0, 6).map((source, index) => (
            <motion.div
              key={`${source.title}-${index}`}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.06 }}
              className={cn(
                "rounded-xl border border-white/10 bg-white/[0.045] p-3",
                theme === "light" && "border-slate-200 bg-white",
              )}
            >
              <div className="mb-2 flex items-center justify-between gap-2">
                <Badge>{source.stance}</Badge>
                <span className="text-xs font-bold text-mint">{Math.round((source.quality_score || 0) * 100)}%</span>
              </div>
              <div className="line-clamp-2 text-sm font-bold">{source.title}</div>
            </motion.div>
          ))}
        </div>
      </div>
    </Card>
  );
}

function EvidenceTabs({ activeCase, theme }: { activeCase: CaseDetail | null; theme: Theme }) {
  const [tab, setTab] = useState<"sources" | "traceback" | "contradictions">("sources");

  return (
    <Card className={cn("p-5", theme === "light" && "border-slate-200 bg-white")}>
      <div className="mb-4 flex flex-wrap gap-2">
        {[
          ["sources", "Sources"],
          ["traceback", "TraceBack"],
          ["contradictions", "Contradictions"],
        ].map(([key, labelText]) => (
          <button
            key={key}
            onClick={() => setTab(key as "sources" | "traceback" | "contradictions")}
            className={cn(
              "rounded-full border px-4 py-2 text-sm font-black transition",
              tab === key
                ? "border-transparent bg-gradient-to-r from-cyan to-mint text-obsidian"
                : "border-white/10 bg-white/[0.035] text-slate-400 hover:border-cyan/40",
              theme === "light" && tab !== key && "border-slate-200 bg-slate-50 text-slate-600",
            )}
          >
            {labelText}
          </button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={tab}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          className="grid gap-3 md:grid-cols-2"
        >
          {tab === "sources" &&
            renderList(activeCase?.sources ?? [], (source) => (
              <SourceCard key={source.id} source={source} theme={theme} />
            ))}
          {tab === "traceback" &&
            renderList(activeCase?.traceback_timeline ?? [], (event) => (
              <article key={event.id} className={itemCard(theme)}>
                <Badge>{event.event_date ?? "date unknown"}</Badge>
                <h3 className="mt-3 font-display font-bold">{event.source_title}</h3>
                <p className={cn("mt-2 text-sm leading-6", muted(theme))}>{event.notes}</p>
              </article>
            ))}
          {tab === "contradictions" &&
            renderList(activeCase?.contradictions ?? [], (item) => (
              <article key={item.id} className={itemCard(theme)}>
                <Badge className="border-amber/30 text-amber">{item.severity}</Badge>
                <h3 className="mt-3 font-display font-bold">Contradiction detected</h3>
                <p className={cn("mt-2 text-sm leading-6", muted(theme))}>{item.contradiction_summary}</p>
              </article>
            ))}
        </motion.div>
      </AnimatePresence>
    </Card>
  );
}

function SourceCard({ source, theme }: { source: Source; theme: Theme }) {
  return (
    <article className={itemCard(theme)}>
      <div className="mb-3 flex flex-wrap gap-2">
        <Badge>{source.source_type}</Badge>
        <Badge>{source.stance}</Badge>
        <Badge className="border-mint/30 text-mint">quality {source.quality_score.toFixed(2)}</Badge>
      </div>
      <a href={source.url} target="_blank" rel="noreferrer" className="group font-display font-bold text-cyan">
        {source.title}
        <ArrowUpRight className="ml-1 inline size-4 transition group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
      </a>
      <p className={cn("mt-2 line-clamp-3 text-sm leading-6", muted(theme))}>{source.snippet}</p>
    </article>
  );
}

function ActivityTimeline({ activities, theme }: { activities: AgentActivity[]; theme: Theme }) {
  return (
    <Card className={cn("p-5", theme === "light" && "border-slate-200 bg-white")}>
      <div className="mb-5 flex items-center justify-between">
        <div>
          <div className={label(theme)}>Agent Trace</div>
          <h2 className="mt-1 font-display text-2xl font-bold">Thinking Steps</h2>
        </div>
        <PanelRight className="size-5 text-cyan" />
      </div>
      <div className="relative grid gap-3">
        {activities.length ? (
          activities.map((activity, index) => (
            <motion.div
              key={`${activity.step}-${index}`}
              initial={{ opacity: 0, x: 16 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className={cn(
                "rounded-xl border border-white/10 bg-white/[0.035] p-3",
                theme === "light" && "border-slate-200 bg-slate-50",
              )}
            >
              <div className="flex items-start gap-3">
                <div className="mt-1 size-2.5 rounded-full bg-mint shadow-[0_0_18px_rgba(82,224,155,0.8)]" />
                <div>
                  <div className="font-bold">{activity.step}</div>
                  <div className={cn("mt-1 text-sm", muted(theme))}>
                    {activity.agent}
                    {activity.tool ? ` · ${activity.tool}` : ""}
                  </div>
                </div>
              </div>
            </motion.div>
          ))
        ) : (
          <EmptyState icon={Brain} text="Run an investigation to see every agent step." theme={theme} />
        )}
      </div>
    </Card>
  );
}

function SourceQuality({ sources, theme }: { sources: Source[]; theme: Theme }) {
  const ranked = useMemo(() => [...sources].sort((a, b) => b.quality_score - a.quality_score).slice(0, 5), [sources]);
  return (
    <Card className={cn("p-5", theme === "light" && "border-slate-200 bg-white")}>
      <div className="mb-5 flex items-center justify-between">
        <div>
          <div className={label(theme)}>Credibility</div>
          <h2 className="mt-1 font-display text-2xl font-bold">Source Badges</h2>
        </div>
        <ShieldCheck className="size-5 text-mint" />
      </div>
      <div className="grid gap-3">
        {ranked.length ? (
          ranked.map((source) => (
            <div key={source.id} className="grid gap-2">
              <div className="flex items-center justify-between gap-3 text-sm">
                <span className="line-clamp-1 font-bold">{source.title}</span>
                <span className="text-mint">{Math.round(source.quality_score * 100)}%</span>
              </div>
              <div className={cn("h-2 rounded-full bg-white/10", theme === "light" && "bg-slate-200")}>
                <div
                  className="h-full rounded-full bg-gradient-to-r from-cyan to-mint"
                  style={{ width: `${Math.round(source.quality_score * 100)}%` }}
                />
              </div>
            </div>
          ))
        ) : (
          <EmptyState icon={FileUp} text="Credibility badges appear after source retrieval." theme={theme} />
        )}
      </div>
    </Card>
  );
}

function EmptyState({
  icon: Icon,
  text,
  theme,
}: {
  icon: typeof AlertTriangle;
  text: string;
  theme: Theme;
}) {
  return (
    <div className={cn("rounded-xl border border-dashed border-white/15 p-5 text-center", theme === "light" && "border-slate-300")}>
      <Icon className="mx-auto mb-3 size-6 text-cyan" />
      <p className={muted(theme)}>{text}</p>
    </div>
  );
}

function renderList<T>(items: T[], render: (item: T) => React.ReactNode) {
  if (!items.length) {
    return (
      <div className="md:col-span-2">
        <div className="rounded-xl border border-dashed border-white/15 p-5 text-center text-slate-400">
          Nothing to show yet.
        </div>
      </div>
    );
  }
  return items.map(render);
}

function placeholderSources(): Source[] {
  return [
    {
      id: "placeholder-1",
      title: "Government source",
      url: "#",
      snippet: "",
      source_type: "government",
      stance: "pending",
      quality_score: 0.92,
    },
    {
      id: "placeholder-2",
      title: "Academic source",
      url: "#",
      snippet: "",
      source_type: "academic",
      stance: "pending",
      quality_score: 0.86,
    },
    {
      id: "placeholder-3",
      title: "TraceBack candidate",
      url: "#",
      snippet: "",
      source_type: "provenance",
      stance: "pending",
      quality_score: 0.64,
    },
  ];
}

function itemCard(theme: Theme) {
  return cn(
    "rounded-xl border border-white/10 bg-white/[0.035] p-4",
    theme === "light" && "border-slate-200 bg-slate-50",
  );
}

function score(value: number | null | undefined) {
  if (value == null) return "--";
  return `${Math.round(value * 100)}%`;
}

function muted(theme: Theme) {
  return cn(theme === "light" ? "text-slate-600" : "text-slate-400");
}

function label(theme: Theme) {
  return cn(
    "text-xs font-black uppercase tracking-[0.16em]",
    theme === "light" ? "text-slate-500" : "text-slate-500",
  );
}

function inputClass(theme: Theme) {
  return cn(
    "w-full rounded-xl border px-3 py-2.5 outline-none transition focus:border-cyan focus:ring-4 focus:ring-cyan/10",
    theme === "light"
      ? "border-slate-300 bg-white text-slate-950 placeholder:text-slate-400"
      : "border-white/10 bg-white/[0.045] text-slate-50 placeholder:text-slate-600",
  );
}
