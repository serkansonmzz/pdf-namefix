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
