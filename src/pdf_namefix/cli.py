from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from pdf_namefix import __version__
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
) -> None:
    """
    Preview discovered PDF files without touching files.
    """
    console.print("[bold]Preview mode[/bold]")
    console.print("No files will be renamed in this command.")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)

    console.print(f"PDF files found: [bold]{result.count}[/bold]")

    if result.pdf_files:
        console.print("")
        for index, pdf_file in enumerate(result.pdf_files, start=1):
            size_kb = pdf_file.size_bytes / 1024
            console.print(
                f"{index}. {pdf_file.path} "
                f"[dim]({size_kb:.1f} KB)[/dim]"
            )

    if result.warnings:
        console.print("")
        console.print("[yellow]Warnings:[/yellow]")
        for warning in result.warnings:
            console.print(f"- {warning.path}: {warning.reason}")


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
    Apply safe PDF filename changes after previewing suggestions.

    This is only a skeleton in Phase 1.
    """
    console.print("[yellow]Apply mode is not implemented yet.[/yellow]")
    console.print("Phase 1 only defines the CLI shape.")

    for path in paths:
        console.print(f"- apply target: {path}")

    if recursive:
        console.print("Recursive scan: enabled")

    if yes:
        console.print("Auto-confirm: enabled")


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