import json
import os
from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console

from pdf_namefix import __version__
from pdf_namefix.ai_naming import OpenAiNamingClient
from pdf_namefix.apply_rename import apply_rename_plan, build_rename_plan
from pdf_namefix.classifier import classify_pdf_files
from pdf_namefix.models import AiNamingInput
from pdf_namefix.name_suggester import suggest_filenames
from pdf_namefix.naming_profile import load_naming_profile
from pdf_namefix.organizer import apply_organize_plan, build_organize_plan
from pdf_namefix.pdf_inspector import inspect_pdf_files
from pdf_namefix.preview_report import (
    build_preview_report,
    filter_suggestions_by_type,
    limit_suggestions,
)
from pdf_namefix.report_exporter import SUPPORTED_REPORT_FORMATS, write_report
from pdf_namefix.safety import (
    check_disk_space_for_copy,
    check_output_not_inside_inputs,
    format_bytes,
)
from pdf_namefix.scanner import scan_pdf_files
from pdf_namefix.undo import apply_undo_plan, build_undo_plan, find_latest_log


load_dotenv()

app = typer.Typer(
    name="pdf-namefix",
    help="Preview and safely rename messy PDF files.",
    no_args_is_help=True,
)

console = Console()


def version_callback(value: bool) -> None:
    if value:
        console.print(f"pdf-namefix {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            help="Show the installed pdf-namefix version.",
            callback=version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """
    pdf-namefix is a local-first CLI tool for safely previewing and renaming PDFs.
    """
    return None


@app.command()
def preview(
    paths: Annotated[
        list[Path],
        typer.Argument(help="One or more folders to scan for PDF files."),
    ],
    recursive: Annotated[
        bool,
        typer.Option("--recursive", "-r", help="Scan folders recursively."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Show classification and suggestion reasons."),
    ] = False,
    summary_only: Annotated[
        bool,
        typer.Option("--summary-only", help="Show only summary without file details."),
    ] = False,
    only: Annotated[
        str | None,
        typer.Option("--only", help="Show only one document type, e.g. unknown, book, transcript."),
    ] = None,
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Limit displayed file details."),
    ] = None,
    inspect_pdf: Annotated[
        bool,
        typer.Option(
            "--inspect-pdf",
            help="Read PDF metadata and first-page text to improve classification.",
        ),
    ] = False,
    output_format: Annotated[
        str,
        typer.Option(
            "--format",
            help="Output format: text, markdown, or json.",
        ),
    ] = "text",
    out: Annotated[
        Path | None,
        typer.Option(
            "--out",
            help="Write preview report to a file. Requires --format markdown or --format json.",
        ),
    ] = None,
    overwrite_report: Annotated[
        bool,
        typer.Option(
            "--overwrite-report",
            help="Overwrite existing report file.",
        ),
    ] = False,
) -> None:
    """
    Preview discovered PDF files and suggested filenames without touching files.
    """
    console.print("[bold]Preview mode[/bold]")
    console.print("No files will be renamed in this command.")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    classified_files = classify_pdf_files(
        result.pdf_files,
        insights_by_path=insights_by_path,
    )
    suggestions = suggest_filenames(classified_files)
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


@app.command()
def apply(
    paths: Annotated[
        list[Path],
        typer.Argument(help="One or more folders to scan before applying safe renames."),
    ],
    recursive: Annotated[
        bool,
        typer.Option("--recursive", "-r", help="Scan folders recursively."),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Apply changes without interactive confirmation."),
    ] = False,
    include_unknown: Annotated[
        bool,
        typer.Option(
            "--include-unknown",
            help="Allow renaming unknown or low-confidence files.",
        ),
    ] = False,
    min_confidence: Annotated[
        float,
        typer.Option(
            "--min-confidence",
            help="Minimum confidence required for default apply.",
        ),
    ] = 0.7,
    inspect_pdf: Annotated[
        bool,
        typer.Option(
            "--inspect-pdf",
            help="Read PDF metadata and first-page text to improve classification.",
        ),
    ] = False,
) -> None:
    """
    Apply safe PDF filename changes.

    This command renames files only after safety checks.
    """
    console.print("[bold]Apply mode[/bold]")
    console.print("Preparing safe rename plan...")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    classified_files = classify_pdf_files(
        result.pdf_files,
        insights_by_path=insights_by_path,
    )
    suggestions = suggest_filenames(classified_files)
    report = build_preview_report(suggestions=suggestions, warnings=result.warnings)
    plan = build_rename_plan(
        suggestions=report.suggestions,
        warnings=report.warnings,
        include_unknown=include_unknown,
        min_confidence=min_confidence,
    )

    console.print(f"PDF files found: [bold]{report.summary.total_files}[/bold]")
    console.print(f"Include unknown: [bold]{include_unknown}[/bold]")
    console.print(f"Minimum confidence: [bold]{min_confidence}[/bold]")
    console.print(f"Planned renames: [bold]{plan.planned_count}[/bold]")
    console.print(f"Skipped items: [bold]{plan.skipped_count}[/bold]")
    console.print(f"Warnings: [bold]{len(plan.warnings)}[/bold]")
    console.print("")

    if plan.items:
        for index, item in enumerate(plan.items, start=1):
            if item.skipped:
                console.print(
                    f"{index}. [yellow]SKIP[/yellow] {item.source_path.name} "
                    f"→ {item.suggested_name} "
                    f"[dim]reason={item.skip_reason}[/dim]"
                )
            else:
                console.print(
                    f"{index}. [green]RENAME[/green] {item.source_path.name} "
                    f"→ {item.suggested_name}"
                )

    suggested_names = [
        suggestion.suggested_name.lower() for suggestion in report.suggestions
    ]
    if len(suggested_names) != len(set(suggested_names)):
        console.print("")
        console.print(
            "[red]Apply blocked because unresolved filename collisions remain.[/red]"
        )
        raise typer.Exit(code=1)

    if plan.planned_count == 0:
        console.print("")
        console.print("[yellow]No files to rename.[/yellow]")
        return

    if not yes:
        console.print("")
        confirmed = typer.confirm("Apply these renames?")
        if not confirmed:
            console.print("[yellow]Apply cancelled.[/yellow]")
            raise typer.Exit(code=1)

    log_dir = Path(".pdf-namefix") / "logs"
    rename_result = apply_rename_plan(plan=plan, log_dir=log_dir)

    console.print("")
    console.print("[bold]Apply result[/bold]")
    console.print(f"- Renamed: {rename_result.renamed_count}")
    console.print(f"- Failed: {rename_result.failed_count}")
    console.print(f"- Log: {rename_result.log_path}")

    if rename_result.failed_count:
        raise typer.Exit(code=1)


@app.command("ai-suggest")
def ai_suggest(
    paths: Annotated[
        list[Path],
        typer.Argument(help="One or more folders containing PDFs."),
    ],
    recursive: Annotated[
        bool,
        typer.Option("--recursive", "-r", help="Scan folders recursively."),
    ] = False,
    inspect_pdf: Annotated[
        bool,
        typer.Option(
            "--inspect-pdf/--no-inspect-pdf",
            help="Read PDF metadata and first-page text.",
        ),
    ] = True,
    profile: Annotated[
        Path | None,
        typer.Option("--profile", help="Optional naming profile YAML file."),
    ] = None,
    model: Annotated[
        str,
        typer.Option("--model", help="OpenAI model to use."),
    ] = "gpt-4.1-mini",
    out: Annotated[
        Path,
        typer.Option("--out", help="Output JSON file for AI suggestions."),
    ] = Path("ai-suggestions.json"),
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Limit number of files sent to AI."),
    ] = None,
    only_unknown: Annotated[
        bool,
        typer.Option(
            "--only-unknown/--all-candidates",
            help="Only send unknown or low-confidence files to AI.",
        ),
    ] = True,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Run without interactive confirmation."),
    ] = False,
) -> None:
    """
    Generate AI-assisted filename suggestions without touching PDF files.
    """
    console.print("[bold]AI Suggest mode[/bold]")
    console.print("This command only writes suggestions. It does not rename files.")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    classified_files = classify_pdf_files(
        result.pdf_files,
        insights_by_path=insights_by_path,
    )
    suggestions = suggest_filenames(classified_files)
    naming_profile = load_naming_profile(profile)

    candidates = []

    for suggestion in suggestions:
        classified = suggestion.classified_pdf_file

        if only_unknown and classified.confidence >= naming_profile.skip_if_confidence_below:
            continue

        candidates.append(suggestion)

    if limit is not None:
        candidates = candidates[:limit]

    console.print(f"PDF files found: [bold]{len(result.pdf_files)}[/bold]")
    console.print(f"PDF inspection: [bold]{inspect_pdf}[/bold]")
    console.print(f"AI candidates: [bold]{len(candidates)}[/bold]")
    console.print(f"Only unknown/low-confidence: [bold]{only_unknown}[/bold]")
    console.print(f"Output: [bold]{out}[/bold]")

    if result.warnings:
        console.print("")
        console.print("[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            console.print(f"- {warning.path}: {warning.reason}")

    if not candidates:
        console.print("[yellow]No AI suggestion candidates found.[/yellow]")
        return

    if not yes:
        console.print("")
        confirmed = typer.confirm("Send these file signals to the AI model?")
        if not confirmed:
            console.print("[yellow]AI suggestion cancelled.[/yellow]")
            raise typer.Exit(code=1)

    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]OPENAI_API_KEY is not set.[/red]")
        console.print("Set it with: export OPENAI_API_KEY='your_api_key_here'")
        raise typer.Exit(code=1)

    client = OpenAiNamingClient()
    ai_results = []

    for index, suggestion in enumerate(candidates, start=1):
        classified = suggestion.classified_pdf_file
        pdf_file = classified.pdf_file
        insights = insights_by_path.get(pdf_file.path)

        naming_input = AiNamingInput(
            source_path=pdf_file.path,
            source_name=pdf_file.path.name,
            current_document_type=classified.document_type,
            current_confidence=classified.confidence,
            current_suggested_name=suggestion.suggested_name,
            metadata_title=insights.metadata_title if insights else None,
            metadata_author=insights.metadata_author if insights else None,
            metadata_subject=insights.metadata_subject if insights else None,
            first_page_text=insights.first_page_text if insights else None,
        )

        ai_suggestion = client.suggest_name(
            naming_input=naming_input,
            profile=naming_profile,
            model=model,
        )

        console.print(
            f"{index}. {pdf_file.path.name} -> [green]{ai_suggestion.suggested_name}[/green] "
            f"[dim]confidence={ai_suggestion.confidence:.2f} "
            f"should_apply={ai_suggestion.should_apply}[/dim]"
        )

        ai_results.append(
            {
                "source_path": str(ai_suggestion.source_path),
                "suggested_name": ai_suggestion.suggested_name,
                "document_type": ai_suggestion.document_type.value,
                "confidence": ai_suggestion.confidence,
                "reason": ai_suggestion.reason,
                "should_apply": ai_suggestion.should_apply,
            }
        )

    payload = {
        "model": model,
        "profile": {
            "language": naming_profile.language,
            "pattern": naming_profile.pattern,
            "max_length": naming_profile.max_length,
            "date_fallback": naming_profile.date_fallback,
            "preserve_author_for_books": naming_profile.preserve_author_for_books,
            "skip_if_confidence_below": naming_profile.skip_if_confidence_below,
        },
        "suggestions": ai_results,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    console.print("")
    console.print("[bold]AI suggestions exported[/bold]")
    console.print(f"- Output: {out}")
    console.print(f"- Suggestions: {len(ai_results)}")


@app.command()
def organize(
    paths: Annotated[
        list[Path],
        typer.Argument(help="One or more folders containing PDFs to organize."),
    ],
    out: Annotated[
        Path,
        typer.Option("--out", help="Output folder for organized PDF files."),
    ],
    recursive: Annotated[
        bool,
        typer.Option("--recursive", "-r", help="Scan folders recursively."),
    ] = False,
    copy: Annotated[
        bool,
        typer.Option("--copy", help="Copy files instead of moving them."),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Organize files without interactive confirmation."),
    ] = False,
    allow_nested_output: Annotated[
        bool,
        typer.Option(
            "--allow-nested-output",
            help="Allow output folder inside an input folder.",
        ),
    ] = False,
    inspect_pdf: Annotated[
        bool,
        typer.Option(
            "--inspect-pdf",
            help="Read PDF metadata and first-page text to improve classification.",
        ),
    ] = False,
) -> None:
    """
    Organize PDF files into type-based folders.
    """
    console.print("[bold]Organize mode[/bold]")
    console.print("Preparing organize plan...")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    classified_files = classify_pdf_files(
        result.pdf_files,
        insights_by_path=insights_by_path,
    )

    if not allow_nested_output:
        path_check = check_output_not_inside_inputs(out_dir=out, input_paths=paths)
        if not path_check.ok:
            console.print(f"[red]{path_check.reason}[/red]")
            raise typer.Exit(code=1)

    plan = build_organize_plan(
        classified_files=classified_files,
        warnings=result.warnings,
        out_dir=out,
        copy=copy,
    )

    if copy:
        disk_check = check_disk_space_for_copy(plan=plan, out_dir=out)

        console.print(
            f"Copy size required: [bold]{format_bytes(disk_check.required_bytes)}[/bold]"
        )
        console.print(
            f"Available disk space: [bold]{format_bytes(disk_check.available_bytes)}[/bold]"
        )

        if not disk_check.ok:
            console.print(
                "[red]Not enough disk space for copy operation. "
                "Use a different output disk/folder or reduce the input set.[/red]"
            )
            raise typer.Exit(code=1)

    mode_label = "copy" if copy else "move"

    console.print(f"PDF files found: [bold]{len(classified_files)}[/bold]")
    console.print(f"Mode: [bold]{mode_label}[/bold]")
    console.print(f"Planned operations: [bold]{plan.planned_count}[/bold]")
    console.print(f"Skipped items: [bold]{plan.skipped_count}[/bold]")
    console.print(f"Warnings: [bold]{len(plan.warnings)}[/bold]")
    console.print("")

    if plan.items:
        for index, item in enumerate(plan.items, start=1):
            if item.skipped:
                console.print(
                    f"{index}. [yellow]SKIP[/yellow] {item.source_path.name} "
                    f"→ {item.target_path} "
                    f"[dim]reason={item.skip_reason}[/dim]"
                )
            else:
                action = "COPY" if copy else "MOVE"
                console.print(
                    f"{index}. [green]{action}[/green] {item.source_path.name} "
                    f"→ {item.target_path}"
                )

    if plan.warnings:
        console.print("")
        console.print("[yellow]Warnings:[/yellow]")
        for warning in plan.warnings:
            console.print(f"- {warning.path}: {warning.reason}")

    if plan.planned_count == 0:
        console.print("")
        console.print("[yellow]No files to organize.[/yellow]")
        return

    if not yes:
        console.print("")
        confirmed = typer.confirm("Apply this organize plan?")
        if not confirmed:
            console.print("[yellow]Organize cancelled.[/yellow]")
            raise typer.Exit(code=1)

    log_dir = Path(".pdf-namefix") / "logs"
    organize_result = apply_organize_plan(plan=plan, log_dir=log_dir)

    console.print("")
    console.print("[bold]Organize result[/bold]")
    console.print(f"- Moved: {organize_result.moved_count}")
    console.print(f"- Copied: {organize_result.copied_count}")
    console.print(f"- Skipped: {organize_result.skipped_count}")
    console.print(f"- Failed: {organize_result.failed_count}")
    console.print(f"- Log: {organize_result.log_path}")

    if organize_result.failed_count:
        raise typer.Exit(code=1)


@app.command()
def undo(
    log: Annotated[
        Path | None,
        typer.Option("--log", help="Specific rename/organize JSONL log to undo."),
    ] = None,
    last: Annotated[
        bool,
        typer.Option("--last", help="Undo the latest rename/organize log."),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Undo without interactive confirmation."),
    ] = False,
) -> None:
    """
    Undo the latest rename/move operation from local logs.

    Copy operations are skipped by default because undoing a copy would delete files.
    """
    console.print("[bold]Undo mode[/bold]")

    log_dir = Path(".pdf-namefix") / "logs"

    if log is None:
        if not last:
            console.print(
                "[yellow]No log provided. Use --last or --log <path>.[/yellow]"
            )
            raise typer.Exit(code=1)

        latest_log = find_latest_log(log_dir)
        if latest_log is None:
            console.print("[yellow]No rename/organize logs found.[/yellow]")
            raise typer.Exit(code=1)

        log = latest_log

    if not log.exists():
        console.print(f"[red]Log file does not exist: {log}[/red]")
        raise typer.Exit(code=1)

    plan = build_undo_plan(log)

    console.print(f"Log: {plan.log_path}")
    console.print(f"Planned undo operations: [bold]{plan.planned_count}[/bold]")
    console.print(f"Skipped items: [bold]{plan.skipped_count}[/bold]")
    console.print("")

    for index, item in enumerate(plan.items, start=1):
        if item.skipped:
            console.print(
                f"{index}. [yellow]SKIP[/yellow] {item.target_path} "
                f"→ {item.source_path} "
                f"[dim]reason={item.skip_reason}[/dim]"
            )
        else:
            console.print(
                f"{index}. [green]UNDO[/green] {item.target_path} "
                f"→ {item.source_path}"
            )

    if plan.planned_count == 0:
        console.print("")
        console.print("[yellow]No undo operations to apply.[/yellow]")
        return

    if not yes:
        console.print("")
        confirmed = typer.confirm("Apply this undo plan?")
        if not confirmed:
            console.print("[yellow]Undo cancelled.[/yellow]")
            raise typer.Exit(code=1)

    result = apply_undo_plan(plan)

    console.print("")
    console.print("[bold]Undo result[/bold]")
    console.print(f"- Undone: {result.undone_count}")
    console.print(f"- Skipped: {result.skipped_count}")
    console.print(f"- Failed: {result.failed_count}")

    if result.failed_count:
        raise typer.Exit(code=1)
