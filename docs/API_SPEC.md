# API Specification

## 1. POST /api/investigate
Starts a new investigation.

Request:
```json
{
  "user_id": "demo_user",
  "input": "Cold water after meals causes cancer",
  "mode": "standard"
}
```

Response:
```json
{
  "case_id": "case_123",
  "status": "started"
}
```

## 2. GET /api/cases/{case_id}
Returns investigation details.

Response:
```json
{
  "case_id": "case_123",
  "claim": "Cold water after meals causes cancer",
  "verdict": "Unsupported",
  "confidence": 0.91,
  "sources": [],
  "traceback_timeline": [],
  "contradictions": [],
  "report_markdown": ""
}
```

## 3. GET /api/cases
Returns previous cases.

Request:
```text
/api/cases?user_id=demo_user
```

Response:
```json
[
  {
    "case_id": "case_123",
    "claim": "Cold water after meals causes cancer",
    "verdict": "Unsupported",
    "confidence": 0.91,
    "created_at": "2026-06-26"
  }
]
```

## 4. POST /api/upload
Uploads a PDF/image.

Request:
- multipart form data

Response:
```json
{
  "file_id": "file_123",
  "extracted_text": "..."
}
```

## 5. GET /api/report/{case_id}
Downloads report.

Response:
- Markdown or PDF file.

## 6. POST /api/preferences
Updates user preferences.

Request:
```json
{
  "user_id": "demo_user",
  "preferences": {
    "preferred_sources": ["academic", "government"],
    "explanation_style": "simple"
  }
}
```

## 7. Error Format
```json
{
  "error": true,
  "message": "Search API failed",
  "recoverable": true
}
```
