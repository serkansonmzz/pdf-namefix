from pathlib import Path

from pdf_namefix.apply_rename import (
    apply_rename_plan,
    build_rename_plan,
)
from pdf_namefix.classifier import classify_pdf_file
from pdf_namefix.models import PdfFile
from pdf_namefix.name_suggester import suggest_filenames


def make_pdf_file(path: Path) -> PdfFile:
    return PdfFile(
        path=path,
        source_root=path.parent,
        size_bytes=path.stat().st_size,
    )


def write_pdf(path: Path) -> Path:
    path.write_text("test", encoding="utf-8")
    return path


def test_build_rename_plan_allows_resolved_collisions(tmp_path: Path):
    scan = write_pdf(tmp_path / "scan.pdf")
    document = write_pdf(tmp_path / "document.pdf")

    classified_files = [
        classify_pdf_file(make_pdf_file(scan)),
        classify_pdf_file(make_pdf_file(document)),
    ]
    suggestions = suggest_filenames(classified_files)

    plan = build_rename_plan(
        suggestions=suggestions,
        warnings=[],
        include_unknown=True,
        min_confidence=0.0,
    )

    assert plan.planned_count == 2
    assert plan.skipped_count == 0
    assert [item.suggested_name for item in plan.items] == [
        "unknown-date_unknown_document.pdf",
        "unknown-date_unknown_document_2.pdf",
    ]


def test_build_rename_plan_skips_existing_target(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_notes.pdf")
    write_pdf(tmp_path / "unknown-date_rust_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])

    plan = build_rename_plan(suggestions=suggestions, warnings=[])

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Target filename already exists."


def test_build_rename_plan_skips_when_name_already_matches(tmp_path: Path):
    source = write_pdf(tmp_path / "unknown-date_rust_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])

    plan = build_rename_plan(suggestions=suggestions, warnings=[])

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Source filename already matches suggested filename."


def test_apply_rename_plan_renames_file_and_writes_log(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_lifetimes_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])
    plan = build_rename_plan(suggestions=suggestions, warnings=[])

    log_dir = tmp_path / ".pdf-namefix" / "logs"
    result = apply_rename_plan(plan=plan, log_dir=log_dir)

    target = tmp_path / "unknown-date_rust_lifetimes_notes.pdf"

    assert result.renamed_count == 1
    assert result.failed_count == 0
    assert source.exists() is False
    assert target.exists() is True
    assert result.log_path is not None
    assert result.log_path.exists()
    assert "unknown-date_rust_lifetimes_notes.pdf" in result.log_path.read_text(
        encoding="utf-8"
    )


def test_apply_rename_plan_does_not_overwrite_existing_target(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_lifetimes_notes.pdf")
    existing = write_pdf(tmp_path / "unknown-date_rust_lifetimes_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])
    plan = build_rename_plan(suggestions=suggestions, warnings=[])

    log_dir = tmp_path / ".pdf-namefix" / "logs"
    result = apply_rename_plan(plan=plan, log_dir=log_dir)

    assert result.renamed_count == 0
    assert source.exists() is True
    assert existing.exists() is True


def test_build_rename_plan_skips_missing_source_after_scan(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_lifetimes_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])

    source.unlink()

    plan = build_rename_plan(suggestions=suggestions, warnings=[])

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Source file no longer exists."


def test_apply_rename_log_includes_operation(tmp_path: Path):
    source = write_pdf(tmp_path / "rust_lifetimes_notes.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])
    plan = build_rename_plan(suggestions=suggestions, warnings=[])

    log_dir = tmp_path / ".pdf-namefix" / "logs"
    result = apply_rename_plan(plan=plan, log_dir=log_dir)

    log_text = result.log_path.read_text(encoding="utf-8")

    assert '"operation": "rename"' in log_text


def test_build_rename_plan_skips_unknown_by_default(tmp_path: Path):
    source = write_pdf(tmp_path / "random_39281.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])

    plan = build_rename_plan(suggestions=suggestions, warnings=[])

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert "Low confidence or unknown type" in plan.items[0].skip_reason


def test_build_rename_plan_can_include_unknown_when_requested(tmp_path: Path):
    source = write_pdf(tmp_path / "random_39281.pdf")

    classified = classify_pdf_file(make_pdf_file(source))
    suggestions = suggest_filenames([classified])

    plan = build_rename_plan(
        suggestions=suggestions,
        warnings=[],
        include_unknown=True,
    )

    assert plan.planned_count == 1
    assert plan.skipped_count == 0
