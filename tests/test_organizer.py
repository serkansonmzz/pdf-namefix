from pathlib import Path

from pdf_namefix.services.classifier import classify_pdf_file
from pdf_namefix.domain.models import DocumentType, PdfFile
from pdf_namefix.app.use_cases.organizer import (
    apply_organize_plan,
    build_organize_plan,
    folder_for_document_type,
)


def write_pdf(path: Path) -> Path:
    path.write_text("test", encoding="utf-8")
    return path


def make_pdf_file(path: Path) -> PdfFile:
    return PdfFile(
        path=path,
        source_root=path.parent,
        size_bytes=path.stat().st_size,
    )


def test_folder_for_document_type_maps_invoice():
    assert folder_for_document_type(DocumentType.INVOICE) == "invoices"


def test_folder_for_document_type_maps_book_and_ebook_to_books():
    assert folder_for_document_type(DocumentType.BOOK) == "books"
    assert folder_for_document_type(DocumentType.EBOOK) == "books"


def test_folder_for_document_type_maps_unknown():
    assert folder_for_document_type(DocumentType.UNKNOWN) == "needs-review"


def test_build_organize_plan_creates_target_path(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_lifetimes_notes.pdf")
    out_dir = tmp_path / "organized"

    classified = classify_pdf_file(make_pdf_file(source))
    plan = build_organize_plan(
        classified_files=[classified],
        warnings=[],
        out_dir=out_dir,
        copy=False,
    )

    assert plan.planned_count == 1
    assert plan.items[0].target_path == out_dir / "notes" / "rust_lifetimes_notes.pdf"
    assert plan.items[0].mode == "move"


def test_build_organize_plan_skips_existing_target(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_lifetimes_notes.pdf")
    out_dir = tmp_path / "organized"
    target_dir = out_dir / "notes"
    target_dir.mkdir(parents=True)
    write_pdf(target_dir / "rust_lifetimes_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    plan = build_organize_plan(
        classified_files=[classified],
        warnings=[],
        out_dir=out_dir,
        copy=False,
    )

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Target file already exists."


def test_apply_organize_plan_moves_file_and_writes_log(tmp_path: Path):
    source = write_pdf(tmp_path / "clean_architecture_book.pdf")
    out_dir = tmp_path / "organized"

    classified = classify_pdf_file(make_pdf_file(source))
    plan = build_organize_plan(
        classified_files=[classified],
        warnings=[],
        out_dir=out_dir,
        copy=False,
    )

    log_dir = tmp_path / ".pdf-namefix" / "logs"
    result = apply_organize_plan(plan=plan, log_dir=log_dir)

    target = out_dir / "books" / "clean_architecture_book.pdf"

    assert result.moved_count == 1
    assert result.copied_count == 0
    assert result.failed_count == 0
    assert source.exists() is False
    assert target.exists() is True
    assert result.log_path is not None
    assert result.log_path.exists()


def test_apply_organize_plan_copies_file_and_keeps_source(tmp_path: Path):
    source = write_pdf(tmp_path / "clean_architecture_book.pdf")
    out_dir = tmp_path / "organized"

    classified = classify_pdf_file(make_pdf_file(source))
    plan = build_organize_plan(
        classified_files=[classified],
        warnings=[],
        out_dir=out_dir,
        copy=True,
    )

    log_dir = tmp_path / ".pdf-namefix" / "logs"
    result = apply_organize_plan(plan=plan, log_dir=log_dir)

    target = out_dir / "books" / "clean_architecture_book.pdf"

    assert result.copied_count == 1
    assert result.moved_count == 0
    assert result.failed_count == 0
    assert source.exists() is True
    assert target.exists() is True


def test_apply_organize_plan_does_not_overwrite_existing_target(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_lifetimes_notes.pdf")
    out_dir = tmp_path / "organized"
    target_dir = out_dir / "notes"
    target_dir.mkdir(parents=True)
    existing = write_pdf(target_dir / "rust_lifetimes_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    plan = build_organize_plan(
        classified_files=[classified],
        warnings=[],
        out_dir=out_dir,
        copy=False,
    )

    log_dir = tmp_path / ".pdf-namefix" / "logs"
    result = apply_organize_plan(plan=plan, log_dir=log_dir)

    assert result.skipped_count == 1
    assert source.exists() is True
    assert existing.exists() is True


def test_build_organize_plan_skips_missing_source_after_scan(tmp_path: Path):
    source = write_pdf(tmp_path / "clean_architecture_book.pdf")
    out_dir = tmp_path / "organized"

    classified = classify_pdf_file(make_pdf_file(source))

    source.unlink()

    plan = build_organize_plan(
        classified_files=[classified],
        warnings=[],
        out_dir=out_dir,
        copy=False,
    )

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Source file no longer exists."


def test_organize_log_includes_operation(tmp_path: Path):
    source = write_pdf(tmp_path / "clean_architecture_book.pdf")
    out_dir = tmp_path / "organized"

    classified = classify_pdf_file(make_pdf_file(source))
    plan = build_organize_plan(
        classified_files=[classified],
        warnings=[],
        out_dir=out_dir,
        copy=False,
    )

    log_dir = tmp_path / ".pdf-namefix" / "logs"
    result = apply_organize_plan(plan=plan, log_dir=log_dir)

    log_text = result.log_path.read_text(encoding="utf-8")

    assert '"operation": "organize"' in log_text
    assert '"mode": "move"' in log_text
