from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from pdf_namefix import __version__
from pdf_namefix.apply_rename import apply_rename_plan, build_rename_plan
from pdf_namefix.classifier import classify_pdf_files
from pdf_namefix.name_suggester import suggest_filenames
from pdf_namefix.preview_report import build_preview_report
from pdf_namefix.scanner import scan_pdf_files


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

            collision_label = " [red][COLLISION][/red]" if suggestion.has_collision else ""

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

    if report.summary.collision_count:
        console.print("")
        console.print(
            "[red]Apply blocked because suggested filename collisions were found.[/red]"
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
) -> None:
    """
    Organize PDF files into type-based folders.

    This is only a skeleton in Phase 1.
    """
    console.print("[yellow]Organize mode is not implemented yet.[/yellow]")
    console.print("Phase 1 only defines the CLI shape.")

    for path in paths:
        console.print(f"- organize target: {path}")

    console.print(f"Output folder: {out}")

    if recursive:
        console.print("Recursive scan: enabled")

    if copy:
        console.print("Mode: copy")
    else:
        console.print("Mode: move")