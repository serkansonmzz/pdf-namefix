from pathlib import Path

import typer
from rich.console import Console

from pdf_namefix.undo import apply_undo_plan, build_undo_plan, find_latest_log


def run_undo(
    *,
    console: Console,
    log: Path | None = None,
    last: bool = False,
    yes: bool = False,
) -> None:
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
                f"-> {item.source_path} "
                f"[dim]reason={item.skip_reason}[/dim]"
            )
        else:
            console.print(
                f"{index}. [green]UNDO[/green] {item.target_path} "
                f"-> {item.source_path}"
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
