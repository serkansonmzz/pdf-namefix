import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from pdf_namefix.models import (
    ClassifiedPdfFile,
    DocumentType,
    OrganizePlan,
    OrganizePlanItem,
    OrganizeResult,
    OrganizeResultItem,
    ScanWarning,
)


TYPE_FOLDER_MAP: dict[DocumentType, str] = {
    DocumentType.INVOICE: "invoices",
    DocumentType.RECEIPT: "receipts",
    DocumentType.CONTRACT: "contracts",
    DocumentType.REPORT: "reports",
    DocumentType.STATEMENT: "statements",
    DocumentType.TAX: "tax",
    DocumentType.OFFER: "offers",
    DocumentType.APPLICATION: "applications",
    DocumentType.BOOK: "books",
    DocumentType.EBOOK: "books",
    DocumentType.COURSE: "courses",
    DocumentType.LESSON: "lessons",
    DocumentType.NOTES: "notes",
    DocumentType.PAPER: "papers",
    DocumentType.ARTICLE: "articles",
    DocumentType.SLIDES: "slides",
    DocumentType.MANUAL: "manuals",
    DocumentType.TRANSCRIPT: "transcripts",
    DocumentType.WORKSHEET: "worksheets",
    DocumentType.GUIDE: "guides",
    DocumentType.CHEATSHEET: "cheatsheets",
    DocumentType.EXAM: "exams",
    DocumentType.STUDENT_DOCUMENT: "student-documents",
    DocumentType.CV: "cv",
    DocumentType.VISA: "visa",
    DocumentType.MEDICAL: "medical",
    DocumentType.FINANCE: "finance",
    DocumentType.PAYMENT: "payments",
    DocumentType.LANGUAGE_LEARNING: "language-learning",
    DocumentType.REFERENCE: "reference",
    DocumentType.NOVEL: "novels",
    DocumentType.WHITEPAPER: "whitepapers",
    DocumentType.STUDY_MATERIAL: "study-materials",
    DocumentType.DOCUMENT: "documents",
    DocumentType.UNKNOWN: "unknown",
}


def folder_for_document_type(document_type: DocumentType) -> str:
    return TYPE_FOLDER_MAP.get(document_type, "unknown")


def build_organize_plan(
    classified_files: list[ClassifiedPdfFile],
    warnings: list[ScanWarning],
    out_dir: Path,
    copy: bool = False,
) -> OrganizePlan:
    items: list[OrganizePlanItem] = []
    mode = "copy" if copy else "move"

    for classified in classified_files:
        pdf_file = classified.pdf_file
        folder_name = folder_for_document_type(classified.document_type)
        target_dir = out_dir.expanduser() / folder_name
        target_path = target_dir / pdf_file.path.name

        if not pdf_file.path.exists():
            items.append(
                OrganizePlanItem(
                    source_path=pdf_file.path,
                    target_path=target_path,
                    document_type=classified.document_type,
                    mode=mode,
                    skipped=True,
                    skip_reason="Source file no longer exists.",
                )
            )
            continue

        if pdf_file.path.resolve() == target_path.resolve(strict=False):
            items.append(
                OrganizePlanItem(
                    source_path=pdf_file.path,
                    target_path=target_path,
                    document_type=classified.document_type,
                    mode=mode,
                    skipped=True,
                    skip_reason="Source file is already in the target location.",
                )
            )
            continue

        if target_path.exists():
            items.append(
                OrganizePlanItem(
                    source_path=pdf_file.path,
                    target_path=target_path,
                    document_type=classified.document_type,
                    mode=mode,
                    skipped=True,
                    skip_reason="Target file already exists.",
                )
            )
            continue

        items.append(
            OrganizePlanItem(
                source_path=pdf_file.path,
                target_path=target_path,
                document_type=classified.document_type,
                mode=mode,
            )
        )

    return OrganizePlan(items=items, warnings=warnings)


def write_organize_log(
    result: OrganizeResult,
    log_dir: Path,
) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = log_dir / f"organize-log-{timestamp}.jsonl"

    with log_path.open("w", encoding="utf-8") as file:
        for item in result.items:
            payload = {
                "operation": "organize",
                "source_path": str(item.source_path),
                "target_path": str(item.target_path),
                "status": item.status,
                "mode": item.mode,
                "error": item.error,
            }
            file.write(json.dumps(payload, ensure_ascii=False) + "\n")

    return log_path


def apply_organize_plan(
    plan: OrganizePlan,
    log_dir: Path,
) -> OrganizeResult:
    result_items: list[OrganizeResultItem] = []

    for item in plan.items:
        if item.skipped:
            result_items.append(
                OrganizeResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="skipped",
                    mode=item.mode,
                    error=item.skip_reason,
                )
            )
            continue

        try:
            if item.target_path.exists():
                result_items.append(
                    OrganizeResultItem(
                        source_path=item.source_path,
                        target_path=item.target_path,
                        status="failed",
                        mode=item.mode,
                        error="Target file already exists.",
                    )
                )
                continue

            item.target_path.parent.mkdir(parents=True, exist_ok=True)

            if item.mode == "copy":
                shutil.copy2(item.source_path, item.target_path)
                status = "copied"
            else:
                shutil.move(str(item.source_path), str(item.target_path))
                status = "moved"

            result_items.append(
                OrganizeResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status=status,
                    mode=item.mode,
                )
            )

        except OSError as exc:
            result_items.append(
                OrganizeResultItem(
                    source_path=item.source_path,
                    target_path=item.target_path,
                    status="failed",
                    mode=item.mode,
                    error=str(exc),
                )
            )

    result = OrganizeResult(items=result_items)
    log_path = write_organize_log(result=result, log_dir=log_dir)

    return OrganizeResult(items=result_items, log_path=log_path)
