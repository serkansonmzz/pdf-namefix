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


def test_preview_accepts_single_path():
    result = runner.invoke(app, ["preview", "/tmp"])

    assert result.exit_code == 0
    assert "Preview mode" in result.output
    assert "No files will be renamed" in result.output
    assert "/tmp" in result.output


def test_preview_accepts_multiple_paths():
    result = runner.invoke(app, ["preview", "/tmp", "/var/tmp"])

    assert result.exit_code == 0
    assert "/tmp" in result.output
    assert "/var/tmp" in result.output


def test_preview_recursive_flag():
    result = runner.invoke(app, ["preview", "/tmp", "--recursive"])

    assert result.exit_code == 0
    assert "Recursive scan: enabled" in result.output


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