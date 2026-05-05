from pathlib import Path

import typer
from rich.console import Console

from pdf_namefix.apply_ai_suggestions import (
    apply_ai_suggestions_to_filename_suggestions,
    load_ai_suggestion_map,
)
from pdf_namefix.apply_rename import apply_rename_plan, build_rename_plan
from pdf_namefix.classifier import classify_pdf_files
from pdf_namefix.name_suggester import suggest_filenames
from pdf_namefix.naming_profile import load_naming_profile
from pdf_namefix.pdf_inspector import inspect_pdf_files
from pdf_namefix.preview_report import build_preview_report
from pdf_namefix.scanner import scan_pdf_files


def run_apply(
    *,
    console: Console,
    paths: list[Path],
    recursive: bool = False,
    yes: bool = False,
    include_unknown: bool = False,
    min_confidence: float = 0.7,
    profile: Path | None = None,
    inspect_pdf: bool = False,
    ai_suggestions: Path | None = None,
    ai_min_confidence: float | None = None,
) -> None:
    console.print("[bold]Apply mode[/bold]")
    console.print("Preparing safe rename plan...")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    classified_files = classify_pdf_files(
        result.pdf_files,
        insights_by_path=insights_by_path,
    )
    naming_profile = load_naming_profile(profile)
    suggestions = suggest_filenames(classified_files, profile=naming_profile)
    effective_ai_min_confidence = (
        ai_min_confidence
        if ai_min_confidence is not None
        else naming_profile.skip_if_confidence_below
    )

    if ai_suggestions is not None:
        ai_map = load_ai_suggestion_map(ai_suggestions)
        suggestions = apply_ai_suggestions_to_filename_suggestions(
            suggestions=suggestions,
            ai_map=ai_map,
            min_confidence=effective_ai_min_confidence,
        )

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
    if ai_suggestions:
        threshold_source = "CLI" if ai_min_confidence is not None else "profile"
        console.print(f"AI suggestions: [bold]{ai_suggestions}[/bold]")
        console.print(
            f"AI min confidence: [bold]{effective_ai_min_confidence}[/bold] "
            f"[dim]({threshold_source})[/dim]"
        )
    console.print(f"Planned renames: [bold]{plan.planned_count}[/bold]")
    console.print(f"Skipped items: [bold]{plan.skipped_count}[/bold]")
    console.print(f"Warnings: [bold]{len(plan.warnings)}[/bold]")
    console.print("")

    if plan.items:
        for index, item in enumerate(plan.items, start=1):
            if item.skipped:
                console.print(
                    f"{index}. [yellow]SKIP[/yellow] {item.source_path.name} "
                    f"-> {item.suggested_name} "
                    f"[dim]reason={item.skip_reason}[/dim]"
                )
            else:
                console.print(
                    f"{index}. [green]RENAME[/green] {item.source_path.name} "
                    f"-> {item.suggested_name}"
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
