from __future__ import annotations

import csv
import io
import os
from pathlib import Path


def parse_text_upload(content: bytes) -> str:
    """Decode a plain-text upload."""
    return content.decode("utf-8", errors="replace").strip()


def parse_csv_upload(content: bytes, filename: str = "uploaded CSV") -> str:
    """Summarize a CSV upload so large datasets do not flood the claim UI."""
    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    columns = reader.fieldnames or []
    rows = []
    numeric_stats: dict[str, dict[str, float]] = {}

    for row_index, row in enumerate(reader):
        if row_index < 5:
            rows.append(row)
        for column, value in row.items():
            if value in (None, ""):
                continue
            try:
                number = float(value)
            except (TypeError, ValueError):
                continue
            stats = numeric_stats.setdefault(column, {"min": number, "max": number, "sum": 0.0, "count": 0.0})
            stats["min"] = min(stats["min"], number)
            stats["max"] = max(stats["max"], number)
            stats["sum"] += number
            stats["count"] += 1

    row_count = row_index + 1 if "row_index" in locals() else 0
    summary = [
        f"Attached dataset: {filename}",
        f"Rows: {row_count}",
        f"Columns: {', '.join(columns[:18])}{'...' if len(columns) > 18 else ''}",
    ]

    if numeric_stats:
        summary.append("Numeric profile:")
        for column, stats in list(numeric_stats.items())[:8]:
            mean = stats["sum"] / max(stats["count"], 1)
            summary.append(f"- {column}: min {stats['min']:.2f}, max {stats['max']:.2f}, mean {mean:.2f}")

    if rows:
        summary.append("Sample rows:")
        for row in rows[:3]:
            compact = ", ".join(f"{key}={value}" for key, value in list(row.items())[:8])
            summary.append(f"- {compact}")

    summary.append("Instruction: verify claims about this dataset using the summary, not raw row dumps.")
    return "\n".join(summary)


def parse_pdf_upload(content: bytes) -> str:
    """Extract text from a PDF when PyMuPDF is installed."""
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PDF parsing requires PyMuPDF. Install requirements.txt first.") from exc

    text_parts: list[str] = []
    with fitz.open(stream=content, filetype="pdf") as document:
        for page in document:
            text_parts.append(page.get_text("text"))
    return "\n".join(text_parts).strip()


def ocr_image_upload(content: bytes) -> str:
    """Extract text from an image when Pillow and Tesseract are installed."""
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Image OCR requires Pillow and pytesseract. Install requirements.txt first.") from exc

    from io import BytesIO

    tesseract_candidates = [
        os.environ.get("TESSERACT_CMD"),
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for candidate in tesseract_candidates:
        if candidate and Path(candidate).exists():
            pytesseract.pytesseract.tesseract_cmd = candidate
            break

    image = Image.open(BytesIO(content))
    try:
        return pytesseract.image_to_string(image).strip()
    except pytesseract.pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Image OCR needs the Tesseract app installed. Install it with: winget install UB-Mannheim.TesseractOCR"
        ) from exc
