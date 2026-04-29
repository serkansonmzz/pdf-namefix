from pathlib import Path

from pdf_namefix.models import PdfFile, ScanResult, ScanWarning


def is_pdf_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() == ".pdf"


def iter_candidate_files(root: Path, recursive: bool) -> list[Path]:
    if recursive:
        return [path for path in root.rglob("*") if path.is_file()]

    return [path for path in root.iterdir() if path.is_file()]


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
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    pdf_files.append(
                        PdfFile(
                            path=path,
                            source_root=path.parent,
                            size_bytes=path.stat().st_size,
                        )
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

        for candidate in candidates:
            try:
                if not is_pdf_file(candidate):
                    continue

                resolved = candidate.resolve()
                if resolved in seen:
                    continue

                seen.add(resolved)
                pdf_files.append(
                    PdfFile(
                        path=candidate,
                        source_root=path,
                        size_bytes=candidate.stat().st_size,
                    )
                )
            except PermissionError:
                warnings.append(ScanWarning(path=candidate, reason="Permission denied."))
            except OSError as exc:
                warnings.append(ScanWarning(path=candidate, reason=str(exc)))

    return ScanResult(pdf_files=pdf_files, warnings=warnings)
