from app.models import InvestigationState
from app.tools.pdf_export import markdown_to_pdf_bytes
from app.tools.reporting import generate_report


def test_markdown_report_can_be_rendered_as_pdf() -> None:
    state = InvestigationState(raw_input="Test claim for PDF export.")
    state.report_markdown = generate_report(state)

    pdf = markdown_to_pdf_bytes(state.report_markdown, "ProofPath Test Report")

    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 500
