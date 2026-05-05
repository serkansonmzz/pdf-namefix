from pathlib import Path
from typing import Annotated

import typer
from dotenv import load_dotenv
from rich.console import Console

from pdf_namefix import __version__
from pdf_namefix.app.ai_suggest import run_ai_suggest
from pdf_namefix.app.apply import run_apply
from pdf_namefix.app.organize import run_organize
from pdf_namefix.app.preview import run_preview
from pdf_namefix.app.undo import run_undo


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
    profile: Annotated[
        Path | None,
        typer.Option("--profile", help="Optional naming profile YAML file."),
    ] = None,
    ai_suggestions: Annotated[
        Path | None,
        typer.Option(
            "--ai-suggestions",
            help="Show reviewed AI suggestions alongside deterministic preview.",
        ),
    ] = None,
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
    run_preview(
        console=console,
        paths=paths,
        recursive=recursive,
        verbose=verbose,
        summary_only=summary_only,
        only=only,
        limit=limit,
        inspect_pdf=inspect_pdf,
        profile=profile,
        ai_suggestions=ai_suggestions,
        output_format=output_format,
        out=out,
        overwrite_report=overwrite_report,
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
    profile: Annotated[
        Path | None,
        typer.Option("--profile", help="Optional naming profile YAML file."),
    ] = None,
    inspect_pdf: Annotated[
        bool,
        typer.Option(
            "--inspect-pdf",
            help="Read PDF metadata and first-page text to improve classification.",
        ),
    ] = False,
    ai_suggestions: Annotated[
        Path | None,
        typer.Option(
            "--ai-suggestions",
            help="Use reviewed AI suggestions JSON as rename input.",
        ),
    ] = None,
    ai_min_confidence: Annotated[
        float | None,
        typer.Option(
            "--ai-min-confidence",
            help="Minimum AI confidence required for applying AI suggestions. Defaults to profile threshold.",
        ),
    ] = None,
) -> None:
    """
    Apply safe PDF filename changes.

    This command renames files only after safety checks.
    """
    run_apply(
        console=console,
        paths=paths,
        recursive=recursive,
        yes=yes,
        include_unknown=include_unknown,
        min_confidence=min_confidence,
        profile=profile,
        inspect_pdf=inspect_pdf,
        ai_suggestions=ai_suggestions,
        ai_min_confidence=ai_min_confidence,
    )


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
        typer.Option("--out", help="Output file for AI suggestions."),
    ] = Path("ai-suggestions.json"),
    output_format: Annotated[
        str,
        typer.Option("--format", help="Output format: json or markdown."),
    ] = "json",
    overwrite_report: Annotated[
        bool,
        typer.Option("--overwrite-report", help="Overwrite existing AI suggestion report."),
    ] = False,
    limit: Annotated[
        int | None,
        typer.Option("--limit", help="Limit number of files sent to AI."),
    ] = None,
    unknown_only: Annotated[
        bool,
        typer.Option(
            "--unknown-only",
            "--only-unknown",
            help="Only send files classified as unknown.",
        ),
    ] = False,
    low_confidence: Annotated[
        bool,
        typer.Option("--low-confidence", help="Only send low-confidence files to AI."),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Run without interactive confirmation."),
    ] = False,
) -> None:
    """
    Generate AI-assisted filename suggestions without touching PDF files.
    """
    run_ai_suggest(
        console=console,
        paths=paths,
        recursive=recursive,
        inspect_pdf=inspect_pdf,
        profile=profile,
        model=model,
        out=out,
        output_format=output_format,
        overwrite_report=overwrite_report,
        limit=limit,
        unknown_only=unknown_only,
        low_confidence=low_confidence,
        yes=yes,
    )


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
    profile: Annotated[
        Path | None,
        typer.Option("--profile", help="Optional naming profile YAML file."),
    ] = None,
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
    run_organize(
        console=console,
        paths=paths,
        out=out,
        recursive=recursive,
        copy=copy,
        yes=yes,
        allow_nested_output=allow_nested_output,
        profile=profile,
        inspect_pdf=inspect_pdf,
    )


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
    run_undo(
        console=console,
        log=log,
        last=last,
        yes=yes,
    )
