from dataclasses import dataclass
from pathlib import Path

from pdf_namefix.domain.models import DocumentType


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
