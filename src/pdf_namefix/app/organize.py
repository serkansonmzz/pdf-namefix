from pathlib import Path

import typer
from rich.console import Console

from pdf_namefix.services.classifier import classify_pdf_files
from pdf_namefix.naming_profile import load_naming_profile
from pdf_namefix.organizer import apply_organize_plan, build_organize_plan
from pdf_namefix.services.pdf_inspector import inspect_pdf_files
from pdf_namefix.infrastructure.safety import (
    check_disk_space_for_copy,
    check_output_not_inside_inputs,
    format_bytes,
)
from pdf_namefix.services.scanner import scan_pdf_files


def run_organize(
    *,
    console: Console,
    paths: list[Path],
    out: Path,
    recursive: bool = False,
    copy: bool = False,
    yes: bool = False,
    allow_nested_output: bool = False,
    profile: Path | None = None,
    inspect_pdf: bool = False,
) -> None:
    console.print("[bold]Organize mode[/bold]")
    console.print("Preparing organize plan...")
    console.print("")

    result = scan_pdf_files(paths=paths, recursive=recursive)
    insights_by_path = inspect_pdf_files(result.pdf_files) if inspect_pdf else {}

    naming_profile = load_naming_profile(profile)

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
        folders=naming_profile.folders,
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
                    f"-> {item.target_path} "
                    f"[dim]reason={item.skip_reason}[/dim]"
                )
            else:
                action = "COPY" if copy else "MOVE"
                console.print(
                    f"{index}. [green]{action}[/green] {item.source_path.name} "
                    f"-> {item.target_path}"
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
