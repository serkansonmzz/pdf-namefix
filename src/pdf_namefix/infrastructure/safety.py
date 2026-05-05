import shutil
from dataclasses import dataclass
from pathlib import Path

from pdf_namefix.domain.models import OrganizePlan


@dataclass(frozen=True)
class DiskSpaceCheck:
    required_bytes: int
    available_bytes: int
    ok: bool


@dataclass(frozen=True)
class PathSafetyCheck:
    ok: bool
    reason: str | None = None


def is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def check_output_not_inside_inputs(
    out_dir: Path,
    input_paths: list[Path],
) -> PathSafetyCheck:
    expanded_out = out_dir.expanduser()

    for input_path in input_paths:
        expanded_input = input_path.expanduser()

        if expanded_input.exists() and expanded_input.is_dir():
            if is_relative_to(expanded_out, expanded_input):
                return PathSafetyCheck(
                    ok=False,
                    reason=(
                        "Output folder is inside an input folder. "
                        "Choose an output folder outside the scanned folder "
                        "or use --allow-nested-output if intentional."
                    ),
                )

    return PathSafetyCheck(ok=True)


def calculate_copy_required_bytes(plan: OrganizePlan) -> int:
    total = 0

    for item in plan.items:
        if item.skipped:
            continue

        if item.mode != "copy":
            continue

        try:
            total += item.source_path.stat().st_size
        except OSError:
            continue

    return total


def check_disk_space_for_copy(plan: OrganizePlan, out_dir: Path) -> DiskSpaceCheck:
    required = calculate_copy_required_bytes(plan)
    usage = shutil.disk_usage(out_dir.expanduser().parent if not out_dir.exists() else out_dir)

    available = usage.free

    return DiskSpaceCheck(
        required_bytes=required,
        available_bytes=available,
        ok=required <= available,
    )


def format_bytes(size: int) -> str:
    value = float(size)

    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if value < 1024:
            return f"{value:.1f} {unit}"
        value /= 1024

    return f"{value:.1f} PB"
