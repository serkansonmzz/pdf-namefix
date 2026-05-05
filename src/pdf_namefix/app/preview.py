from pathlib import Path

import typer
from rich.console import Console

from pdf_namefix.services.apply_ai_suggestions import (
    apply_ai_suggestions_to_filename_suggestions,
    load_ai_suggestion_map,
)
from pdf_namefix.services.classifier import classify_pdf_files
from pdf_namefix.services.name_suggester import suggest_filenames
from pdf_namefix.domain.naming_profile import load_naming_profile
from pdf_namefix.services.pdf_inspector import inspect_pdf_files
from pdf_namefix.services.preview_report import (
    build_preview_report,
    filter_suggestions_by_type,
    limit_suggestions,
)
from pdf_namefix.infrastructure.report_exporter import SUPPORTED_REPORT_FORMATS, write_report
from pdf_namefix.services.scanner import scan_pdf_files


def run_preview(
    *,
    console: Console,
    paths: list[Path],
    recursive: bool = False,
    verbose: bool = False,
    summary_only: bool = False,
    only: str | None = None,
    limit: int | None = None,
    inspect_pdf: bool = False,
    profile: Path | None = None,
    ai_suggestions: Path | None = None,
    output_format: str = "text",
    out: Path | None = None,
    overwrite_report: bool = False,
) -> None:
    console.print("[bold]Preview mode[/bold]")
    console.print("No files will be renamed in this command.")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    classified_files = classify_pdf_files(
        result.pdf_files,
        insights_by_path=insights_by_path,
    )
    naming_profile = load_naming_profile(profile)
    suggestions = suggest_filenames(classified_files, profile=naming_profile)

    if ai_suggestions is not None:
        ai_map = load_ai_suggestion_map(ai_suggestions)
        suggestions = apply_ai_suggestions_to_filename_suggestions(
            suggestions=suggestions,
            ai_map=ai_map,
            min_confidence=0.0,
        )

    report = build_preview_report(suggestions=suggestions, warnings=result.warnings)

    if output_format not in SUPPORTED_REPORT_FORMATS:
        console.print(
            f"[red]Unsupported format: {output_format}. "
            f"Supported formats: {', '.join(sorted(SUPPORTED_REPORT_FORMATS))}[/red]"
        )
        raise typer.Exit(code=1)

    if output_format in {"markdown", "json"} and out is None:
        console.print(
            "[red]--out is required when using --format markdown or --format json.[/red]"
        )
        raise typer.Exit(code=1)

    if output_format == "text" and out is not None:
        console.print(
            "[red]--out is only supported with --format markdown or --format json.[/red]"
        )
        raise typer.Exit(code=1)

    if output_format in {"markdown", "json"} and out is not None:
        try:
            written_path = write_report(
                report=report,
                report_format=output_format,
                out_path=out,
                overwrite=overwrite_report,
            )
        except FileExistsError as exc:
            console.print(f"[red]{exc}[/red]")
            console.print("Use --overwrite-report to replace it.")
            raise typer.Exit(code=1)

        console.print("[bold]Preview report exported[/bold]")
        console.print(f"- Format: {output_format}")
        console.print(f"- Output: {written_path}")
        console.print(f"- Total PDF files: {report.summary.total_files}")
        console.print(f"- Unknown type: {report.summary.unknown_count}")
        console.print(f"- Suggested name collisions: {report.summary.collision_count}")
        console.print(f"- Warnings: {report.summary.warning_count}")
        return

    console.print(f"PDF files found: [bold]{report.summary.total_files}[/bold]")

    display_suggestions = filter_suggestions_by_type(
        report.suggestions,
        only_type=only,
    )
    display_suggestions = limit_suggestions(
        display_suggestions,
        limit=limit,
    )

    if display_suggestions and not summary_only:
        console.print("")
        if only:
            console.print(f"Filter: [bold]{only}[/bold]")
        if limit is not None:
            console.print(f"Displayed items limit: [bold]{limit}[/bold]")

        for index, suggestion in enumerate(display_suggestions, start=1):
            classified = suggestion.classified_pdf_file
            pdf_file = classified.pdf_file
            size_kb = pdf_file.size_bytes / 1024

            if suggestion.collision_resolved:
                collision_label = " [yellow][RESOLVED COLLISION][/yellow]"
            elif suggestion.has_collision:
                collision_label = " [red][COLLISION][/red]"
            else:
                collision_label = ""

            console.print(
                fr"{index}. {pdf_file.path} "
                f"[dim]({size_kb:.1f} KB)[/dim] "
                fr"[cyan]\[{classified.document_type.value}][/cyan] "
                f"[dim]confidence={classified.confidence:.1f}[/dim]"
                f"{collision_label}"
            )
            console.print(f"   → [green]{suggestion.suggested_name}[/green]")

            if verbose:
                console.print(f"   [dim]classification: {classified.reason}[/dim]")
                console.print(f"   [dim]suggestion: {suggestion.reason}[/dim]")
                if suggestion.original_suggested_name:
                    console.print(
                        f"   [dim]original suggestion: {suggestion.original_suggested_name}[/dim]"
                    )
                if inspect_pdf:
                    insight = insights_by_path.get(pdf_file.path)
                    if insight and insight.extraction_error:
                        console.print(f"   [dim]inspection error: {insight.extraction_error}[/dim]")
                    elif insight and insight.metadata_title:
                        console.print(f"   [dim]metadata title: {insight.metadata_title}[/dim]")

    if report.warnings:
        console.print("")
        console.print("[yellow]Warnings:[/yellow]")
        for warning in report.warnings:
            console.print(f"- {warning.path}: {warning.reason}")

    console.print("")
    console.print("[bold]Summary[/bold]")
    console.print(f"- Total PDF files: {report.summary.total_files}")
    console.print(f"- PDF inspection: {inspect_pdf}")
    console.print(f"- Unknown type: {report.summary.unknown_count}")
    console.print(f"- Suggested name collisions: {report.summary.collision_count}")
    console.print(f"- Warnings: {report.summary.warning_count}")

    if report.summary.collision_count:
        console.print("")
        console.print(
            "[red]Some suggestions have filename collisions. "
            "Do not apply renames until collisions are resolved.[/red]"
        )
