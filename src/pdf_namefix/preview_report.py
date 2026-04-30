from dataclasses import dataclass

from pdf_namefix.models import DocumentType, FilenameSuggestion, ScanWarning


@dataclass(frozen=True)
class PreviewSummary:
    total_files: int
    unknown_count: int
    collision_count: int
    warning_count: int


@dataclass(frozen=True)
class PreviewReport:
    suggestions: list[FilenameSuggestion]
    warnings: list[ScanWarning]
    summary: PreviewSummary


def build_preview_summary(
    suggestions: list[FilenameSuggestion],
    warnings: list[ScanWarning],
) -> PreviewSummary:
    unknown_count = sum(
        1
        for suggestion in suggestions
        if suggestion.classified_pdf_file.document_type == DocumentType.UNKNOWN
    )

    collision_count = sum(1 for suggestion in suggestions if suggestion.has_collision)

    return PreviewSummary(
        total_files=len(suggestions),
        unknown_count=unknown_count,
        collision_count=collision_count,
        warning_count=len(warnings),
    )


def build_preview_report(
    suggestions: list[FilenameSuggestion],
    warnings: list[ScanWarning],
) -> PreviewReport:
    return PreviewReport(
        suggestions=suggestions,
        warnings=warnings,
        summary=build_preview_summary(suggestions, warnings),
    )
