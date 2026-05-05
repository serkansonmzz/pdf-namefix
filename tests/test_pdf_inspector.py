from pathlib import Path

from pypdf import PdfWriter

from pdf_namefix.domain.models import PdfFile
from pdf_namefix.services.pdf_inspector import inspect_pdf_file, safe_str, truncate_text


def make_pdf_file(path: Path) -> PdfFile:
    return PdfFile(
        path=path,
        source_root=path.parent,
        size_bytes=path.stat().st_size if path.exists() else 0,
    )


def create_pdf_with_metadata(path: Path) -> Path:
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    writer.add_metadata(
        {
            "/Title": "Essential Grammar in Use",
            "/Author": "Raymond Murphy",
            "/Subject": "English grammar reference",
        }
    )

    with path.open("wb") as file:
        writer.write(file)

    return path


def test_safe_str_returns_none_for_empty_values():
    assert safe_str(None) is None
    assert safe_str("   ") is None
    assert safe_str(" hello ") == "hello"


def test_truncate_text_normalizes_whitespace():
    assert truncate_text("hello\n\nworld") == "hello world"


def test_inspect_pdf_file_reads_metadata(tmp_path: Path):
    path = create_pdf_with_metadata(tmp_path / "file.pdf")
    pdf_file = make_pdf_file(path)

    insights = inspect_pdf_file(pdf_file)

    assert insights.extraction_error is None
    assert insights.page_count == 1
    assert insights.metadata_title == "Essential Grammar in Use"
    assert insights.metadata_author == "Raymond Murphy"
    assert insights.metadata_subject == "English grammar reference"


def test_inspect_pdf_file_handles_broken_pdf(tmp_path: Path):
    path = tmp_path / "broken.pdf"
    path.write_text("not a pdf", encoding="utf-8")

    pdf_file = make_pdf_file(path)

    insights = inspect_pdf_file(pdf_file)

    assert insights.extraction_error is not None
