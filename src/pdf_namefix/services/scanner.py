from pathlib import Path

from pdf_namefix.domain.models import PdfFile, ScanResult, ScanWarning


def is_pdf_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".pdf"


def iter_candidate_files(root: Path, recursive: bool) -> list[Path]:
    if recursive:
        return [path for path in root.rglob("*") if path.is_file()]

    return [path for path in root.iterdir() if path.is_file()]


def add_pdf_file_if_unique(
    pdf_files: list[PdfFile],
    seen: set[Path],
    path: Path,
    source_root: Path,
    warnings: list[ScanWarning],
) -> None:
    try:
        resolved = path.resolve()
    except OSError as exc:
        warnings.append(ScanWarning(path=path, reason=str(exc)))
        return

    if resolved in seen:
        return

    try:
        size_bytes = path.stat().st_size
    except OSError as exc:
        warnings.append(ScanWarning(path=path, reason=str(exc)))
        return

    seen.add(resolved)
    pdf_files.append(
        PdfFile(
            path=path,
            source_root=source_root,
            size_bytes=size_bytes,
        )
    )


def scan_pdf_files(paths: list[Path], recursive: bool = False) -> ScanResult:
    pdf_files: list[PdfFile] = []
    warnings: list[ScanWarning] = []
    seen: set[Path] = set()

    for raw_path in paths:
        path = raw_path.expanduser()

        if not path.exists():
            warnings.append(ScanWarning(path=path, reason="Path does not exist."))
            continue

        if path.is_file():
            if is_pdf_file(path):
                add_pdf_file_if_unique(
                    pdf_files=pdf_files,
                    seen=seen,
                    path=path,
                    source_root=path.parent,
                    warnings=warnings,
                )
            else:
                warnings.append(ScanWarning(path=path, reason="Path is not a PDF file."))
            continue

        if not path.is_dir():
            warnings.append(ScanWarning(path=path, reason="Path is not a directory."))
            continue

        try:
            candidates = iter_candidate_files(path, recursive=recursive)
        except PermissionError:
            warnings.append(ScanWarning(path=path, reason="Permission denied."))
            continue
        except OSError as exc:
            warnings.append(ScanWarning(path=path, reason=str(exc)))
            continue

        for candidate in candidates:
            try:
                if not is_pdf_file(candidate):
                    continue

                add_pdf_file_if_unique(
                    pdf_files=pdf_files,
                    seen=seen,
                    path=candidate,
                    source_root=path,
                    warnings=warnings,
                )
            except PermissionError:
                warnings.append(ScanWarning(path=candidate, reason="Permission denied."))
            except OSError as exc:
                warnings.append(ScanWarning(path=candidate, reason=str(exc)))

    return ScanResult(pdf_files=pdf_files, warnings=warnings)
