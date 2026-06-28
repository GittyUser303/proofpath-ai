# Evaluation Metrics

## 1. Bootcamp Requirement Mapping

| Requirement | ProofPath Implementation |
|---|---|
| Accept user input | Claim input/upload |
| Use LLM API | Claim extraction, planning, reasoning |
| Use at least 2 tools | Search, source scoring, PDF/OCR, database |
| Tool need is clear | Evidence retrieval and TraceBack need tools |
| Maintain memory | SQLite case memory |
| Multi-step workflow | Extract → Plan → Search → Trace → Score → Reason |
| Planning/decision-making | Planner chooses tools |
| Polished frontend | Investigation dashboard |

## 2. Product Metrics

### Evidence Quality Score
Average credibility score of selected sources.

### Contradiction Coverage
How many contradictions were identified.

### TraceBack Completeness
How well the system traced claim versions.

### Confidence Calibration
Whether high confidence is only assigned when evidence is strong.

### Memory Utility
Whether past cases improve future responses.

## 3. Demo Metrics
During demo, judges should see:
- planner output,
- multiple tools,
- evidence list,
- traceback timeline,
- confidence score,
- final verdict,
- stored memory.

## 4. Test Claims
Use these to evaluate:

1. "Cold water after meals causes cancer."
2. "Creatine damages kidneys in healthy adults."
3. "AI detectors can reliably detect AI writing."
4. "Blue light glasses prevent eye damage."
5. "Drinking alkaline water cures disease."

## 5. Failure Modes
Track:
- no sources found,
- low-quality sources only,
- contradictory sources,
- search API failure,
- LLM invalid JSON,
- missing dates for timeline.

## 6. Quality Gates
Before final answer:
- at least 3 sources found,
- at least 1 high-quality source preferred,
- source stance identified,
- confidence explained,
- limitations included.
