from typer.testing import CliRunner

from pdf_namefix import __version__
from pdf_namefix.cli import app


runner = CliRunner()


def test_help_command():
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Preview and safely rename messy PDF files" in result.output
    assert "preview" in result.output
    assert "apply" in result.output
    assert "organize" in result.output


def test_version_command():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert f"pdf-namefix {__version__}" in result.output


def test_preview_accepts_single_path(tmp_path):
    pdf = tmp_path / "sample_invoice_2026-04-29.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path)])

    assert result.exit_code == 0
    assert "Preview mode" in result.output
    assert "No files will be renamed" in result.output
    assert "PDF files found: 1" in result.output
    assert "sample_invoice" in result.output
    assert "invoice" in result.output
    assert "2026-04-29_sample_invoice.pdf" in result.output


def test_preview_accepts_multiple_paths(tmp_path):
    folder_a = tmp_path / "a"
    folder_b = tmp_path / "b"
    folder_a.mkdir()
    folder_b.mkdir()

    (folder_a / "one_invoice.pdf").write_text("test", encoding="utf-8")
    (folder_b / "two_book.pdf").write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(folder_a), str(folder_b)])

    assert result.exit_code == 0
    assert "PDF files found: 2" in result.output
    assert "one_invoice" in result.output
    assert "two_book" in result.output
    assert "invoice" in result.output
    assert "book" in result.output
    assert "unknown-date_one_invoice.pdf" in result.output
    assert "unknown-date_two_book.pdf" in result.output


def test_preview_recursive_flag(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "inside_slides.pdf").write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path), "--recursive"])

    assert result.exit_code == 0
    assert "PDF files found: 1" in result.output
    assert "inside" in result.output
    assert "slide" in result.output
    assert "confidence=0.9" in result.output
    assert "unknown-date_inside_slides.pdf" in result.output


def test_preview_unknown_file_type(tmp_path):
    pdf = tmp_path / "random_39281.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path)])

    assert result.exit_code == 0
    assert "PDF files found: 1" in result.output
    assert "random_39281" in result.output
    assert "unknown" in result.output
    assert "unknown-date_random_39281_unknown.pdf" in result.output


def test_preview_missing_path_shows_warning(tmp_path):
    missing = tmp_path / "missing"

    result = runner.invoke(app, ["preview", str(missing)])

    assert result.exit_code == 0
    assert "PDF files found: 0" in result.output
    assert "Warnings" in result.output
    assert "does not exist" in result.output


def test_apply_renames_file_with_yes(tmp_path):
    pdf = tmp_path / "rust_lifetimes_notes.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["apply", str(tmp_path), "--yes"])

    target = tmp_path / "unknown-date_rust_lifetimes_notes.pdf"

    assert result.exit_code == 0
    assert "Apply mode" in result.output
    assert "Planned renames: 1" in result.output
    assert "Renamed: 1" in result.output
    assert pdf.exists() is False
    assert target.exists() is True


def test_apply_blocks_collision(tmp_path):
    scan = tmp_path / "scan.pdf"
    document = tmp_path / "document.pdf"
    scan.write_text("test", encoding="utf-8")
    document.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["apply", str(tmp_path), "--yes"])

    assert result.exit_code == 1
    assert "Apply blocked because suggested filename collisions were found" in result.output
    assert scan.exists() is True
    assert document.exists() is True


def test_apply_cancelled_without_confirmation(tmp_path):
    pdf = tmp_path / "rust_lifetimes_notes.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["apply", str(tmp_path)], input="n\n")

    target = tmp_path / "unknown-date_rust_lifetimes_notes.pdf"

    assert result.exit_code == 1
    assert "Apply cancelled" in result.output
    assert pdf.exists() is True
    assert target.exists() is False


def test_organize_moves_file_with_yes(tmp_path):
    source_dir = tmp_path / "source"
    out_dir = tmp_path / "organized"
    source_dir.mkdir()

    pdf = source_dir / "clean_architecture_book.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(
        app,
        ["organize", str(source_dir), "--out", str(out_dir), "--yes"],
    )

    target = out_dir / "books" / "clean_architecture_book.pdf"

    assert result.exit_code == 0
    assert "Organize mode" in result.output
    assert "Mode: move" in result.output
    assert "Planned operations: 1" in result.output
    assert "Moved: 1" in result.output
    assert pdf.exists() is False
    assert target.exists() is True


def test_organize_copies_file_with_copy_flag(tmp_path):
    source_dir = tmp_path / "source"
    out_dir = tmp_path / "organized"
    source_dir.mkdir()

    pdf = source_dir / "clean_architecture_book.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(
        app,
        ["organize", str(source_dir), "--out", str(out_dir), "--copy", "--yes"],
    )

    target = out_dir / "books" / "clean_architecture_book.pdf"

    assert result.exit_code == 0
    assert "Mode: copy" in result.output
    assert "Copied: 1" in result.output
    assert pdf.exists() is True
    assert target.exists() is True


def test_organize_cancelled_without_confirmation(tmp_path):
    source_dir = tmp_path / "source"
    out_dir = tmp_path / "organized"
    source_dir.mkdir()

    pdf = source_dir / "clean_architecture_book.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(
        app,
        ["organize", str(source_dir), "--out", str(out_dir)],
        input="n\n",
    )

    target = out_dir / "books" / "clean_architecture_book.pdf"

    assert result.exit_code == 1
    assert "Organize cancelled" in result.output
    assert pdf.exists() is True
    assert target.exists() is False


def test_organize_skips_existing_target(tmp_path):
    source_dir = tmp_path / "source"
    out_dir = tmp_path / "organized"
    target_dir = out_dir / "books"

    source_dir.mkdir()
    target_dir.mkdir(parents=True)

    pdf = source_dir / "clean_architecture_book.pdf"
    pdf.write_text("test", encoding="utf-8")

    existing = target_dir / "clean_architecture_book.pdf"
    existing.write_text("existing", encoding="utf-8")

    result = runner.invoke(
        app,
        ["organize", str(source_dir), "--out", str(out_dir), "--yes"],
    )

    assert result.exit_code == 0
    assert "SKIP" in result.output
    assert "Target file already exists" in result.output
    assert pdf.exists() is True
    assert existing.exists() is True


def test_preview_shows_summary(tmp_path):
    pdf = tmp_path / "sample_invoice_2026-04-29.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path)])

    assert result.exit_code == 0
    assert "Summary" in result.output
    assert "Total PDF files: 1" in result.output
    assert "Unknown type: 0" in result.output
    assert "Suggested name collisions: 0" in result.output
    assert "Warnings: 0" in result.output


def test_preview_marks_filename_collisions(tmp_path):
    scan = tmp_path / "scan.pdf"
    document = tmp_path / "document.pdf"
    scan.write_text("test", encoding="utf-8")
    document.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path)])

    assert result.exit_code == 0
    assert "[COLLISION]" in result.output
    assert "Suggested name collisions: 2" in result.output
    assert "Do not apply renames until collisions" in result.output


def test_preview_verbose_shows_reasons(tmp_path):
    pdf = tmp_path / "sample_invoice_2026-04-29.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path), "--verbose"])

    assert result.exit_code == 0
    assert "classification:" in result.output
    assert "suggestion:" in result.output


def test_preview_default_hides_reasons(tmp_path):
    pdf = tmp_path / "sample_invoice_2026-04-29.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path)])

    assert result.exit_code == 0
    assert "classification:" not in result.output
    assert "suggestion:" not in result.output


def test_preview_empty_folder_shows_zero_summary(tmp_path):
    result = runner.invoke(app, ["preview", str(tmp_path)])

    assert result.exit_code == 0
    assert "PDF files found: 0" in result.output
    assert "Total PDF files: 0" in result.output
    assert "Warnings: 0" in result.output


def test_apply_empty_folder_does_nothing(tmp_path):
    result = runner.invoke(app, ["apply", str(tmp_path), "--yes"])

    assert result.exit_code == 0
    assert "PDF files found: 0" in result.output
    assert "No files to rename" in result.output


def test_organize_empty_folder_does_nothing(tmp_path):
    out_dir = tmp_path / "organized"

    result = runner.invoke(
        app,
        ["organize", str(tmp_path), "--out", str(out_dir), "--yes"],
    )

    assert result.exit_code == 0
    assert "PDF files found: 0" in result.output
    assert "No files to organize" in result.output