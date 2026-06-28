# Demo Script: ProofPath AI

## Demo Goal

Show that ProofPath AI is more than a chatbot.

The main idea is simple:

> Instead of asking an AI answer and trusting it, ProofPath checks the claim, finds sources, traces where the claim may have come from, compares evidence, and gives a cautious verdict.

## Best Claim To Demo

Use this claim:

> Cold water after meals causes cancer.

Why this works well:

- Everyone understands it quickly.
- It sounds like the kind of thing people see online.
- It should produce useful medical/fact-check sources.
- It lets you show source quality, contradictions, and TraceBack.

## 3-5 Minute Demo Flow

### 0:00-0:30 - Quick Intro

Say something like:

> This is ProofPath AI. It is an agentic claim verification app. The goal is to help students, journalists, and normal readers check whether an AI answer or viral claim is actually supported by evidence.

Then add:

> A normal chatbot would just respond to the claim. ProofPath does a workflow: it extracts the claim, plans which tools to use, searches sources, traces origin, checks contradictions, uses an LLM reasoning step, and saves the case in memory.

## 0:30-1:00 - Enter The Claim

Type:

> Cold water after meals causes cancer.

Click **Verify claim**.

Point out:

- The app accepts a user claim.
- It can also accept files like text, PDFs, CSVs, and screenshots.
- The workflow starts in real time.

Say:

> I am using a simple health misinformation example so the workflow is easy to follow.

## 1:00-1:40 - Show The Work Process

Focus on the work process section.

Say:

> This panel is not just animation. It is showing the backend workflow as it runs. The app uses LangGraph to move through nodes like claim extraction, planning, evidence retrieval, TraceBack, source scoring, contradiction detection, LLM reasoning, confidence scoring, report generation, and memory save.

Point out:

- Claim Extraction Agent
- Planner Agent
- Evidence Retrieval Agent
- TraceBack Agent
- Source Quality Agent
- LLM Reasoning Agent
- Case Manager Agent

Say:

> This is what makes it agentic. The system is deciding what steps and tools are needed instead of doing one prompt-to-answer call.

## 1:40-2:30 - Show Sources And Tool Usage

Open the source cards or citation inspector.

Say:

> Here the agent has collected sources. Each source is labeled by type and stance. For example, medical or government sources should be treated differently from blogs or unknown websites.

Point out:

- Source title
- Website/domain
- Stance label
- Trust label
- Open citation link

Say:

> The tools matter because the LLM should not invent citations. The search tool retrieves evidence, the source scoring tool ranks credibility, and the contradiction tool checks whether the evidence agrees or conflicts.

## 2:30-3:10 - Show TraceBack

Click the **TraceBack trail** tab.

Say:

> This is the TraceBack part. It looks for earlier accessible appearances of the claim and similar wording. It does not claim the absolute origin unless there is enough evidence. It uses cautious wording like earliest accessible candidate.

If there are no TraceBack events, say:

> If nothing is found, the app says that clearly instead of pretending it found an origin.

## 3:10-3:50 - Show Contradictions And Verdict

Click **Contradictions**.

Say:

> This section shows where the evidence is mixed, weak, or conflicting. It also names the source behind the caution when the backend can identify it.

Then show the verdict gauge.

Say:

> The final verdict is not just a random LLM answer. It is based on retrieved evidence, source quality, agreement between sources, primary-source strength, TraceBack clarity, and contradiction penalties.

Mention:

> The LLM is used as a reasoning agent after the tools run, not as the only source of truth.

## 3:50-4:30 - Show Memory And Report

Show saved checks or reload a previous case.

Say:

> ProofPath also has persistent memory. It saves cases, sources, TraceBack events, contradictions, activity logs, and reports in SQLite, so a user can come back to previous investigations.

Show export/report if useful.

Say:

> The report can be downloaded as Markdown, and the backend also supports PDF export.

## 4:30-5:00 - Closing

Say:

> So overall, ProofPath demonstrates the main parts of an agentic AI application: user input, an LLM API, multiple tools, planning, autonomous workflow decisions, persistent memory, and a polished frontend.

End with:

> The purpose is to make AI-generated answers auditable. Instead of asking users to blindly trust an answer, ProofPath shows the evidence trail behind the verdict.

## Backup Claims

Use these if the first claim does not produce good sources:

- Creatine damages kidneys in healthy adults.
- AI detectors can reliably detect ChatGPT writing.
- Blue light glasses prevent all eye damage.
- Alkaline water cures disease.

## Quick Demo Tips

- Keep the app visible the whole time.
- Do not read every source.
- Focus on the workflow, not just the final answer.
- Mention LangGraph once.
- Mention that the LLM is used after tool retrieval.
- Show memory before ending.
- Keep the tone calm and confident.
