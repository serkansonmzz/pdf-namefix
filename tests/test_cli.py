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
    pdf = tmp_path / "sample.pdf"
    pdf.write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path)])

    assert result.exit_code == 0
    assert "Preview mode" in result.output
    assert "No files will be renamed" in result.output
    assert "PDF files found: 1" in result.output
    assert "sample.pdf" in result.output


def test_preview_accepts_multiple_paths(tmp_path):
    folder_a = tmp_path / "a"
    folder_b = tmp_path / "b"
    folder_a.mkdir()
    folder_b.mkdir()

    (folder_a / "one.pdf").write_text("test", encoding="utf-8")
    (folder_b / "two.pdf").write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(folder_a), str(folder_b)])

    assert result.exit_code == 0
    assert "PDF files found: 2" in result.output
    assert "one.pdf" in result.output
    assert "two.pdf" in result.output


def test_preview_recursive_flag(tmp_path):
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "inside.pdf").write_text("test", encoding="utf-8")

    result = runner.invoke(app, ["preview", str(tmp_path), "--recursive"])

    assert result.exit_code == 0
    assert "PDF files found: 1" in result.output
    assert "inside.pdf" in result.output


def test_preview_missing_path_shows_warning(tmp_path):
    missing = tmp_path / "missing"

    result = runner.invoke(app, ["preview", str(missing)])

    assert result.exit_code == 0
    assert "PDF files found: 0" in result.output
    assert "Warnings" in result.output
    assert "does not exist" in result.output


def test_apply_is_skeleton_only():
    result = runner.invoke(app, ["apply", "/tmp"])

    assert result.exit_code == 0
    assert "Apply mode is not implemented yet" in result.output
    assert "Phase 1 only defines the CLI shape" in result.output


def test_organize_is_skeleton_only():
    result = runner.invoke(app, ["organize", "/tmp", "--out", "/tmp/out"])

    assert result.exit_code == 0
    assert "Organize mode is not implemented yet" in result.output
    assert "Output folder: /tmp/out" in result.output