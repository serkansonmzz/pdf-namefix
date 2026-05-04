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

    EXAM = "exam"
    STUDENT_DOCUMENT = "student_document"
    CV = "cv"
    VISA = "visa"
    MEDICAL = "medical"
    FINANCE = "finance"
    PAYMENT = "payment"
    LANGUAGE_LEARNING = "language_learning"
    REFERENCE = "reference"
    NOVEL = "novel"
    WHITEPAPER = "whitepaper"
    STUDY_MATERIAL = "study_material"

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
class PdfInsights:
    path: Path
    page_count: int | None = None
    metadata_title: str | None = None
    metadata_author: str | None = None
    metadata_subject: str | None = None
    metadata_creator: str | None = None
    metadata_producer: str | None = None
    metadata_creation_date: str | None = None
    first_page_text: str | None = None
    extraction_error: str | None = None

    @property
    def has_text(self) -> bool:
        return bool(self.first_page_text and self.first_page_text.strip())

    @property
    def searchable_text(self) -> str:
        parts = [
            self.metadata_title,
            self.metadata_author,
            self.metadata_subject,
            self.metadata_creator,
            self.metadata_producer,
            self.first_page_text,
        ]

        return " ".join(part for part in parts if part).strip()


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
    collision_resolved: bool = False
    original_suggested_name: str | None = None


@dataclass(frozen=True)
class AiNamingInput:
    source_path: Path
    source_name: str
    current_document_type: DocumentType
    current_confidence: float
    current_suggested_name: str
    metadata_title: str | None = None
    metadata_author: str | None = None
    metadata_subject: str | None = None
    first_page_text: str | None = None


@dataclass(frozen=True)
class AiNamingSuggestion:
    source_path: Path
    source_name: str
    current_suggested_name: str
    current_document_type: DocumentType
    current_confidence: float
    ai_suggested_name: str
    ai_document_type: DocumentType
    semantic_type: str
    confidence: float
    reason: str
    improvement: str
    should_apply: bool


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


@dataclass(frozen=True)
class OrganizePlanItem:
    source_path: Path
    target_path: Path
    document_type: DocumentType
    mode: str
    skipped: bool = False
    skip_reason: str | None = None


@dataclass(frozen=True)
class OrganizePlan:
    items: list[OrganizePlanItem]
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
class OrganizeResultItem:
    source_path: Path
    target_path: Path
    status: str
    mode: str
    error: str | None = None


@dataclass(frozen=True)
class OrganizeResult:
    items: list[OrganizeResultItem]
    log_path: Path | None = None

    @property
    def moved_count(self) -> int:
        return sum(1 for item in self.items if item.status == "moved")

    @property
    def copied_count(self) -> int:
        return sum(1 for item in self.items if item.status == "copied")

    @property
    def skipped_count(self) -> int:
        return sum(1 for item in self.items if item.status == "skipped")

    @property
    def failed_count(self) -> int:
        return sum(1 for item in self.items if item.status == "failed")
