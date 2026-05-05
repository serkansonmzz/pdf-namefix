from pathlib import Path

from pdf_namefix.services.classifier import classify_pdf_file
from pdf_namefix.domain.models import PdfFile, ScanWarning
from pdf_namefix.services.name_suggester import suggest_filenames
from pdf_namefix.services.preview_report import (
    build_preview_report,
    build_preview_summary,
    filter_suggestions_by_type,
    limit_suggestions,
)
from pdf_namefix.domain.models import DocumentType

def make_pdf_file(name: str) -> PdfFile:
    return PdfFile(
        path=Path(name),
        source_root=Path("."),
        size_bytes=100,
    )


def test_build_preview_summary_counts_total_unknown_collisions_and_warnings():
    classified_files = [
        classify_pdf_file(make_pdf_file("scan.pdf")),
        classify_pdf_file(make_pdf_file("document.pdf")),
        classify_pdf_file(make_pdf_file("random_39281.pdf")),
    ]
    suggestions = suggest_filenames(classified_files)
    warnings = [ScanWarning(path=Path("missing"), reason="Path does not exist.")]

    summary = build_preview_summary(suggestions=suggestions, warnings=warnings)

    assert summary.total_files == 3
    assert summary.unknown_count == 1
    assert summary.collision_count == 2
    assert summary.warning_count == 1


def test_build_preview_report_keeps_suggestions_and_warnings():
    classified_files = [
        classify_pdf_file(make_pdf_file("rust_notes.pdf")),
    ]
    suggestions = suggest_filenames(classified_files)
    warnings = [ScanWarning(path=Path("missing"), reason="Path does not exist.")]

    report = build_preview_report(suggestions=suggestions, warnings=warnings)

    assert report.suggestions == suggestions
    assert report.warnings == warnings
    assert report.summary.total_files == 1
    assert report.summary.warning_count == 1


def test_filter_suggestions_by_type():
    classified_files = [
        classify_pdf_file(make_pdf_file("random_39281.pdf")),
        classify_pdf_file(make_pdf_file("Transcript - Advanced Episode.pdf")),
    ]
    suggestions = suggest_filenames(classified_files)

    filtered = filter_suggestions_by_type(suggestions, only_type="unknown")

    assert len(filtered) == 1
    assert filtered[0].classified_pdf_file.document_type == DocumentType.UNKNOWN


def test_limit_suggestions():
    classified_files = [
        classify_pdf_file(make_pdf_file("one_book.pdf")),
        classify_pdf_file(make_pdf_file("two_book.pdf")),
    ]
    suggestions = suggest_filenames(classified_files)

    limited = limit_suggestions(suggestions, limit=1)

    assert len(limited) == 1
