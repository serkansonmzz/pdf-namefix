import json
from datetime import datetime, timezone
from pathlib import Path

from pdf_namefix.models import (
    FilenameSuggestion,
    RenamePlan,
    RenamePlanItem,
    RenameResult,
    RenameResultItem,
    ScanWarning,
)


def build_rename_plan(
    suggestions: list[FilenameSuggestion],
    warnings: list[ScanWarning],
) -> RenamePlan:
    items: list[RenamePlanItem] = []

    for suggestion in suggestions:
        classified = suggestion.classified_pdf_file
        pdf_file = classified.pdf_file

        source_path = pdf_file.path
        target_path = source_path.with_name(suggestion.suggested_name)

        if not source_path.exists():
            items.append(
                RenamePlanItem(
                    source_path=source_path,
                    target_path=target_path,
                    original_name=source_path.name,
                    suggested_name=suggestion.suggested_name,
                    document_type=classified.document_type,
                    skipped=True,
                    skip_reason="Source file no longer exists.",
                )
            )
            continue

        if suggestion.has_collision:
            items.append(
                RenamePlanItem(
                    source_path=source_path,
                    target_path=target_path,
                    original_name=source_path.name,
                    suggested_name=suggestion.suggested_name,
                    document_type=classified.document_type,
                    skipped=True,
                    skip_reason="Suggested filename collision.",
                )
            )
            continue

        if source_path.name == suggestion.suggested_name:
            items.append(
                RenamePlanItem(
                    source_path=source_path,
                    target_path=target_path,
                    original_name=source_path.name,
                    suggested_name=suggestion.suggested_name,
                    document_type=classified.document_type,
                    skipped=True,
                    skip_reason="Source filename already matches suggested filename.",
                )
            )
            continue

        if target_path.exists():
            items.append(
                RenamePlanItem(
                    source_path=source_path,
                    target_path=target_path,
                    original_name=source_path.name,
                    suggested_name=suggestion.suggested_name,
                    document_type=classified.document_type,
                    skipped=True,
                    skip_reason="Target filename already exists.",
                )
            )
            continue

        items.append(
            RenamePlanItem(
                source_path=source_path,
                target_path=target_path,
                original_name=source_path.name,
                suggested_name=suggestion.suggested_name,
                document_type=classified.document_type,
            )
        )

    return RenamePlan(items=items, warnings=warnings)


def write_rename_log(
    result: RenameResult,
    log_dir: Path,
) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"rename-log-{timestamp}.jsonl"

    with log_path.open("w", encoding="utf-8") as file:
        for item in result.items:
            payload = {
                "source_path": str(item.source_path),
                "target_path": str(item.target_path),
                "status": item.status,
                "error": item.error,
            }
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return log_path


def apply_rename_plan(
    plan: RenamePlan,
    log_dir: Path,
) -> RenameResult:
    result_items: list[RenameResultItem] = []

    for item in plan.items:
        if item.skipped:
            result_items.append(
                RenameResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="skipped",
                    error=item.skip_reason,
                )
            )
            continue

        try:
            if item.target_path.exists():
                result_items.append(
                    RenameResultItem(
                        source_path=item.source_path,
                        target_path=item.target_path,
                        status="failed",
                        error="Target filename already exists.",
                    )
                )
                continue

            item.source_path.rename(item.target_path)

            result_items.append(
                RenameResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="renamed",
                )
            )

        except OSError as exc:
            result_items.append(
                RenameResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="failed",
                    error=str(exc),
                )
            )

    result = RenameResult(items=result_items)
    log_path = write_rename_log(result=result, log_dir=log_dir)

    return RenameResult(items=result_items, log_path=log_path)
