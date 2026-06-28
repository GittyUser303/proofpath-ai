from __future__ import annotations

import textwrap


def markdown_to_pdf_bytes(markdown: str, title: str = "ProofPath Report") -> bytes:
    """Render a readable plain-text PDF from a Markdown report."""
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("PDF export requires PyMuPDF. Install requirements.txt first.") from exc

    document = fitz.open()
    margin = 54
    line_height = 13
    page_width = 595
    page_height = 842
    usable_width = page_width - margin * 2
    y = margin

    def add_page():
        page = document.new_page(width=page_width, height=page_height)
        return page

    page = add_page()
    page.insert_text((margin, y), title, fontsize=16, fontname="helv", color=(0.03, 0.05, 0.07))
    y += 28

    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if not line:
            y += line_height
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip()
            font_size = 13
            y += 6
        else:
            font_size = 10
        if line.startswith("- "):
            line = f"* {line[2:]}"
        wrapped = textwrap.wrap(line, width=max(40, int(usable_width / (font_size * 0.52)))) or [""]
        for item in wrapped:
            if y > page_height - margin:
                page = add_page()
                y = margin
            page.insert_text((margin, y), item, fontsize=font_size, fontname="helv", color=(0.08, 0.1, 0.13))
            y += line_height + (2 if font_size > 10 else 0)

    return document.tobytes()
