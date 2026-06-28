# Security and Privacy

## 1. Data Sensitivity
ProofPath may process:
- user claims,
- uploaded screenshots,
- PDFs,
- AI-generated answers,
- potentially sensitive documents.

## 2. MVP Privacy Rules
- Do not store unnecessary personal data.
- Store only case text, sources, and reports.
- Allow user to delete memory.
- Keep API keys in `.env`.
- Do not commit `.env`.

## 3. API Key Handling
Use `.env`:

```text
LLM_API_KEY=
TAVILY_API_KEY=
SERPER_API_KEY=
```

Never expose keys in:
- frontend,
- GitHub,
- logs,
- demo video.

## 4. Safety Disclaimers
For medical/legal/financial claims, include:

> This is an evidence investigation assistant, not professional advice. Consult a qualified professional for decisions involving health, law, or finance.

## 5. Hallucination Prevention
The agent must:
- avoid fake citations,
- show URLs,
- state when evidence is weak,
- use "not enough evidence" when needed,
- avoid claiming absolute origin.

## 6. TraceBack Safety
TraceBack should say:
- "earliest accessible source found"
- "appears to have spread through"
- "based on available search results"

Avoid:
- "this is definitely the first source"
- "this person started the rumor"
- accusations without strong evidence.

## 7. User Upload Safety
For uploaded files:
- limit file size,
- restrict accepted formats,
- avoid executing file content,
- sanitize filenames.

## 8. Future Production Considerations
- authentication,
- encryption at rest,
- role-based access,
- data deletion endpoint,
- audit logs,
- privacy policy,
- rate limiting.
