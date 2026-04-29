from pathlib import Path

from pdf_namefix.scanner import is_pdf_file, scan_pdf_files


def write_file(path: Path, content: str = "test") -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def test_is_pdf_file_accepts_lowercase_pdf(tmp_path: Path):
    pdf = write_file(tmp_path / "sample.pdf")

    assert is_pdf_file(pdf) is True


def test_is_pdf_file_accepts_uppercase_pdf(tmp_path: Path):
    pdf = write_file(tmp_path / "BOOK.PDF")

    assert is_pdf_file(pdf) is True


def test_is_pdf_file_rejects_non_pdf(tmp_path: Path):
    txt = write_file(tmp_path / "notes.txt")

    assert is_pdf_file(txt) is False


def test_scan_finds_pdf_files_in_single_folder(tmp_path: Path):
    write_file(tmp_path / "a.pdf")
    write_file(tmp_path / "b.txt")
    write_file(tmp_path / "c.PDF")

    result = scan_pdf_files([tmp_path])

    assert result.count == 2
    assert sorted(pdf.name for pdf in result.pdf_files) == ["a.pdf", "c.PDF"]
    assert result.warnings == []


def test_scan_accepts_multiple_folders(tmp_path: Path):
    folder_a = tmp_path / "a"
    folder_b = tmp_path / "b"
    folder_a.mkdir()
    folder_b.mkdir()

    write_file(folder_a / "one.pdf")
    write_file(folder_b / "two.pdf")

    result = scan_pdf_files([folder_a, folder_b])

    assert result.count == 2
    assert sorted(pdf.name for pdf in result.pdf_files) == ["one.pdf", "two.pdf"]


def test_scan_deduplicates_same_folder(tmp_path: Path):
    write_file(tmp_path / "one.pdf")

    result = scan_pdf_files([tmp_path, tmp_path])

    assert result.count == 1
    assert result.pdf_files[0].name == "one.pdf"


def test_scan_non_recursive_does_not_find_nested_pdf(tmp_path: Path):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_file(nested / "inside.pdf")

    result = scan_pdf_files([tmp_path], recursive=False)

    assert result.count == 0


def test_scan_recursive_finds_nested_pdf(tmp_path: Path):
    nested = tmp_path / "nested"
    nested.mkdir()
    write_file(nested / "inside.pdf")

    result = scan_pdf_files([tmp_path], recursive=True)

    assert result.count == 1
    assert result.pdf_files[0].name == "inside.pdf"


def test_scan_missing_path_returns_warning(tmp_path: Path):
    missing = tmp_path / "missing"

    result = scan_pdf_files([missing])

    assert result.count == 0
    assert len(result.warnings) == 1
    assert result.warnings[0].path == missing
    assert "does not exist" in result.warnings[0].reason


def test_scan_accepts_direct_pdf_file(tmp_path: Path):
    pdf = write_file(tmp_path / "direct.pdf")

    result = scan_pdf_files([pdf])

    assert result.count == 1
    assert result.pdf_files[0].name == "direct.pdf"


def test_scan_direct_non_pdf_file_returns_warning(tmp_path: Path):
    txt = write_file(tmp_path / "notes.txt")

    result = scan_pdf_files([txt])

    assert result.count == 0
    assert len(result.warnings) == 1
    assert "not a PDF" in result.warnings[0].reason
