from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PdfFile:
    path: Path
    source_root: Path
    size_bytes: int

    @property
    def name(self) -> str:
        return self.path.name


@dataclass(frozen=True)
class ScanWarning:
    path: Path
    reason: str


@dataclass(frozen=True)
class ScanResult:
    pdf_files: list[PdfFile]
    warnings: list[ScanWarning]

    @property
    def count(self) -> int:
        return len(self.pdf_files)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)
