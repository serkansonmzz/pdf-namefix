import json
from pathlib import Path

from pdf_namefix.services.classifier import classify_pdf_file
from pdf_namefix.domain.models import PdfFile
from pdf_namefix.services.name_suggester import suggest_filenames
from pdf_namefix.services.preview_report import build_preview_report
from pdf_namefix.infrastructure.report_exporter import (
    render_json_report,
    render_markdown_report,
    report_to_dict,
    write_report,
)


def make_pdf_file(name: str) -> PdfFile:
    return PdfFile(
        path=Path(name),
        source_root=Path("."),
        size_bytes=100,
    )


def make_report():
    files = [
        make_pdf_file("clean_architecture_book.pdf"),
        make_pdf_file("random_39281.pdf"),
    ]

    classified = [classify_pdf_file(file) for file in files]
    suggestions = suggest_filenames(classified)

    return build_preview_report(suggestions=suggestions, warnings=[])


def test_report_to_dict_contains_summary_and_suggestions():
    report = make_report()

    data = report_to_dict(report)

    assert "generated_at" in data
    assert data["summary"]["total_files"] == 2
    assert len(data["suggestions"]) == 2
    assert data["warnings"] == []


def test_render_json_report_outputs_valid_json():
    report = make_report()

    content = render_json_report(report)
    data = json.loads(content)

    assert data["summary"]["total_files"] == 2
    assert len(data["suggestions"]) == 2


def test_render_markdown_report_contains_summary_and_table():
    report = make_report()

    content = render_markdown_report(report)

    assert "# pdf-namefix Preview Report" in content
    assert "## Summary" in content
    assert "## Suggestions" in content
    assert "| Current file |" in content
    assert "clean_architecture_book.pdf" in content


def test_write_markdown_report(tmp_path: Path):
    report = make_report()
    out = tmp_path / "report.md"

    written = write_report(report=report, report_format="markdown", out_path=out)

    assert written == out
    assert out.exists()
    assert "# pdf-namefix Preview Report" in out.read_text(encoding="utf-8")


def test_write_json_report(tmp_path: Path):
    report = make_report()
    out = tmp_path / "report.json"

    written = write_report(report=report, report_format="json", out_path=out)

    assert written == out
    assert out.exists()

    data = json.loads(out.read_text(encoding="utf-8"))

    assert data["summary"]["total_files"] == 2
