import json
from datetime import datetime, timezone
from pathlib import Path

from pdf_namefix.models import FilenameSuggestion, ScanWarning
from pdf_namefix.services.preview_report import PreviewReport


SUPPORTED_REPORT_FORMATS = {"text", "markdown", "json"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def suggestion_to_dict(suggestion: FilenameSuggestion) -> dict:
    classified = suggestion.classified_pdf_file
    pdf_file = classified.pdf_file

    return {
        "source_path": str(pdf_file.path),
        "source_name": pdf_file.path.name,
        "source_root": str(pdf_file.source_root),
        "size_bytes": pdf_file.size_bytes,
        "document_type": classified.document_type.value,
        "confidence": classified.confidence,
        "classification_reason": classified.reason,
        "suggested_name": suggestion.suggested_name,
        "suggestion_reason": suggestion.reason,
        "has_collision": suggestion.has_collision,
        "collision_resolved": suggestion.collision_resolved,
        "collision_group": suggestion.collision_group,
        "original_suggested_name": suggestion.original_suggested_name,
    }


def warning_to_dict(warning: ScanWarning) -> dict:
    return {
        "path": str(warning.path),
        "reason": warning.reason,
    }


def report_to_dict(report: PreviewReport) -> dict:
    return {
        "generated_at": utc_now_iso(),
        "summary": {
            "total_files": report.summary.total_files,
            "unknown_count": report.summary.unknown_count,
            "collision_count": report.summary.collision_count,
            "warning_count": report.summary.warning_count,
        },
        "suggestions": [
            suggestion_to_dict(suggestion)
            for suggestion in report.suggestions
        ],
        "warnings": [
            warning_to_dict(warning)
            for warning in report.warnings
        ],
    }


def render_json_report(report: PreviewReport) -> str:
    return json.dumps(
        report_to_dict(report),
        ensure_ascii=False,
        indent=2,
    )


def render_markdown_report(report: PreviewReport) -> str:
    data = report_to_dict(report)
    summary = data["summary"]

    lines: list[str] = []

    lines.append("# pdf-namefix Preview Report")
    lines.append("")
    lines.append(f"Generated at: `{data['generated_at']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Total PDF files: {summary['total_files']}")
    lines.append(f"- Unknown type: {summary['unknown_count']}")
    lines.append(f"- Suggested name collisions: {summary['collision_count']}")
    lines.append(f"- Warnings: {summary['warning_count']}")
    lines.append("")

    lines.append("## Suggestions")
    lines.append("")
    lines.append(
        "| # | Current file | Type | Confidence | Suggested name | Collision | Reason |"
    )
    lines.append(
        "|---:|---|---|---:|---|---|---|"
    )

    for index, suggestion in enumerate(report.suggestions, start=1):
        classified = suggestion.classified_pdf_file
        pdf_file = classified.pdf_file

        collision = "resolved" if suggestion.collision_resolved else (
            "yes" if suggestion.has_collision else "no"
        )

        lines.append(
            "| "
            f"{index} | "
            f"`{pdf_file.path.name}` | "
            f"{classified.document_type.value} | "
            f"{classified.confidence:.2f} | "
            f"`{suggestion.suggested_name}` | "
            f"{collision} | "
            f"{classified.reason} |"
        )

    if report.warnings:
        lines.append("")
        lines.append("## Warnings")
        lines.append("")

        for warning in report.warnings:
            lines.append(f"- `{warning.path}`: {warning.reason}")

    lines.append("")

    return "\n".join(lines)


def render_report(report: PreviewReport, report_format: str) -> str:
    if report_format == "json":
        return render_json_report(report)

    if report_format == "markdown":
        return render_markdown_report(report)

    raise ValueError(f"Unsupported report format: {report_format}")


def write_report(
    report: PreviewReport,
    report_format: str,
    out_path: Path,
    overwrite: bool = False,
) -> Path:
    if out_path.exists() and not overwrite:
        raise FileExistsError(f"Report file already exists: {out_path}")

    content = render_report(report=report, report_format=report_format)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")

    return out_path
