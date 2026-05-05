import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UndoLogEntry:
    operation: str
    source_path: Path
    target_path: Path
    status: str
    mode: str | None = None
    error: str | None = None


@dataclass(frozen=True)
class UndoPlanItem:
    source_path: Path
    target_path: Path
    operation: str
    action: str
    skipped: bool = False
    skip_reason: str | None = None


@dataclass(frozen=True)
class UndoPlan:
    log_path: Path
    items: list[UndoPlanItem]

    @property
    def planned_count(self) -> int:
        return sum(1 for item in self.items if not item.skipped)

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.items if item.skipped)


@dataclass(frozen=True)
class UndoResultItem:
    source_path: Path
    target_path: Path
    status: str
    action: str
    error: str | None = None


@dataclass(frozen=True)
class UndoResult:
    items: list[UndoResultItem]

    @property
    def undone_count(self) -> int:
        return sum(1 for item in self.items if item.status == "undone")

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.items if item.status == "skipped")

    @property
    def failed_count(self) -> int:
        return sum(1 for item in self.items if item.status == "failed")


def find_latest_log(log_dir: Path) -> Path | None:
    if not log_dir.exists():
        return None

    logs = sorted(
        [
            path
            for path in log_dir.glob("*.jsonl")
            if path.name.startswith(("rename-log-", "organize-log-"))
        ],
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    return logs[0] if logs else None


def read_undo_log(log_path: Path) -> list[UndoLogEntry]:
    entries: list[UndoLogEntry] = []

    with log_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue

            entries.append(
                UndoLogEntry(
                    operation=payload.get("operation", "unknown"),
                    source_path=Path(payload["source_path"]),
                    target_path=Path(payload["target_path"]),
                    status=payload.get("status", "unknown"),
                    mode=payload.get("mode"),
                    error=payload.get("error"),
                )
            )

    return entries


def build_undo_plan(log_path: Path) -> UndoPlan:
    entries = read_undo_log(log_path)
    items: list[UndoPlanItem] = []

    for entry in reversed(entries):
        if entry.status not in {"renamed", "moved", "copied"}:
            items.append(
                UndoPlanItem(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    operation=entry.operation,
                    action="skip",
                    skipped=True,
                    skip_reason=f"Cannot undo status: {entry.status}",
                )
            )
            continue

        if entry.status == "copied":
            items.append(
                UndoPlanItem(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    operation=entry.operation,
                    action="skip",
                    skipped=True,
                    skip_reason="Copy undo is not destructive by default.",
                )
            )
            continue

        if not entry.target_path.exists():
            items.append(
                UndoPlanItem(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    operation=entry.operation,
                    action="move_back",
                    skipped=True,
                    skip_reason="Target path no longer exists.",
                )
            )
            continue

        if entry.source_path.exists():
            items.append(
                UndoPlanItem(
                    source_path=entry.source_path,
                    target_path=entry.target_path,
                    operation=entry.operation,
                    action="move_back",
                    skipped=True,
                    skip_reason="Original source path already exists.",
                )
            )
            continue

        items.append(
            UndoPlanItem(
                source_path=entry.source_path,
                target_path=entry.target_path,
                operation=entry.operation,
                action="move_back",
            )
        )

    return UndoPlan(log_path=log_path, items=items)


def apply_undo_plan(plan: UndoPlan) -> UndoResult:
    result_items: list[UndoResultItem] = []

    for item in plan.items:
        if item.skipped:
            result_items.append(
                UndoResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="skipped",
                    action=item.action,
                    error=item.skip_reason,
                )
            )
            continue

        try:
            item.target_path.rename(item.source_path)

            result_items.append(
                UndoResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="undone",
                    action=item.action,
                )
            )

        except OSError as exc:
            result_items.append(
                UndoResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="failed",
                    action=item.action,
                    error=str(exc),
                )
            )

    return UndoResult(items=result_items)
