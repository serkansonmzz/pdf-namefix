import json
from pathlib import Path

from pdf_namefix.undo import (
    apply_undo_plan,
    build_undo_plan,
    find_latest_log,
    read_undo_log,
)


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row) + "\n")
    return path


def test_find_latest_log(tmp_path: Path):
    log_dir = tmp_path / ".pdf-namefix" / "logs"
    first = write_jsonl(
        log_dir / "rename-log-20260101T000000Z.jsonl",
        [],
    )
    second = write_jsonl(
        log_dir / "rename-log-20260102T000000Z.jsonl",
        [],
    )

    first.touch()
    second.touch()

    latest = find_latest_log(log_dir)

    assert latest is not None
    assert latest.name in {
        "rename-log-20260101T000000Z.jsonl",
        "rename-log-20260102T000000Z.jsonl",
    }


def test_read_undo_log_reads_entries(tmp_path: Path):
    log_path = write_jsonl(
        tmp_path / "rename-log.jsonl",
        [
            {
                "operation": "rename",
                "source_path": str(tmp_path / "old.pdf"),
                "target_path": str(tmp_path / "new.pdf"),
                "status": "renamed",
                "error": None,
            }
        ],
    )

    entries = read_undo_log(log_path)

    assert len(entries) == 1
    assert entries[0].operation == "rename"
    assert entries[0].status == "renamed"


def test_undo_rename_moves_target_back_to_source(tmp_path: Path):
    source = tmp_path / "old.pdf"
    target = tmp_path / "new.pdf"
    target.write_text("test", encoding="utf-8")

    log_path = write_jsonl(
        tmp_path / ".pdf-namefix" / "logs" / "rename-log.jsonl",
        [
            {
                "operation": "rename",
                "source_path": str(source),
                "target_path": str(target),
                "status": "renamed",
                "error": None,
            }
        ],
    )

    plan = build_undo_plan(log_path)
    result = apply_undo_plan(plan)

    assert result.undone_count == 1
    assert source.exists() is True
    assert target.exists() is False


def test_undo_move_organize_moves_target_back_to_source(tmp_path: Path):
    source = tmp_path / "source" / "book.pdf"
    target = tmp_path / "organized" / "books" / "book.pdf"
    target.parent.mkdir(parents=True)
    target.write_text("test", encoding="utf-8")

    log_path = write_jsonl(
        tmp_path / ".pdf-namefix" / "logs" / "organize-log.jsonl",
        [
            {
                "operation": "organize",
                "source_path": str(source),
                "target_path": str(target),
                "status": "moved",
                "mode": "move",
                "error": None,
            }
        ],
    )

    source.parent.mkdir(parents=True)

    plan = build_undo_plan(log_path)
    result = apply_undo_plan(plan)

    assert result.undone_count == 1
    assert source.exists() is True
    assert target.exists() is False


def test_undo_copy_is_skipped_by_default(tmp_path: Path):
    source = tmp_path / "source.pdf"
    target = tmp_path / "copy.pdf"
    source.write_text("source", encoding="utf-8")
    target.write_text("copy", encoding="utf-8")

    log_path = write_jsonl(
        tmp_path / ".pdf-namefix" / "logs" / "organize-log.jsonl",
        [
            {
                "operation": "organize",
                "source_path": str(source),
                "target_path": str(target),
                "status": "copied",
                "mode": "copy",
                "error": None,
            }
        ],
    )

    plan = build_undo_plan(log_path)

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Copy undo is not destructive by default."


def test_undo_skips_when_source_already_exists(tmp_path: Path):
    source = tmp_path / "old.pdf"
    target = tmp_path / "new.pdf"
    source.write_text("existing", encoding="utf-8")
    target.write_text("target", encoding="utf-8")

    log_path = write_jsonl(
        tmp_path / ".pdf-namefix" / "logs" / "rename-log.jsonl",
        [
            {
                "operation": "rename",
                "source_path": str(source),
                "target_path": str(target),
                "status": "renamed",
                "error": None,
            }
        ],
    )

    plan = build_undo_plan(log_path)

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Original source path already exists."


def test_undo_skips_when_target_missing(tmp_path: Path):
    source = tmp_path / "old.pdf"
    target = tmp_path / "new.pdf"

    log_path = write_jsonl(
        tmp_path / ".pdf-namefix" / "logs" / "rename-log.jsonl",
        [
            {
                "operation": "rename",
                "source_path": str(source),
                "target_path": str(target),
                "status": "renamed",
                "error": None,
            }
        ],
    )

    plan = build_undo_plan(log_path)

    assert plan.planned_count == 0
    assert plan.skipped_count == 1
    assert plan.items[0].skip_reason == "Target path no longer exists."
