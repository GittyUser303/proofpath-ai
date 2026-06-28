export type CaseSummary = {
  case_id: string;
  claim: string;
  verdict: string | null;
  confidence: number | null;
  created_at: string;
};

export type Activity = {
  step: string;
  agent: string;
  tool?: string | null;
  status: string;
  detail?: string | null;
  timestamp: string;
};

export type Source = {
  id: string;
  title: string;
  url: string;
  snippet: string;
  source_type: string;
  stance: string;
  quality_score: number;
  published_date?: string | null;
};

export type TracebackEvent = {
  id: string;
  event_date?: string | null;
  source_title: string;
  source_url: string;
  claim_version: string;
  quality_label: string;
  notes: string;
};

export type Contradiction = {
  id: string;
  claim_part: string;
  source_a?: string | null;
  source_b?: string | null;
  contradiction_summary: string;
  severity: string;
};

export type CaseDetail = {
  case_id: string;
  user_id: string;
  claim: string;
  original_input: string;
  domain: string;
  verdict: string | null;
  confidence: number | null;
  reasoning_summary: string | null;
  report_markdown: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  sources: Source[];
  traceback_timeline: TracebackEvent[];
  contradictions: Contradiction[];
  activities: Activity[];
};
