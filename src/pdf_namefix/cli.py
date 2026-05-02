from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from pdf_namefix import __version__
from pdf_namefix.apply_rename import apply_rename_plan, build_rename_plan
from pdf_namefix.classifier import classify_pdf_files
from pdf_namefix.name_suggester import suggest_filenames
from pdf_namefix.organizer import apply_organize_plan, build_organize_plan
from pdf_namefix.preview_report import build_preview_report
from pdf_namefix.scanner import scan_pdf_files
from pdf_namefix.undo import apply_undo_plan, build_undo_plan, find_latest_log


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
) -> None:
    """
    Preview discovered PDF files and suggested filenames without touching files.
    """
    console.print("[bold]Preview mode[/bold]")
    console.print("No files will be renamed in this command.")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    classified_files = classify_pdf_files(result.pdf_files)
    suggestions = suggest_filenames(classified_files)
    report = build_preview_report(suggestions=suggestions, warnings=result.warnings)

    console.print(f"PDF files found: [bold]{report.summary.total_files}[/bold]")

    if report.suggestions:
        console.print("")
        for index, suggestion in enumerate(report.suggestions, start=1):
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

    if report.warnings:
        console.print("")
        console.print("[yellow]Warnings:[/yellow]")
        for warning in report.warnings:
            console.print(f"- {warning.path}: {warning.reason}")

    console.print("")
    console.print("[bold]Summary[/bold]")
    console.print(f"- Total PDF files: {report.summary.total_files}")
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
) -> None:
    """
    Apply safe PDF filename changes.

    This command renames files only after safety checks.
    """
    console.print("[bold]Apply mode[/bold]")
    console.print("Preparing safe rename plan...")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    classified_files = classify_pdf_files(result.pdf_files)
    suggestions = suggest_filenames(classified_files)
    report = build_preview_report(suggestions=suggestions, warnings=result.warnings)
    plan = build_rename_plan(suggestions=report.suggestions, warnings=report.warnings)

    console.print(f"PDF files found: [bold]{report.summary.total_files}[/bold]")
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
) -> None:
    """
    Organize PDF files into type-based folders.
    """
    console.print("[bold]Organize mode[/bold]")
    console.print("Preparing organize plan...")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    classified_files = classify_pdf_files(result.pdf_files)
    plan = build_organize_plan(
        classified_files=classified_files,
        warnings=result.warnings,
        out_dir=out,
        copy=copy,
    )

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