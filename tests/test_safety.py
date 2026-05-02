from pathlib import Path

from pdf_namefix.safety import check_output_not_inside_inputs, format_bytes


def test_check_output_not_inside_inputs_blocks_nested_output(tmp_path: Path):
    input_dir = tmp_path / "input"
    out_dir = input_dir / "organized"
    input_dir.mkdir()

    result = check_output_not_inside_inputs(out_dir=out_dir, input_paths=[input_dir])

    assert result.ok is False
    assert "Output folder is inside an input folder" in result.reason


def test_check_output_not_inside_inputs_allows_external_output(tmp_path: Path):
    input_dir = tmp_path / "input"
    out_dir = tmp_path / "organized"
    input_dir.mkdir()

    result = check_output_not_inside_inputs(out_dir=out_dir, input_paths=[input_dir])

    assert result.ok is True


def test_format_bytes():
    assert format_bytes(1024) == "1.0 KB"
