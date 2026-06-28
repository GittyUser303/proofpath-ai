import asyncio
import json

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse, Response, StreamingResponse

from app.config.settings import get_settings
from app.memory.sqlite_memory import SQLiteMemory
from app.models import InvestigationRequest, InvestigationResponse, UserPreferenceUpdate
from app.tools.document_parsing import ocr_image_upload, parse_csv_upload, parse_pdf_upload, parse_text_upload
from app.tools.pdf_export import markdown_to_pdf_bytes
from app.workflow import ProofPathWorkflow

router = APIRouter()


@router.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Return service health and environment metadata."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
    }


@router.post("/investigate", response_model=InvestigationResponse, tags=["investigations"])
async def investigate(request: InvestigationRequest) -> InvestigationResponse:
    """Run a complete ProofPath investigation and persist it."""
    workflow = ProofPathWorkflow()
    state = await workflow.run(raw_input=request.input, user_id=request.user_id)
    return InvestigationResponse(
        case_id=state.case_id,
        status=state.status,
        claim=state.claim,
        verdict=state.verdict,
        confidence=state.confidence,
    )


@router.post("/investigate/stream", tags=["investigations"])
async def investigate_stream(request: InvestigationRequest) -> StreamingResponse:
    """Run an investigation and stream real workflow progress as newline-delimited JSON."""

    async def event_stream():
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue()
        workflow = ProofPathWorkflow()

        async def progress(payload: dict[str, object]) -> None:
            await queue.put(payload)

        task = asyncio.create_task(
            workflow.run(
                raw_input=request.input,
                user_id=request.user_id,
                progress_callback=progress,
            )
        )

        while True:
            if task.done() and queue.empty():
                break
            try:
                payload = await asyncio.wait_for(queue.get(), timeout=0.25)
                yield json.dumps(payload) + "\n"
            except TimeoutError:
                yield json.dumps({"event": "heartbeat"}) + "\n"

        state = await task
        yield json.dumps(
            {
                "event": "complete" if state.status.value == "completed" else "error",
                "case_id": state.case_id,
                "status": state.status.value,
            }
        ) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")


@router.get("/cases", tags=["memory"])
async def list_cases(user_id: str = "demo_user") -> list[dict[str, object]]:
    """Return previous investigations for a user."""
    memory = SQLiteMemory()
    return [case.model_dump() for case in memory.list_cases(user_id=user_id)]


@router.get("/cases/{case_id}", tags=["memory"])
async def get_case(case_id: str) -> dict[str, object]:
    """Return full persisted investigation details."""
    memory = SQLiteMemory()
    payload = memory.get_case_payload(case_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Case not found")
    return payload


@router.get("/report/{case_id}", response_class=PlainTextResponse, tags=["reports"])
async def get_report(case_id: str) -> str:
    """Return the Markdown report for a completed investigation."""
    memory = SQLiteMemory()
    payload = memory.get_case_payload(case_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Case not found")
    report = payload.get("report_markdown")
    if not report:
        raise HTTPException(status_code=404, detail="Report not available")
    return str(report)


@router.get("/report/{case_id}/pdf", tags=["reports"])
async def get_report_pdf(case_id: str) -> Response:
    """Return the investigation report as a downloadable PDF."""
    memory = SQLiteMemory()
    payload = memory.get_case_payload(case_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Case not found")
    report = payload.get("report_markdown")
    if not report:
        raise HTTPException(status_code=404, detail="Report not available")
    try:
        pdf_bytes = markdown_to_pdf_bytes(str(report), title=f"ProofPath Report - {case_id}")
    except RuntimeError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{case_id}_proofpath_report.pdf"'},
    )


@router.post("/preferences", tags=["memory"])
async def update_preferences(update: UserPreferenceUpdate) -> dict[str, object]:
    """Persist source and explanation preferences for a user."""
    memory = SQLiteMemory()
    memory.save_preferences(update.user_id, update.preferences)
    return {
        "status": "ok",
        "user_id": update.user_id,
        "preferences": memory.get_preferences(update.user_id),
    }


@router.post("/upload", tags=["uploads"])
async def upload(file: UploadFile = File(...)) -> dict[str, str]:
    """Accept a text-like upload and return extracted text for investigation."""
    content = await file.read()
    content_type = file.content_type or ""
    filename = file.filename or "uploaded_file"
    lower_name = filename.lower()
    try:
        if lower_name.endswith(".csv") or content_type in {"text/csv", "application/csv"}:
            extracted = parse_csv_upload(content, filename)
        elif content_type.startswith("text/") or lower_name.endswith((".txt", ".md", ".markdown", ".log")):
            extracted = parse_text_upload(content)
        elif content_type == "application/pdf" or lower_name.endswith(".pdf"):
            extracted = parse_pdf_upload(content)
        elif content_type.startswith("image/") or lower_name.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff")):
            extracted = ocr_image_upload(content)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload .txt, .md, .pdf, or an image file.",
            )
    except RuntimeError as exc:
        message = str(exc)
        status_code = 501 if "requires" in message.lower() else 422
        raise HTTPException(status_code=status_code, detail=message) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Could not extract readable text from {filename}. Try a text-based PDF, .txt, or .md file.",
        ) from exc

    if not extracted.strip():
        raise HTTPException(
            status_code=422,
            detail=f"No readable text was found in {filename}. Scanned PDFs and screenshots may need OCR/Tesseract.",
        )

    return {
        "file_id": filename,
        "extracted_text": extracted,
    }
