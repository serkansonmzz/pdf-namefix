from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class DocumentType(StrEnum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CONTRACT = "contract"
    REPORT = "report"
    STATEMENT = "statement"
    TAX = "tax"
    OFFER = "offer"
    APPLICATION = "application"

    BOOK = "book"
    EBOOK = "ebook"
    COURSE = "course"
    LESSON = "lesson"
    NOTES = "notes"
    PAPER = "paper"
    ARTICLE = "article"
    SLIDES = "slides"
    MANUAL = "manual"
    TRANSCRIPT = "transcript"
    WORKSHEET = "worksheet"
    GUIDE = "guide"
    CHEATSHEET = "cheatsheet"

    DOCUMENT = "document"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class PdfFile:
    path: Path
    source_root: Path
    size_bytes: int

    @property
    def name(self) -> str:
        return self.path.name


@dataclass(frozen=True)
class ClassifiedPdfFile:
    pdf_file: PdfFile
    document_type: DocumentType
    confidence: float
    reason: str


@dataclass(frozen=True)
class FilenameSuggestion:
    classified_pdf_file: ClassifiedPdfFile
    suggested_name: str
    reason: str
    has_collision: bool = False
    collision_group: str | None = None


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


@dataclass(frozen=True)
class RenamePlanItem:
    source_path: Path
    target_path: Path
    original_name: str
    suggested_name: str
    document_type: DocumentType
    skipped: bool = False
    skip_reason: str | None = None


@dataclass(frozen=True)
class RenamePlan:
    items: list[RenamePlanItem]
    warnings: list[ScanWarning]

    @property
    def planned_count(self) -> int:
        return sum(1 for item in self.items if not item.skipped)

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.items if item.skipped)

    @property
    def has_skipped_items(self) -> bool:
        return self.skipped_count > 0


@dataclass(frozen=True)
class RenameResultItem:
    source_path: Path
    target_path: Path
    status: str
    error: str | None = None


@dataclass(frozen=True)
class RenameResult:
    items: list[RenameResultItem]
    log_path: Path | None = None

    @property
    def renamed_count(self) -> int:
        return sum(1 for item in self.items if item.status == "renamed")

    @property
    def failed_count(self) -> int:
        return sum(1 for item in self.items if item.status == "failed")
