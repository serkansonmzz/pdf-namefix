from pathlib import Path

from pdf_namefix.classifier import classify_pdf_file
from pdf_namefix.models import DocumentType, PdfFile
from pdf_namefix.name_suggester import (
    build_title_slug,
    clamp_filename,
    extract_date_from_name,
    has_any_collision,
    slugify_filename_part,
    suggest_filename,
    suggest_filenames,
)


def make_pdf_file(name: str) -> PdfFile:
    return PdfFile(
        path=Path(name),
        source_root=Path("."),
        size_bytes=100,
    )


def test_extract_date_from_year_month_day_filename():
    date = extract_date_from_name(Path("invoice_2026-04-29.pdf"))

    assert date == "2026-04-29"


def test_extract_date_from_day_month_year_filename():
    date = extract_date_from_name(Path("invoice_29-04-2026.pdf"))

    assert date == "2026-04-29"


def test_extract_date_from_compact_filename():
    date = extract_date_from_name(Path("invoice_20260429.pdf"))

    assert date == "2026-04-29"


def test_extract_date_returns_unknown_date_when_missing():
    date = extract_date_from_name(Path("rust_lifetimes_notes.pdf"))

    assert date == "unknown-date"


def test_extract_date_ignores_invalid_month():
    date = extract_date_from_name(Path("invoice_2026-99-29.pdf"))

    assert date == "unknown-date"


def test_slugify_filename_part_normalizes_turkish_characters():
    slug = slugify_filename_part("kira sözleşme eğitim fiş")

    assert slug == "kira_sozlesme_egitim_fis"


def test_build_title_slug_removes_date_and_noise_words():
    # 'scan' is noise, '2026-04-29' is date, 'final' is noise, 'invoice' is type.
    # build_title_slug(Path("scan_2026-04-29_final_invoice.pdf"), "invoice")
    # 1. strip_date_patterns -> "scan_ _final_invoice"
    # 2. slugify -> "scan_final_invoice"
    # 3. filter noise -> ["invoice"]
    # 4. remove trailing type -> []
    # 5. empty -> "unknown"
    slug = build_title_slug(Path("scan_2026-04-29_final_invoice.pdf"), "invoice")

    assert slug == "unknown"


def test_build_title_slug_removes_trailing_document_type():
    slug = build_title_slug(Path("rust_lifetimes_notes.pdf"), "notes")

    assert slug == "rust_lifetimes"


def test_build_title_slug_returns_unknown_when_empty():
    slug = build_title_slug(Path("scan.pdf"), "document")

    assert slug == "unknown"


def test_clamp_filename_keeps_short_filename():
    filename = clamp_filename("unknown-date_rust_notes.pdf", max_length=120)

    assert filename == "unknown-date_rust_notes.pdf"


def test_clamp_filename_shortens_long_filename_and_keeps_pdf_suffix():
    filename = clamp_filename(f"{'a' * 200}.pdf", max_length=120)

    assert len(filename) <= 120
    assert filename.endswith(".pdf")


def test_suggest_filename_for_notes_pdf():
    pdf_file = make_pdf_file("rust_lifetimes_notes.pdf")
    classified = classify_pdf_file(pdf_file)

    suggestion = suggest_filename(classified)

    assert classified.document_type == DocumentType.NOTES
    assert suggestion.suggested_name == "unknown-date_rust_lifetimes_notes.pdf"


def test_suggest_filename_for_invoice_with_date():
    pdf_file = make_pdf_file("turkcell_fatura_2026-04-29.pdf")
    classified = classify_pdf_file(pdf_file)

    suggestion = suggest_filename(classified)

    assert classified.document_type == DocumentType.INVOICE
    assert suggestion.suggested_name == "2026-04-29_turkcell_fatura_invoice.pdf"


def test_suggest_filename_for_unknown_pdf():
    pdf_file = make_pdf_file("random_39281.pdf")
    classified = classify_pdf_file(pdf_file)

    suggestion = suggest_filename(classified)

    assert classified.document_type == DocumentType.UNKNOWN
    assert suggestion.suggested_name == "unknown-date_random_39281_unknown.pdf"


def test_suggest_filenames_marks_collisions():
    files = [
        make_pdf_file("scan.pdf"),
        make_pdf_file("document.pdf"),
    ]
    classified_files = [classify_pdf_file(file) for file in files]

    suggestions = suggest_filenames(classified_files)

    assert len(suggestions) == 2
    assert all(suggestion.has_collision for suggestion in suggestions)
    assert all(
        suggestion.collision_group == "unknown-date_unknown_document.pdf"
        for suggestion in suggestions
    )


def test_suggest_filenames_does_not_mark_unique_names_as_collisions():
    files = [
        make_pdf_file("rust_lifetimes_notes.pdf"),
        make_pdf_file("clean_architecture_book.pdf"),
    ]
    classified_files = [classify_pdf_file(file) for file in files]

    suggestions = suggest_filenames(classified_files)

    assert len(suggestions) == 2
    assert all(not suggestion.has_collision for suggestion in suggestions)
    assert all(suggestion.collision_group is None for suggestion in suggestions)


def test_has_any_collision_returns_true_for_collisions():
    files = [
        make_pdf_file("scan.pdf"),
        make_pdf_file("document.pdf"),
    ]
    classified_files = [classify_pdf_file(file) for file in files]
    suggestions = suggest_filenames(classified_files)

    assert has_any_collision(suggestions) is True


def test_has_any_collision_returns_false_for_unique_suggestions():
    files = [
        make_pdf_file("rust_lifetimes_notes.pdf"),
        make_pdf_file("clean_architecture_book.pdf"),
    ]
    classified_files = [classify_pdf_file(file) for file in files]
    suggestions = suggest_filenames(classified_files)

    assert has_any_collision(suggestions) is False
