import os
from pathlib import Path

import typer
from rich.console import Console

from pdf_namefix.ai_naming import OpenAiNamingClient, select_ai_candidates
from pdf_namefix.infrastructure.ai_report_exporter import write_ai_report
from pdf_namefix.classifier import classify_pdf_files
from pdf_namefix.models import AiNamingInput, AiNamingSuggestion
from pdf_namefix.name_suggester import suggest_filenames
from pdf_namefix.naming_profile import load_naming_profile
from pdf_namefix.pdf_inspector import inspect_pdf_files
from pdf_namefix.scanner import scan_pdf_files


def run_ai_suggest(
    *,
    console: Console,
    paths: list[Path],
    recursive: bool = False,
    inspect_pdf: bool = True,
    profile: Path | None = None,
    model: str = "gpt-4.1-mini",
    out: Path = Path("ai-suggestions.json"),
    output_format: str = "json",
    overwrite_report: bool = False,
    limit: int | None = None,
    unknown_only: bool = False,
    low_confidence: bool = False,
    yes: bool = False,
) -> None:
    console.print("[bold]AI Suggest mode[/bold]")
    console.print("This command only writes suggestions. It does not rename files.")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    classified_files = classify_pdf_files(
        result.pdf_files,
        insights_by_path=insights_by_path,
    )
    naming_profile = load_naming_profile(profile)
    suggestions = suggest_filenames(classified_files, profile=naming_profile)

    if not unknown_only and not low_confidence:
        low_confidence = True

    candidates = select_ai_candidates(
        suggestions=suggestions,
        unknown_only=unknown_only,
        low_confidence=low_confidence,
        threshold=naming_profile.skip_if_confidence_below,
    )

    if limit is not None:
        candidates = candidates[:limit]

    console.print(f"PDF files found: [bold]{len(result.pdf_files)}[/bold]")
    console.print(f"PDF inspection: [bold]{inspect_pdf}[/bold]")
    console.print(f"AI candidates: [bold]{len(candidates)}[/bold]")
    console.print(f"Unknown only: [bold]{unknown_only}[/bold]")
    console.print(f"Low confidence: [bold]{low_confidence}[/bold]")
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
    ai_results: list[AiNamingSuggestion] = []

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
            f"{index}. {pdf_file.path.name}"
        )
        console.print(
            f"   current: {suggestion.suggested_name} "
            f"[{classified.document_type.value} confidence={classified.confidence:.2f}]"
        )
        console.print(
            f"   AI:      [green]{ai_suggestion.ai_suggested_name}[/green] "
            f"[{ai_suggestion.ai_document_type.value}/{ai_suggestion.semantic_type} "
            f"confidence={ai_suggestion.confidence:.2f} "
            f"should_apply={ai_suggestion.should_apply}]"
        )
        console.print(
            f"   [dim]improvement: {ai_suggestion.improvement}[/dim]"
        )

        ai_results.append(ai_suggestion)

    try:
        written = write_ai_report(
            suggestions=ai_results,
            model=model,
            out_path=out,
            output_format=output_format,
            overwrite=overwrite_report,
        )
    except FileExistsError as exc:
        console.print(f"[red]{exc}[/red]")
        console.print("Use --overwrite-report to replace it.")
        raise typer.Exit(code=1)

    console.print("")
    console.print("[bold]AI suggestions exported[/bold]")
    console.print(f"- Format: {output_format}")
    console.print(f"- Output: {written}")
    console.print(f"- Suggestions: {len(ai_results)}")
